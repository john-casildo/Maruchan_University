from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import os
import shutil
from pathlib import Path

from database import get_db
from models import CourseMaterial, Course, User, UserRole, MaterialType
from schemas import (
    CourseMaterialCreate, CourseMaterialUpdate, CourseMaterialResponse,
    MessageResponse
)
from dependencies import (
    get_current_user,
    get_current_teacher_or_admin,
    verify_course_access
)

router = APIRouter(
    prefix="/api/materials",
    tags=["Course Materials"]
)

# Directorio base para materiales
MATERIALS_DIR = os.getenv("MATERIALS_DIR", "./maruchan_storage/materials")
Path(MATERIALS_DIR).mkdir(parents=True, exist_ok=True)

# Tamaño máximo de archivo (100MB para materiales)
MAX_MATERIAL_SIZE = 100 * 1024 * 1024

# Extensiones permitidas por tipo
ALLOWED_EXTENSIONS = {
    MaterialType.PDF: ['.pdf'],
    MaterialType.VIDEO: ['.mp4', '.avi', '.mov', '.mkv', '.webm'],
    MaterialType.SLIDE: ['.ppt', '.pptx', '.key', '.odp'],
    MaterialType.DOCUMENT: ['.doc', '.docx', '.txt', '.odt', '.rtf'],
    MaterialType.LINK: [],  # No requiere archivo
    MaterialType.OTHER: []  # Cualquier extensión
}


# ==================== UTILIDADES ====================

def save_material_file(upload_file: UploadFile, course_id: int, material_type: str) -> str:
    """
    Guarda un archivo de material y retorna la ruta relativa.
    
    Estructura: materials/course_{id}/type_{type}/filename.ext
    """
    # Crear directorio si no existe
    course_dir = Path(MATERIALS_DIR) / f"course_{course_id}" / f"type_{material_type}"
    course_dir.mkdir(parents=True, exist_ok=True)
    
    # Generar nombre con timestamp
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    file_extension = Path(upload_file.filename).suffix
    safe_filename = f"{timestamp}_{upload_file.filename}"
    
    file_path = course_dir / safe_filename
    
    # Guardar archivo
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)
    
    # Retornar ruta relativa
    return str(file_path.relative_to(MATERIALS_DIR))


def get_full_material_path(relative_path: str) -> Path:
    """Obtiene la ruta completa del archivo"""
    return Path(MATERIALS_DIR) / relative_path


def delete_material_file(relative_path: str) -> bool:
    """Elimina un archivo de material"""
    try:
        full_path = get_full_material_path(relative_path)
        if full_path.exists():
            full_path.unlink()
            return True
        return False
    except Exception as e:
        print(f"Error eliminando archivo: {e}")
        return False


def validate_file_extension(filename: str, material_type: MaterialType) -> bool:
    """Valida que la extensión del archivo sea permitida para el tipo"""
    if material_type in [MaterialType.LINK, MaterialType.OTHER]:
        return True
    
    file_extension = Path(filename).suffix.lower()
    allowed = ALLOWED_EXTENSIONS.get(material_type, [])
    
    return file_extension in allowed if allowed else True


# ==================== GET ENDPOINTS ====================

@router.get("/", response_model=List[CourseMaterialResponse])
async def get_materials(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    course_id: Optional[int] = None,
    material_type: Optional[MaterialType] = None,
    visible_only: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lista materiales del curso con filtros opcionales.
    
    Filtros:
    - course_id: Filtrar por curso
    - material_type: Filtrar por tipo de material
    - visible_only: Solo materiales visibles
    """
    query = db.query(CourseMaterial)
    
    # Filtrar por curso
    if course_id:
        # Verificar acceso al curso
        if not verify_course_access(current_user, course_id, db):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes acceso a este curso"
            )
        query = query.filter(CourseMaterial.course_id == course_id)
    else:
        # Sin curso específico, filtrar por cursos accesibles
        if current_user.role == UserRole.STUDENT:
            from models import Enrollment
            enrolled_courses = db.query(Enrollment.course_id).filter(
                Enrollment.student_id == current_user.id,
                Enrollment.status == "enrolled"
            ).all()
            course_ids = [c[0] for c in enrolled_courses]
            query = query.filter(CourseMaterial.course_id.in_(course_ids))
        
        elif current_user.role == UserRole.TEACHER:
            teacher_courses = [c.id for c in current_user.courses_taught]
            query = query.filter(CourseMaterial.course_id.in_(teacher_courses))
    
    # Filtros adicionales
    if material_type:
        query = query.filter(CourseMaterial.type == material_type)
    
    # Estudiantes solo ven materiales visibles
    if visible_only and current_user.role == UserRole.STUDENT:
        query = query.filter(CourseMaterial.is_visible == True)
    
    materials = query.order_by(CourseMaterial.order, CourseMaterial.uploaded_at.desc()).offset(skip).limit(limit).all()
    
    # Formatear respuesta
    from schemas import CourseList
    
    result = []
    for material in materials:
        course_data = CourseList(
            id=material.course.id,
            code=material.course.code,
            title=material.course.title,
            teacher_name=material.course.teacher.full_name,
            semester=material.course.semester,
            credits=material.course.credits,
            enrolled_count=len([e for e in material.course.enrollments if e.status == "enrolled"]),
            status=material.course.status
        )
        
        uploaded_by_name = None
        if material.uploaded_by:
            uploaded_by_name = material.uploaded_by.full_name
        
        result.append(CourseMaterialResponse(
            id=material.id,
            course_id=material.course_id,
            course=course_data,
            title=material.title,
            description=material.description,
            file_path=material.file_path,
            type=material.type,
            uploaded_at=material.uploaded_at,
            uploaded_by_name=uploaded_by_name,
            is_visible=material.is_visible,
            order=material.order
        ))
    
    return result


@router.get("/{material_id}", response_model=CourseMaterialResponse)
async def get_material_by_id(
    material_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtiene un material por ID"""
    material = db.query(CourseMaterial).filter(CourseMaterial.id == material_id).first()
    
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Material no encontrado"
        )
    
    # Verificar acceso al curso
    if not verify_course_access(current_user, material.course_id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes acceso a este material"
        )
    
    # Estudiantes solo ven materiales visibles
    if current_user.role == UserRole.STUDENT and not material.is_visible:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Material no encontrado"
        )
    
    # Formatear respuesta
    from schemas import CourseList
    
    course_data = CourseList(
        id=material.course.id,
        code=material.course.code,
        title=material.course.title,
        teacher_name=material.course.teacher.full_name,
        semester=material.course.semester,
        credits=material.course.credits,
        enrolled_count=len([e for e in material.course.enrollments if e.status == "enrolled"]),
        status=material.course.status
    )
    
    uploaded_by_name = None
    if material.uploaded_by:
        uploaded_by_name = material.uploaded_by.full_name
    
    return CourseMaterialResponse(
        id=material.id,
        course_id=material.course_id,
        course=course_data,
        title=material.title,
        description=material.description,
        file_path=material.file_path,
        type=material.type,
        uploaded_at=material.uploaded_at,
        uploaded_by_name=uploaded_by_name,
        is_visible=material.is_visible,
        order=material.order
    )


# ==================== POST ENDPOINTS (UPLOAD) ====================

@router.post("/upload", response_model=CourseMaterialResponse, status_code=status.HTTP_201_CREATED)
async def upload_material(
    course_id: int = Form(...),
    title: str = Form(...),
    material_type: MaterialType = Form(...),
    description: Optional[str] = Form(None),
    is_visible: bool = Form(True),
    order: int = Form(0),
    file: Optional[UploadFile] = File(None),
    file_path: Optional[str] = Form(None),  # Para links
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_teacher_or_admin)
):
    """
    Sube un material al curso.
    
    Solo profesores del curso o administradores.
    
    - Para archivos: enviar 'file'
    - Para links: enviar 'file_path' (URL)
    """
    # Verificar que el curso existe
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Curso no encontrado"
        )
    
    # Verificar permisos
    if current_user.role == UserRole.TEACHER:
        if course.teacher_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo el profesor del curso puede subir materiales"
            )
    
    # Validar que se proporcione archivo o URL según el tipo
    if material_type == MaterialType.LINK:
        if not file_path:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Debe proporcionar una URL para materiales de tipo 'link'"
            )
        final_path = file_path
    
    else:
        if not file:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Debe proporcionar un archivo para este tipo de material"
            )
        
        # Validar extensión
        if not validate_file_extension(file.filename, material_type):
            allowed = ALLOWED_EXTENSIONS.get(material_type, [])
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Extensión no permitida. Permitidas: {', '.join(allowed)}"
            )
        
        # Verificar tamaño
        file.file.seek(0, 2)
        file_size = file.file.tell()
        file.file.seek(0)
        
        if file_size > MAX_MATERIAL_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Archivo muy grande. Máximo {MAX_MATERIAL_SIZE / 1024 / 1024}MB"
            )
        
        # Guardar archivo
        try:
            final_path = save_material_file(file, course_id, material_type.value)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error guardando archivo: {str(e)}"
            )
    
    # Crear material
    new_material = CourseMaterial(
        course_id=course_id,
        title=title,
        description=description,
        file_path=final_path,
        type=material_type,
        uploaded_by_id=current_user.id,
        is_visible=is_visible,
        order=order
    )
    
    db.add(new_material)
    db.commit()
    db.refresh(new_material)
    
    return await get_material_by_id(new_material.id, db, current_user)


# ==================== PUT/PATCH ENDPOINTS ====================

@router.put("/{material_id}", response_model=CourseMaterialResponse)
async def update_material(
    material_id: int,
    material_data: CourseMaterialUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_teacher_or_admin)
):
    """Actualiza la información de un material (sin cambiar el archivo)"""
    material = db.query(CourseMaterial).filter(CourseMaterial.id == material_id).first()
    
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Material no encontrado"
        )
    
    # Verificar permisos
    if current_user.role == UserRole.TEACHER:
        if material.course.teacher_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo el profesor del curso puede editar materiales"
            )
    
    # Actualizar campos
    update_data = material_data.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(material, field, value)
    
    db.commit()
    db.refresh(material)
    
    return await get_material_by_id(material_id, db, current_user)


@router.patch("/{material_id}/toggle-visibility", response_model=MessageResponse)
async def toggle_material_visibility(
    material_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_teacher_or_admin)
):
    """Cambia la visibilidad de un material"""
    material = db.query(CourseMaterial).filter(CourseMaterial.id == material_id).first()
    
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Material no encontrado"
        )
    
    # Verificar permisos
    if current_user.role == UserRole.TEACHER:
        if material.course.teacher_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo el profesor del curso puede cambiar la visibilidad"
            )
    
    material.is_visible = not material.is_visible
    db.commit()
    
    return MessageResponse(
        message=f"Material {'visible' if material.is_visible else 'oculto'}",
        success=True
    )


# ==================== DOWNLOAD ENDPOINT ====================

@router.get("/{material_id}/download")
async def download_material(
    material_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Descarga un material del curso.
    
    Solo usuarios con acceso al curso.
    """
    material = db.query(CourseMaterial).filter(CourseMaterial.id == material_id).first()
    
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Material no encontrado"
        )
    
    # Verificar acceso
    if not verify_course_access(current_user, material.course_id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes acceso a este material"
        )
    
    # Estudiantes solo descargan materiales visibles
    if current_user.role == UserRole.STUDENT and not material.is_visible:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Material no encontrado"
        )
    
    # Si es un link, retornar la URL
    if material.type == MaterialType.LINK:
        return {"url": material.file_path, "type": "link"}
    
    # Obtener archivo
    file_path = get_full_material_path(material.file_path)
    
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


# ==================== DELETE ENDPOINTS ====================

@router.delete("/{material_id}", response_model=MessageResponse)
async def delete_material(
    material_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_teacher_or_admin)
):
    """
    Elimina un material del curso.
    
    Solo profesores del curso o administradores.
    """
    material = db.query(CourseMaterial).filter(CourseMaterial.id == material_id).first()
    
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Material no encontrado"
        )
    
    # Verificar permisos
    if current_user.role == UserRole.TEACHER:
        if material.course.teacher_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo el profesor del curso puede eliminar materiales"
            )
    
    # Eliminar archivo si no es link
    if material.type != MaterialType.LINK:
        delete_material_file(material.file_path)
    
    # Eliminar de BD
    db.delete(material)
    db.commit()
    
    return MessageResponse(
        message="Material eliminado exitosamente",
        success=True
    )