from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import os
import shutil
from pathlib import Path

from database import get_db
from models import Submission, Assignment, User, UserRole, Enrollment
from schemas import (
    SubmissionResponse, SubmissionGrade, MessageResponse
)
from dependencies import (
    get_current_user,
    get_current_student,
    get_current_teacher_or_admin,
    verify_student_in_course
)

router = APIRouter(
    prefix="/api/submissions",
    tags=["Submissions"]
)

# Directorio base para archivos
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./maruchan_storage/submissions")
Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)

# Tamaño máximo de archivo (50MB)
MAX_FILE_SIZE = 50 * 1024 * 1024


# ==================== UTILIDADES ====================

def save_upload_file(upload_file: UploadFile, assignment_id: int, student_id: int) -> str:
    """
    Guarda un archivo subido y retorna la ruta relativa.
    
    Estructura: submissions/assignment_{id}/student_{id}/filename.ext
    """
    # Crear directorio si no existe
    assignment_dir = Path(UPLOAD_DIR) / f"assignment_{assignment_id}" / f"student_{student_id}"
    assignment_dir.mkdir(parents=True, exist_ok=True)
    
    # Generar nombre único con timestamp
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    file_extension = Path(upload_file.filename).suffix
    safe_filename = f"{timestamp}_{upload_file.filename}"
    
    file_path = assignment_dir / safe_filename
    
    # Guardar archivo
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)
    
    # Retornar ruta relativa
    return str(file_path.relative_to(UPLOAD_DIR))


def get_full_file_path(relative_path: str) -> Path:
    """Obtiene la ruta completa del archivo"""
    return Path(UPLOAD_DIR) / relative_path


def delete_file(relative_path: str) -> bool:
    """Elimina un archivo del sistema"""
    try:
        full_path = get_full_file_path(relative_path)
        if full_path.exists():
            full_path.unlink()
            return True
        return False
    except Exception as e:
        print(f"Error eliminando archivo: {e}")
        return False


# ==================== GET ENDPOINTS ====================

@router.get("/", response_model=List[SubmissionResponse])
async def get_submissions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    assignment_id: Optional[int] = None,
    student_id: Optional[int] = None,
    late_only: Optional[bool] = None,
    graded_only: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lista entregas con filtros opcionales.
    
    Permisos:
    - Estudiantes: solo sus propias entregas
    - Profesores: entregas de sus cursos
    - Admins: todas las entregas
    """
    query = db.query(Submission)
    
    # Filtrar según rol
    if current_user.role == UserRole.STUDENT:
        query = query.filter(Submission.student_id == current_user.id)
    
    elif current_user.role == UserRole.TEACHER:
        # Solo entregas de asignaciones de sus cursos
        teacher_courses = [c.id for c in current_user.courses_taught]
        query = query.join(Assignment).filter(Assignment.course_id.in_(teacher_courses))
    
    # Filtros adicionales
    if assignment_id:
        query = query.filter(Submission.assignment_id == assignment_id)
    
    if student_id:
        if current_user.role == UserRole.STUDENT and student_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No puedes ver entregas de otros estudiantes"
            )
        query = query.filter(Submission.student_id == student_id)
    
    if late_only is not None:
        query = query.filter(Submission.late == late_only)
    
    if graded_only is not None:
        if graded_only:
            query = query.filter(Submission.grade.isnot(None))
        else:
            query = query.filter(Submission.grade.is_(None))
    
    submissions = query.offset(skip).limit(limit).all()
    
    # Formatear respuesta
    from schemas import UserList, AssignmentList
    
    result = []
    for submission in submissions:
        student_data = UserList(
            id=submission.student.id,
            full_name=submission.student.full_name,
            email=submission.student.email,
            role=submission.student.role,
            carnet=submission.student,
            is_active=submission.student.is_active
        )
        
        assignment_data = AssignmentList(
            id=submission.assignment.id,
            title=submission.assignment.title,
            course_code=submission.assignment.course.code,
            due_date=submission.assignment.due_date,
            max_score=submission.assignment.max_score,
            is_overdue=submission.assignment.is_overdue,
            is_published=submission.assignment.is_published
        )
        
        graded_by_name = None
        if submission.graded_by:
            graded_by_name = submission.graded_by.full_name
        
        result.append(SubmissionResponse(
            id=submission.id,
            assignment_id=submission.assignment_id,
            assignment=assignment_data,
            student_id=submission.student_id,
            student=student_data,
            file_path=submission.file_path,
            submitted_at_date=submission.submitted_at_date,
            late=submission.late,
            grade=submission.grade,
            feedback_char=submission.feedback_char,
            graded_at=submission.graded_at,
            graded_by_name=graded_by_name
        ))
    
    return result


@router.get("/my-submissions", response_model=List[SubmissionResponse])
async def get_my_submissions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student)
):
    """Obtiene las entregas del estudiante actual"""
    return await get_submissions(
        skip=0,
        limit=100,
        student_id=current_user.id,
        db=db,
        current_user=current_user
    )


@router.get("/{submission_id}", response_model=SubmissionResponse)
async def get_submission_by_id(
    submission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtiene una entrega por ID"""
    submission = db.query(Submission).filter(Submission.id == submission_id).first()
    
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entrega no encontrada"
        )
    
    # Verificar permisos
    if current_user.role == UserRole.STUDENT:
        if submission.student_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para ver esta entrega"
            )
    
    elif current_user.role == UserRole.TEACHER:
        if submission.assignment.course.teacher_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para ver esta entrega"
            )
    
    # Formatear respuesta
    from schemas import UserList, AssignmentList
    
    student_data = UserList(
        id=submission.student.id,
        full_name=submission.student.full_name,
        email=submission.student.email,
        role=submission.student.role,
        carnet=submission.student.carnet
    )
    
    assignment_data = AssignmentList(
        id=submission.assignment.id,
        title=submission.assignment.title,
        course_code=submission.assignment.course.code,
        due_date=submission.assignment.due_date,
        max_score=submission.assignment.max_score,
        is_overdue=submission.assignment.is_overdue,
        is_published=submission.assignment.is_published
    )
    
    graded_by_name = None
    if submission.graded_by:
        graded_by_name = submission.graded_by.full_name
    
    return SubmissionResponse(
        id=submission.id,
        assignment_id=submission.assignment_id,
        assignment=assignment_data,
        student_id=submission.student_id,
        student=student_data,
        file_path=submission.file_path,
        submitted_at_date=submission.submitted_at_date,
        late=submission.late,
        grade=submission.grade,
        feedback_char=submission.feedback_char,
        graded_at=submission.graded_at,
        graded_by_name=graded_by_name
    )


# ==================== POST ENDPOINTS (UPLOAD) ====================

@router.post("/upload", response_model=SubmissionResponse, status_code=status.HTTP_201_CREATED)
async def upload_submission(
    assignment_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student)
):
    """
    Sube una entrega de tarea.
    
    Solo estudiantes pueden subir sus propias entregas.
    """
    # Verificar que la asignación existe
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asignación no encontrada"
        )
    
    # Verificar que la asignación esté publicada
    if not assignment.is_published:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La asignación no está publicada"
        )
    
    # Verificar que el estudiante esté inscrito en el curso
    if not verify_student_in_course(current_user.id, assignment.course_id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No estás inscrito en este curso"
        )
    
    # Verificar si ya existe una entrega
    existing = db.query(Submission).filter(
        Submission.assignment_id == assignment_id,
        Submission.student_id == current_user.id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya has entregado esta tarea. Use PUT para actualizar."
        )
    
    # Verificar tamaño del archivo
    file.file.seek(0, 2)  # Ir al final del archivo
    file_size = file.file.tell()  # Obtener posición (tamaño)
    file.file.seek(0)  # Volver al inicio
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"El archivo es muy grande. Máximo {MAX_FILE_SIZE / 1024 / 1024}MB"
        )
    
    # Guardar archivo
    try:
        file_path = save_upload_file(file, assignment_id, current_user.id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error guardando el archivo: {str(e)}"
        )
    
    # Determinar si es tarde
    is_late = datetime.utcnow() > assignment.due_date
    
    # Crear entrega
    new_submission = Submission(
        assignment_id=assignment_id,
        student_id=current_user.id,
        file_path=file_path,
        late=is_late
    )
    
    db.add(new_submission)
    db.commit()
    db.refresh(new_submission)
    
    return await get_submission_by_id(new_submission.id, db, current_user)


# ==================== PUT ENDPOINTS (RE-UPLOAD) ====================

@router.put("/{submission_id}/reupload", response_model=SubmissionResponse)
async def reupload_submission(
    submission_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student)
):
    """
    Re-sube/actualiza el archivo de una entrega.
    
    Solo el estudiante que hizo la entrega puede actualizarla.
    """
    submission = db.query(Submission).filter(Submission.id == submission_id).first()
    
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entrega no encontrada"
        )
    
    # Verificar que sea el dueño de la entrega
    if submission.student_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo puedes actualizar tus propias entregas"
        )
    
    # Verificar que no esté calificada
    if submission.grade is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes actualizar una entrega ya calificada"
        )
    
    # Verificar tamaño del archivo
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"El archivo es muy grande. Máximo {MAX_FILE_SIZE / 1024 / 1024}MB"
        )
    
    # Eliminar archivo anterior
    delete_file(submission.file_path)
    
    # Guardar nuevo archivo
    try:
        new_file_path = save_upload_file(
            file,
            submission.assignment_id,
            current_user.id
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error guardando el archivo: {str(e)}"
        )
    
    # Actualizar entrega
    submission.file_path = new_file_path
    submission.submitted_at_date = datetime.utcnow()
    submission.late = datetime.utcnow() > submission.assignment.due_date
    
    db.commit()
    db.refresh(submission)
    
    return await get_submission_by_id(submission_id, db, current_user)


# ==================== DOWNLOAD ENDPOINT ====================

@router.get("/{submission_id}/download")
async def download_submission_file(
    submission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Descarga el archivo de una entrega.
    
    Permisos:
    - Estudiante: solo su propia entrega
    - Profesor: entregas de sus cursos
    - Admin: cualquier entrega
    """
    submission = db.query(Submission).filter(Submission.id == submission_id).first()
    
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entrega no encontrada"
        )
    
    # Verificar permisos
    if current_user.role == UserRole.STUDENT:
        if submission.student_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para descargar esta entrega"
            )
    
    elif current_user.role == UserRole.TEACHER:
        if submission.assignment.course.teacher_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para descargar esta entrega"
            )
    
    # Obtener archivo
    file_path = get_full_file_path(submission.file_path)
    
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Archivo no encontrado en el servidor"
        )
    
    # Retornar archivo
    return FileResponse(
        path=file_path,
        filename=file_path.name,
        media_type="application/octet-stream"
    )


# ==================== GRADING ENDPOINTS ====================

@router.patch("/{submission_id}/grade", response_model=SubmissionResponse)
async def grade_submission(
    submission_id: int,
    grade_data: SubmissionGrade,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_teacher_or_admin)
):
    """
    Califica una entrega.
    
    Solo profesores del curso o administradores.
    """
    submission = db.query(Submission).filter(Submission.id == submission_id).first()
    
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entrega no encontrada"
        )
    
    # Verificar permisos
    if current_user.role == UserRole.TEACHER:
        if submission.assignment.course.teacher_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo el profesor del curso puede calificar"
            )
    
    # Verificar que la calificación no exceda el máximo
    if grade_data.grade > submission.assignment.max_score:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"La calificación no puede exceder {submission.assignment.max_score}"
        )
    
    # Actualizar calificación
    submission.grade = grade_data.grade
    submission.feedback_char = grade_data.feedback_char
    submission.graded_by_id = grade_data.graded_by_id
    submission.graded_at = datetime.utcnow()
    
    db.commit()
    db.refresh(submission)
    
    return await get_submission_by_id(submission_id, db, current_user)


# ==================== DELETE ENDPOINTS ====================

@router.delete("/{submission_id}", response_model=MessageResponse)
async def delete_submission(
    submission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Elimina una entrega.
    
    Permisos:
    - Estudiantes: solo sus propias entregas NO calificadas
    - Admins: cualquier entrega
    """
    submission = db.query(Submission).filter(Submission.id == submission_id).first()
    
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entrega no encontrada"
        )
    
    # Verificar permisos
    if current_user.role == UserRole.STUDENT:
        if submission.student_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo puedes eliminar tus propias entregas"
            )
        
        if submission.grade is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No puedes eliminar una entrega ya calificada"
            )
    
    elif current_user.role == UserRole.TEACHER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Los profesores no pueden eliminar entregas"
        )
    
    # Eliminar archivo del sistema
    delete_file(submission.file_path)
    
    # Eliminar de la base de datos
    db.delete(submission)
    db.commit()
    
    return MessageResponse(
        message="Entrega eliminada exitosamente",
        success=True
    )