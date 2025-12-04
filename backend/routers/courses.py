from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from database import get_db
from models import Course, User, UserRole, CourseStatus
from schemas import (
    CourseCreate, CourseUpdate, CourseResponse, CourseList,
    MessageResponse
)
from dependencies import (
    get_current_user,
    get_current_admin
)

router = APIRouter(
    prefix="/api/courses",
    tags=["Courses"]
)


# ==================== GET ENDPOINTS ====================

@router.get("/", response_model=List[CourseList])
async def get_courses(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: Optional[CourseStatus] = None,
    teacher_id: Optional[int] = None,
    carrera_id: Optional[int] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lista todos los cursos.
    """
    query = db.query(Course)
    
    # Aplicar filtros
    if status:
        query = query.filter(Course.status == status)
    
    if teacher_id:
        query = query.filter(Course.teacher_id == teacher_id)
        
    if carrera_id:
        query = query.filter(Course.carrera_id == carrera_id)
    
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (Course.title.ilike(search_filter)) |
            (Course.code.ilike(search_filter))
        )
    
    # Paginación
    courses = query.offset(skip).limit(limit).all()
    
    # Mapear a CourseList
    result = []
    for course in courses:
        # Contar solo inscripciones activas (no dropped)
        active_enrollments = [e for e in course.enrollments if e.status == "enrolled"]
        result.append({
            "id": course.id,
            "code": course.code,
            "title": course.title,
            "teacher_name": course.teacher.full_name if course.teacher else "Sin asignar",
            "teacher_id": course.teacher_id,
            "semester": course.semester,
            "credits": course.credits,
            "enrolled_count": len(active_enrollments),
            "status": course.status
        })
        
    return result


@router.get("/my-courses", response_model=List[CourseList])
async def get_my_courses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene los cursos del usuario actual.
    - Estudiantes: cursos donde están inscritos
    - Profesores: cursos que imparten
    """
    if current_user.role == UserRole.TEACHER:
        courses = db.query(Course).filter(Course.teacher_id == current_user.id).all()
    elif current_user.role == UserRole.STUDENT:
        # Obtener cursos a través de inscripciones ACTIVAS (no dropped)
        courses = [enrollment.course for enrollment in current_user.enrollments if enrollment.status == "enrolled"]
    else:
        # Admin ve todos (o podría no ver ninguno en "mis cursos")
        courses = db.query(Course).all()
        
    # Mapear a CourseList
    result = []
    for course in courses:
        # Contar solo inscripciones activas (no dropped)
        active_enrollments = [e for e in course.enrollments if e.status == "enrolled"]
        result.append({
            "id": course.id,
            "code": course.code,
            "title": course.title,
            "teacher_name": course.teacher.full_name if course.teacher else "Sin asignar",
            "teacher_id": course.teacher_id,
            "semester": course.semester,
            "credits": course.credits,
            "enrolled_count": len(active_enrollments),
            "status": course.status
        })
        
    return result


@router.get("/{course_id}", response_model=CourseResponse)
async def get_course_by_id(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtiene detalles de un curso"""
    course = db.query(Course).filter(Course.id == course_id).first()
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Curso no encontrado"
        )
        
    # Preparar respuesta
    response = CourseResponse.from_orm(course)
    # Contar solo inscripciones activas
    active_enrollments = [e for e in course.enrollments if e.status == "enrolled"]
    response.enrolled_count = len(active_enrollments)
    response.is_full = course.is_full
    
    return response


# ==================== POST ENDPOINTS ====================

@router.post("/", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
async def create_course(
    course_data: CourseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """
    Crea un nuevo curso (solo administradores).
    """
    # Verificar código único
    if db.query(Course).filter(Course.code == course_data.code).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El código del curso ya existe"
        )
        
    # Verificar que el profesor existe y es profesor
    teacher = db.query(User).filter(User.id == course_data.teacher_id).first()
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profesor no encontrado"
        )
    if teacher.role != UserRole.TEACHER and teacher.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario asignado no es un profesor"
        )
        
    new_course = Course(**course_data.dict())
    
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    
    # Preparar respuesta
    response = CourseResponse.from_orm(new_course)
    response.enrolled_count = 0
    
    return response


# ==================== PUT ENDPOINTS ====================

@router.put("/{course_id}", response_model=CourseResponse)
async def update_course(
    course_id: int,
    course_data: CourseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Actualiza un curso (solo administradores)"""
    course = db.query(Course).filter(Course.id == course_id).first()
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Curso no encontrado"
        )
        
    update_data = course_data.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(course, field, value)
        
    db.commit()
    db.refresh(course)
    
    response = CourseResponse.from_orm(course)
    # Contar solo inscripciones activas
    active_enrollments = [e for e in course.enrollments if e.status == "enrolled"]
    response.enrolled_count = len(active_enrollments)
    
    return response


# ==================== DELETE ENDPOINTS ====================

@router.delete("/{course_id}", response_model=MessageResponse)
async def delete_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Elimina un curso (solo administradores)"""
    course = db.query(Course).filter(Course.id == course_id).first()
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Curso no encontrado"
        )
        
    db.delete(course)
    db.commit()
    
    return MessageResponse(message="Curso eliminado exitosamente", success=True)