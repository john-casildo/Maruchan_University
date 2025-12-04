from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from database import get_db
from models import Enrollment, Course, User, UserRole, EnrollmentStatus
from schemas import (
    EnrollmentCreate, EnrollmentUpdate, EnrollmentResponse,
    EnrollmentGrade, MessageResponse
)
from dependencies import (
    get_current_user,
    get_current_student,
    get_current_teacher_or_admin
)

router = APIRouter(
    prefix="/api/enrollments",
    tags=["Enrollments"]
)


# ==================== GET ENDPOINTS ====================

@router.get("/", response_model=List[EnrollmentResponse])
async def get_enrollments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    course_id: Optional[int] = None,
    student_id: Optional[int] = None,
    status: Optional[EnrollmentStatus] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lista inscripciones con filtros opcionales.
    
    Permisos:
    - Admins: todas las inscripciones
    - Profesores: inscripciones de sus cursos
    - Estudiantes: solo sus propias inscripciones
    """
    query = db.query(Enrollment)
    
    # Aplicar filtros según el rol
    if current_user.role == UserRole.STUDENT:
        query = query.filter(Enrollment.student_id == current_user.id)
    
    elif current_user.role == UserRole.TEACHER:
        # Solo inscripciones de cursos que imparte
        teacher_courses = [c.id for c in current_user.courses_taught]
        query = query.filter(Enrollment.course_id.in_(teacher_courses))
    
    # Aplicar filtros adicionales
    if course_id:
        query = query.filter(Enrollment.course_id == course_id)
    
    if student_id:
        # Solo admins y el propio estudiante pueden filtrar por student_id
        if current_user.role != UserRole.ADMIN and current_user.id != student_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para ver inscripciones de otros estudiantes"
            )
        query = query.filter(Enrollment.student_id == student_id)
    
    if status:
        query = query.filter(Enrollment.status == status)
    
    enrollments = query.offset(skip).limit(limit).all()
    
    # Formatear respuesta
    from schemas import UserList, CourseList
    
    result = []
    for enrollment in enrollments:
        student_data = UserList(
            id=enrollment.student.id,
            full_name=enrollment.student.full_name,
            email=enrollment.student.email,
            role=enrollment.student.role,
            carnet=enrollment.student.carnet,
            is_active=enrollment.student.is_active
            )
        
        course_data = CourseList(
            id=enrollment.course.id,
            code=enrollment.course.code,
            title=enrollment.course.title,
            teacher_name=enrollment.course.teacher.full_name,
            teacher_id=enrollment.course.teacher_id,
            semester=enrollment.course.semester,
            credits=enrollment.course.credits,
            enrolled_count=len([e for e in enrollment.course.enrollments if e.status == "enrolled"]),
            status=enrollment.course.status
        )
        
        result.append(EnrollmentResponse(
            id=enrollment.id,
            student_id=enrollment.student_id,
            student=student_data,
            course_id=enrollment.course_id,
            course=course_data,
            status=enrollment.status,
            grade=enrollment.grade,
            enrolled_at=enrollment.enrolled_at,
            status_update_date=enrollment.status_update_date,
            grade_assigned_date=enrollment.grade_assigned_date
        ))
    
    return result


@router.get("/my-enrollments", response_model=List[EnrollmentResponse])
async def get_my_enrollments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student)
):
    """Obtiene las inscripciones del estudiante actual"""
    return await get_enrollments(
        student_id=current_user.id,
        db=db,
        current_user=current_user
    )


@router.get("/{enrollment_id}", response_model=EnrollmentResponse)
async def get_enrollment_by_id(
    enrollment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtiene una inscripción por ID"""
    enrollment = db.query(Enrollment).filter(Enrollment.id == enrollment_id).first()
    
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inscripción no encontrada"
        )
    
    # Verificar permisos
    if current_user.role == UserRole.STUDENT:
        if enrollment.student_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para ver esta inscripción"
            )
    
    elif current_user.role == UserRole.TEACHER:
        if enrollment.course.teacher_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para ver esta inscripción"
            )
    
    # Formatear respuesta
    from schemas import UserList, CourseList
    
    student_data = UserList(
        id=enrollment.student.id,
        full_name=enrollment.student.full_name,
        email=enrollment.student.email,
        role=enrollment.student.role,
        carnet=enrollment.student.carnet,
        is_active=enrollment.student.is_active
    )
    
    course_data = CourseList(
        id=enrollment.course.id,
        code=enrollment.course.code,
        title=enrollment.course.title,
        teacher_name=enrollment.course.teacher.full_name,
        teacher_id=enrollment.course.teacher_id,
        semester=enrollment.course.semester,
        credits=enrollment.course.credits,
        enrolled_count=len([e for e in enrollment.course.enrollments if e.status == "enrolled"]),
        status=enrollment.course.status
    )
    
    return EnrollmentResponse(
        id=enrollment.id,
        student_id=enrollment.student_id,
        student=student_data,
        course_id=enrollment.course_id,
        course=course_data,
        status=enrollment.status,
        grade=enrollment.grade,
        enrolled_at=enrollment.enrolled_at,
        status_update_date=enrollment.status_update_date,
        grade_assigned_date=enrollment.grade_assigned_date
    )


# ==================== POST ENDPOINTS ====================

@router.post("/", response_model=EnrollmentResponse, status_code=status.HTTP_201_CREATED)
async def create_enrollment(
    enrollment_data: EnrollmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Crea una nueva inscripción.
    
    Permisos:
    - Estudiantes: pueden inscribirse a sí mismos
    - Admins: pueden inscribir a cualquier estudiante
    """
    # Verificar permisos
    if current_user.role == UserRole.STUDENT:
        if enrollment_data.student_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo puedes inscribirte a ti mismo"
            )
    
    # Verificar que el curso existe
    course = db.query(Course).filter(Course.id == enrollment_data.course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Curso no encontrado"
        )

    # Si es profesor, verificar que sea SU curso
    if current_user.role == UserRole.TEACHER:
        if course.teacher_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo puedes inscribir estudiantes en tus propios cursos"
            )
    
    # Verificar que el estudiante existe y es estudiante
    student = db.query(User).filter(User.id == enrollment_data.student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Estudiante no encontrado"
        )
    
    if student.role != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario seleccionado no es un estudiante"
        )
    
    # Verificar que el curso existe
    course = db.query(Course).filter(Course.id == enrollment_data.course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Curso no encontrado"
        )
    
    # Verificar que el curso esté activo
    if course.status != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El curso no está activo"
        )
    
    # Verificar si ya existe una inscripción (activa o dropped)
    existing = db.query(Enrollment).filter(
        Enrollment.student_id == enrollment_data.student_id,
        Enrollment.course_id == enrollment_data.course_id
    ).first()
    
    if existing:
        # Si ya está inscrito activamente, error
        if existing.status == EnrollmentStatus.ENROLLED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El estudiante ya está inscrito en este curso"
            )
        # Si estaba dropped, reactivar la inscripción
        elif existing.status == EnrollmentStatus.DROPPED:
            existing.status = EnrollmentStatus.ENROLLED
            existing.status_update_date = datetime.utcnow()
            db.commit()
            db.refresh(existing)
            return await get_enrollment_by_id(existing.id, db, current_user)
    
    # Verificar cupo disponible
    if course.is_full:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El curso ha alcanzado su capacidad máxima"
        )
    
    # Crear inscripción nueva
    new_enrollment = Enrollment(**enrollment_data.model_dump())
    
    db.add(new_enrollment)
    db.commit()
    db.refresh(new_enrollment)
    
    return await get_enrollment_by_id(new_enrollment.id, db, current_user)


@router.post("/enroll/{course_id}", response_model=EnrollmentResponse)
async def enroll_in_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student)
):
    """Inscribe al estudiante actual en un curso"""
    enrollment_data = EnrollmentCreate(
        student_id=current_user.id,
        course_id=course_id
    )
    
    return await create_enrollment(enrollment_data, db, current_user)


# ==================== PUT/PATCH ENDPOINTS ====================

@router.patch("/{enrollment_id}/drop", response_model=MessageResponse)
async def drop_enrollment(
    enrollment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retira a un estudiante de un curso.
    
    Permisos:
    - Estudiantes: pueden retirarse ellos mismos
    - Profesores: pueden retirar estudiantes de sus cursos
    - Admins: pueden retirar a cualquier estudiante
    """
    enrollment = db.query(Enrollment).filter(Enrollment.id == enrollment_id).first()
    
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inscripción no encontrada"
        )
    
    # Verificar permisos
    if current_user.role == UserRole.STUDENT:
        if enrollment.student_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo puedes retirarte de tus propios cursos"
            )
    elif current_user.role == UserRole.TEACHER:
        # Los profesores pueden retirar estudiantes de sus propios cursos
        if enrollment.course.teacher_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo puedes retirar estudiantes de tus propios cursos"
            )
    # Admins pueden retirar a cualquiera
    
    if enrollment.status == EnrollmentStatus.DROPPED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El estudiante ya está retirado de este curso"
        )
    
    enrollment.status = EnrollmentStatus.DROPPED
    enrollment.status_update_date = datetime.utcnow()
    
    db.commit()
    
    return MessageResponse(
        message="Estudiante retirado del curso exitosamente",
        success=True
    )


@router.patch("/{enrollment_id}/grade", response_model=EnrollmentResponse)
async def update_enrollment_grade(
    enrollment_id: int,
    grade_data: EnrollmentGrade,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_teacher_or_admin)
):
    """
    Actualiza la calificación de una inscripción.
    
    Solo profesores del curso o administradores.
    """
    enrollment = db.query(Enrollment).filter(Enrollment.id == enrollment_id).first()
    
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inscripción no encontrada"
        )
    
    # Verificar que sea el profesor del curso
    if current_user.role == UserRole.TEACHER:
        if enrollment.course.teacher_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo el profesor del curso puede calificar"
            )
    
    enrollment.grade = grade_data.grade
    enrollment.grade_assigned_date = datetime.utcnow()
    
    db.commit()
    db.refresh(enrollment)
    
    return await get_enrollment_by_id(enrollment_id, db, current_user)


@router.patch("/{enrollment_id}/complete", response_model=MessageResponse)
async def complete_enrollment(
    enrollment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_teacher_or_admin)
):
    """Marca una inscripción como completada"""
    enrollment = db.query(Enrollment).filter(Enrollment.id == enrollment_id).first()
    
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inscripción no encontrada"
        )
    
    # Verificar que sea el profesor del curso
    if current_user.role == UserRole.TEACHER:
        if enrollment.course.teacher_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo el profesor del curso puede completar inscripciones"
            )
    
    if enrollment.grade is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe asignar una calificación antes de completar la inscripción"
        )
    
    enrollment.status = EnrollmentStatus.COMPLETED
    enrollment.status_update_date = datetime.utcnow()
    
    db.commit()
    
    return MessageResponse(
        message="Inscripción marcada como completada",
        success=True
    )


# ==================== DELETE ENDPOINTS ====================

@router.delete("/{enrollment_id}", response_model=MessageResponse)
async def delete_enrollment(
    enrollment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Elimina una inscripción (solo administradores).
    
    ADVERTENCIA: Esta operación es permanente.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los administradores pueden eliminar inscripciones"
        )
    
    enrollment = db.query(Enrollment).filter(Enrollment.id == enrollment_id).first()
    
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inscripción no encontrada"
        )
    
    db.delete(enrollment)
    db.commit()
    
    return MessageResponse(
        message="Inscripción eliminada exitosamente",
        success=True
    )