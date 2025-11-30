from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
import shutil
import os
import uuid

from database import get_db
from models import User, UserRole
from schemas import (
    UserCreate, UserUpdate, UserResponse, UserList,
    MessageResponse
)
from dependencies import (
    get_current_user,
    get_current_admin,
    get_password_hash
)

router = APIRouter(
    prefix="/api/users",
    tags=["Users"]
)


# ==================== GET ENDPOINTS ====================

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Obtiene la información del usuario autenticado"""
    return current_user


@router.get("/", response_model=List[UserList])
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    role: Optional[UserRole] = None,
    carrera_id: Optional[int] = None,
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lista todos los usuarios.
    
    Permisos:
    - Admins: pueden ver todos
    - Profesores: pueden ver estudiantes (para inscribirlos)
    """
    
    """ ES POR EL HECHO DEL CHAT
    # Verificar permisos
    if current_user.role != UserRole.ADMIN:
        # Si no es admin, solo permitimos si es profesor buscando estudiantes
        if current_user.role == UserRole.TEACHER:
            # Forzamos el filtro de rol a STUDENT si es profesor
            # O verificamos que esté pidiendo estudiantes
            if role != UserRole.STUDENT:
                 raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Los profesores solo pueden listar estudiantes"
                )
        else:
            # Estudiantes no pueden listar usuarios
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para listar usuarios"
            )"""

    query = db.query(User)
    
    # Aplicar filtros
    if role:
        query = query.filter(User.role == role)
    
    if carrera_id:
        query = query.filter(User.carrera_id == carrera_id)
    
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (User.first_name.ilike(search_filter)) |
            (User.last_name.ilike(search_filter)) |
            (User.email.ilike(search_filter)) |
            (User.carnet.ilike(search_filter))
        )
    
    # Paginación
    users = query.offset(skip).limit(limit).all()
    
    return users


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene un usuario por ID.
    
    Permisos:
    - Admins: pueden ver cualquier usuario
    - Otros: solo pueden ver su propia información
    """
    # Verificar permisos
    if current_user.role != UserRole.ADMIN and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para ver este usuario"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    return user


@router.get("/by-role/{role}", response_model=List[UserList])
async def get_users_by_role(
    role: UserRole,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Lista usuarios por rol específico"""
    users = db.query(User).filter(
        User.role == role,
        User.is_active == True
    ).offset(skip).limit(limit).all()
    
    return users


@router.get("/students/by-carrera/{carrera_id}", response_model=List[UserList])
async def get_students_by_carrera(
    carrera_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Lista estudiantes de una carrera específica"""
    users = db.query(User).filter(
        User.role == UserRole.STUDENT,
        User.carrera_id == carrera_id,
        User.is_active == True
    ).offset(skip).limit(limit).all()
    
    return users


# ==================== POST ENDPOINTS ====================

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """
    Crea un nuevo usuario (solo administradores).
    
    La contraseña será hasheada automáticamente.
    """
    # Verificar si el username ya existe
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El username ya está en uso"
        )
    
    # Verificar si el email ya existe
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya está registrado"
        )
    
    # Verificar si el carnet ya existe (si se proporciona)
    if user_data.carnet:
        if db.query(User).filter(User.carnet == user_data.carnet).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El carnet ya está registrado"
            )
    
    # Crear usuario
    user_dict = user_data.model_dump(exclude={"password", "password_confirm"})
    user_dict["hashed_password"] = get_password_hash(user_data.password)
    
    new_user = User(**user_dict)
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


# ==================== PUT/PATCH ENDPOINTS ====================

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Actualiza un usuario.
    
    Permisos:
    - Admins: pueden actualizar cualquier usuario
    - Otros: solo pueden actualizar su propia información
    """
    # Verificar permisos
    if current_user.role != UserRole.ADMIN and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para actualizar este usuario"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # Actualizar solo los campos proporcionados
    update_data = user_data.model_dump(exclude_unset=True)
    
    # Verificar email único si se está actualizando
    if "email" in update_data and update_data["email"] != user.email:
        if db.query(User).filter(User.email == update_data["email"]).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El email ya está en uso"
            )
    
    for field, value in update_data.items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    
    return user


@router.patch("/{user_id}/toggle-active", response_model=MessageResponse)
async def toggle_user_active(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Activa o desactiva un usuario (solo administradores)"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # No permitir desactivar al propio admin
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes desactivar tu propia cuenta"
        )
    
    user.is_active = not user.is_active
    db.commit()
    
    return MessageResponse(
        message=f"Usuario {'activado' if user.is_active else 'desactivado'} exitosamente",
        success=True
    )


# ==================== DELETE ENDPOINTS ====================

@router.delete("/{user_id}", response_model=MessageResponse)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """
    Elimina un usuario (solo administradores).
    
    ADVERTENCIA: Esta operación es permanente.
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # No permitir eliminar al propio admin
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes eliminar tu propia cuenta"
        )
    
    db.delete(user)
    db.commit()
    
    return MessageResponse(
        message="Usuario eliminado exitosamente",
        success=True
    )


# ==================== STATS ENDPOINTS ====================

@router.get("/stats/summary")
async def get_users_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Obtiene estadísticas generales de usuarios (solo administradores)"""
    total_users = db.query(User).count()
    total_students = db.query(User).filter(User.role == UserRole.STUDENT).count()
    total_teachers = db.query(User).filter(User.role == UserRole.TEACHER).count()
    total_admins = db.query(User).filter(User.role == UserRole.ADMIN).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    
    return {
        "total_users": total_users,
        "total_students": total_students,
        "total_teachers": total_teachers,
        "total_admins": total_admins,
        "active_users": active_users,
        "inactive_users": total_users - active_users
    }


@router.post("/{user_id}/profile-picture", response_model=UserResponse)
async def upload_profile_picture(
    user_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Sube una foto de perfil para el usuario.
    """
    # Verificar permisos
    if current_user.role != UserRole.ADMIN and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para actualizar este usuario"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # Validar tipo de archivo
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo debe ser una imagen"
        )
    
    # Crear directorio si no existe
    STORAGE_DIR = os.getenv("STORAGE_DIR", "./maruchan_storage")
    profiles_dir = os.path.join(STORAGE_DIR, "profiles")
    os.makedirs(profiles_dir, exist_ok=True)
    
    # Generar nombre único
    file_ext = file.filename.split(".")[-1]
    filename = f"user_{user_id}_{uuid.uuid4()}.{file_ext}"
    file_path = os.path.join(profiles_dir, filename)
    
    # Guardar archivo
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # Actualizar URL en base de datos
    # La URL debe ser accesible desde el frontend. 
    # Asumimos que /files está montado en backend/main.py
    # Guardamos la ruta relativa para ser servida por StaticFiles
    # Nota: El frontend deberá anteponer la URL base del backend
    relative_path = f"/files/profiles/{filename}"
    
    user.profile_pic_url = relative_path
    db.commit()
    db.refresh(user)
    
    return user