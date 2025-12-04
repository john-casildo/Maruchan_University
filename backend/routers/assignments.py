from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from database import get_db
from models import Assignment, Course, User, UserRole, Enrollment
from schemas import (
    AssignmentCreate, AssignmentUpdate, AssignmentResponse,
    AssignmentList, MessageResponse
)
from dependencies import (
    get_current_user,
    get_current_teacher_or_admin,
    verify_course_access
)

router = APIRouter(
    prefix="/api/assignments",
    tags=["Assignments"]
)


# ==================== GET ENDPOINTS ====================

@router.get("/", response_model=List[AssignmentList])
async def get_assignments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    course_id: Optional[int] = None,
    is_published: Optional[bool] = None,
    is_overdue: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lista asignaciones con filtros opcionales.
    
    Filtros:
    - course_id: Filtrar por curso
    - is_published: Solo asignaciones publicadas
    - is_overdue: Solo asignaciones vencidas
    """
    query = db.query(Assignment)
    
    # Filtrar por curso si se especifica
    if course_id:
        # Verificar acceso al curso
        if not verify_course_access(current_user, course_id, db):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes acceso a este curso"
            )
        query = query.filter(Assignment.course_id == course_id)
    else:
        # Si no se especifica curso, mostrar solo de cursos accesibles
        if current_user.role == UserRole.STUDENT:
            # Cursos donde está inscrito
            enrolled_courses = db.query(Enrollment.course_id).filter(
                Enrollment.student_id == current_user.id,
                Enrollment.status == "enrolled"
            ).all()
            course_ids = [c[0] for c in enrolled_courses]
            query = query.filter(Assignment.course_id.in_(course_ids))
        
        elif current_user.role == UserRole.TEACHER:
            # Cursos que imparte
            teacher_courses = [c.id for c in current_user.courses_taught]
            query = query.filter(Assignment.course_id.in_(teacher_courses))
    
    # Filtros adicionales
    if is_published is not None:
        query = query.filter(Assignment.is_published == is_published)
    
    assignments = query.offset(skip).limit(limit).all()
    
    # Filtrar por vencidas si se solicita
    if is_overdue is not None:
        now = datetime.utcnow()
        if is_overdue:
            assignments = [a for a in assignments if a.due_date < now]
        else:
            assignments = [a for a in assignments if a.due_date >= now]
    
    # Formatear respuesta
    result = []
    for assignment in assignments:
        result.append(AssignmentList(
            id=assignment.id,
            title=assignment.title,
            description=assignment.description,
            course_id=assignment.course_id,
            course_code=assignment.course.code,
            due_date=assignment.due_date,
            max_score=assignment.max_score,
            weight=assignment.weight,
            is_overdue=assignment.is_overdue,
            is_published=assignment.is_published
        ))
    
    return result


@router.get("/my-assignments", response_model=List[AssignmentList])
async def get_my_assignments(
    pending_only: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene las asignaciones del usuario actual.
    
    - Estudiantes: asignaciones de sus cursos
    - Profesores: asignaciones que han creado
    """
    if current_user.role == UserRole.STUDENT:
        # Asignaciones de cursos donde está inscrito
        enrolled_courses = db.query(Enrollment.course_id).filter(
            Enrollment.student_id == current_user.id,
            Enrollment.status == "enrolled"
        ).all()
        course_ids = [c[0] for c in enrolled_courses]
        
        assignments = db.query(Assignment).filter(
            Assignment.course_id.in_(course_ids),
            Assignment.is_published == True
        ).all()
        
        # Si solo pendientes, filtrar las que no ha entregado
        if pending_only:
            from models import Submission
            submitted_ids = db.query(Submission.assignment_id).filter(
                Submission.student_id == current_user.id
            ).all()
            submitted_ids = [s[0] for s in submitted_ids]
            assignments = [a for a in assignments if a.id not in submitted_ids]
    
    elif current_user.role == UserRole.TEACHER:
        # Asignaciones de cursos que imparte
        teacher_courses = [c.id for c in current_user.courses_taught]
        assignments = db.query(Assignment).filter(
            Assignment.course_id.in_(teacher_courses)
        ).all()
    
    else:  # ADMIN
        assignments = db.query(Assignment).all()
    
    # Formatear respuesta
    result = []
    for assignment in assignments:
        result.append(AssignmentList(
            id=assignment.id,
            title=assignment.title,
            description=assignment.description,
            course_id=assignment.course_id,
            course_code=assignment.course.code,
            due_date=assignment.due_date,
            max_score=assignment.max_score,
            weight=assignment.weight,
            is_overdue=assignment.is_overdue,
            is_published=assignment.is_published
        ))
    
    return result


@router.get("/{assignment_id}", response_model=AssignmentResponse)
async def get_assignment_by_id(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtiene una asignación por ID"""
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asignación no encontrada"
        )
    
    # Verificar acceso
    if not verify_course_access(current_user, assignment.course_id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes acceso a esta asignación"
        )
    
    # Estudiantes solo ven asignaciones publicadas
    if current_user.role == UserRole.STUDENT and not assignment.is_published:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asignación no encontrada"
        )
    
    # Formatear respuesta
    from schemas import CourseList
    
    course_data = CourseList(
        id=assignment.course.id,
        code=assignment.course.code,
        title=assignment.course.title,
        teacher_name=assignment.course.teacher.full_name,
        teacher_id=assignment.course.teacher_id,
        semester=assignment.course.semester,
        credits=assignment.course.credits,
        enrolled_count=len([e for e in assignment.course.enrollments if e.status == "enrolled"]),
        status=assignment.course.status
    )
    
    return AssignmentResponse(
        id=assignment.id,
        course_id=assignment.course_id,
        course=course_data,
        title=assignment.title,
        description=assignment.description,
        due_date=assignment.due_date,
        attachment_path=assignment.attachment_path,
        max_score=assignment.max_score,
        weight=assignment.weight,
        is_published=assignment.is_published,
        is_overdue=assignment.is_overdue,
        submissions_count=len(assignment.submissions),
        created_at=assignment.created_at,
        updated_at=assignment.updated_at
    )


# ==================== POST ENDPOINTS ====================

@router.post("/", response_model=AssignmentResponse, status_code=status.HTTP_201_CREATED)
async def create_assignment(
    assignment_data: AssignmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_teacher_or_admin)
):
    """
    Crea una nueva asignación.
    
    Solo profesores del curso o administradores.
    """
    # Verificar que el curso existe
    course = db.query(Course).filter(Course.id == assignment_data.course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Curso no encontrado"
        )
    
    # Verificar que sea el profesor del curso
    if current_user.role == UserRole.TEACHER:
        if course.teacher_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo el profesor del curso puede crear asignaciones"
            )
    
    # (Opcional) Verificar que la fecha de entrega sea futura
    # Comentado para evitar problemas con zonas horarias en desarrollo
    # if assignment_data.due_date <= datetime.utcnow():
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail="La fecha de entrega debe ser futura"
    #     )
    
    # Crear asignación
    new_assignment = Assignment(**assignment_data.model_dump())
    
    db.add(new_assignment)
    db.commit()
    db.refresh(new_assignment)
    
    return await get_assignment_by_id(new_assignment.id, db, current_user)


# ==================== PUT/PATCH ENDPOINTS ====================

@router.put("/{assignment_id}", response_model=AssignmentResponse)
async def update_assignment(
    assignment_id: int,
    assignment_data: AssignmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_teacher_or_admin)
):
    """
    Actualiza una asignación.
    
    Solo el profesor del curso o administradores.
    """
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asignación no encontrada"
        )
    
    # Verificar permisos
    if current_user.role == UserRole.TEACHER:
        if assignment.course.teacher_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo el profesor del curso puede editar esta asignación"
            )
    
    # Actualizar campos
    update_data = assignment_data.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(assignment, field, value)
    
    assignment.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(assignment)
    
    return await get_assignment_by_id(assignment_id, db, current_user)


@router.patch("/{assignment_id}/publish", response_model=MessageResponse)
async def toggle_assignment_publish(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_teacher_or_admin)
):
    """Publica o despublica una asignación"""
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asignación no encontrada"
        )
    
    # Verificar permisos
    if current_user.role == UserRole.TEACHER:
        if assignment.course.teacher_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo el profesor del curso puede publicar esta asignación"
            )
    
    assignment.is_published = not assignment.is_published
    db.commit()
    
    return MessageResponse(
        message=f"Asignación {'publicada' if assignment.is_published else 'despublicada'} exitosamente",
        success=True
    )


# ==================== DELETE ENDPOINTS ====================

@router.delete("/{assignment_id}", response_model=MessageResponse)
async def delete_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_teacher_or_admin)
):
    """
    Elimina una asignación.
    
    ADVERTENCIA: También eliminará todas las entregas asociadas.
    """
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asignación no encontrada"
        )
    
    # Verificar permisos
    if current_user.role == UserRole.TEACHER:
        if assignment.course.teacher_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo el profesor del curso puede eliminar esta asignación"
            )
    
    # Eliminar entregas asociadas primero
    from models import Submission
    submissions_count = len(assignment.submissions)
    if submissions_count > 0:
        db.query(Submission).filter(Submission.assignment_id == assignment_id).delete()
    
    db.delete(assignment)
    db.commit()
    
    if submissions_count > 0:
        return MessageResponse(
            message=f"Asignación eliminada junto con {submissions_count} entrega(s)",
            success=True
        )
    
    return MessageResponse(
        message="Asignación eliminada exitosamente",
        success=True
    )


# ==================== STATS ENDPOINTS ====================

@router.get("/{assignment_id}/stats")
async def get_assignment_stats(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_teacher_or_admin)
):
    """Obtiene estadísticas de una asignación"""
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asignación no encontrada"
        )
    
    # Verificar permisos
    if current_user.role == UserRole.TEACHER:
        if assignment.course.teacher_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes acceso a esta asignación"
            )
    
    from models import Submission, Enrollment
    
    # Calcular estadísticas
    total_students = db.query(Enrollment).filter(
        Enrollment.course_id == assignment.course_id,
        Enrollment.status == "enrolled"
    ).count()
    
    total_submissions = len(assignment.submissions)
    late_submissions = len([s for s in assignment.submissions if s.late])
    graded_submissions = len([s for s in assignment.submissions if s.grade is not None])
    
    # Promedio de calificaciones
    grades = [s.grade for s in assignment.submissions if s.grade is not None]
    average_grade = sum(grades) / len(grades) if grades else 0.0
    
    submission_rate = (total_submissions / total_students * 100) if total_students > 0 else 0.0
    
    return {
        "assignment_id": assignment.id,
        "total_students": total_students,
        "total_submissions": total_submissions,
        "pending_submissions": total_students - total_submissions,
        "late_submissions": late_submissions,
        "graded_submissions": graded_submissions,
        "pending_grading": total_submissions - graded_submissions,
        "average_grade": round(average_grade, 2),
        "submission_rate": round(submission_rate, 2),
        "is_overdue": assignment.is_overdue
    }