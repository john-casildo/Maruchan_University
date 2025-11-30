from fastapi import Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
import os
from dotenv import load_dotenv

from database import get_db
from models import User, UserRole
from schemas import TokenData

# Cargar variables de entorno
load_dotenv()

# Configuración de seguridad
SECRET_KEY = os.getenv("SECRET_KEY", "tu-clave-secreta-super-segura-cambiala-en-produccion")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Contexto para hashing de passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login", auto_error=False)


# ==================== PASSWORD UTILITIES ====================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica que una contraseña coincida con su hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Genera el hash de una contraseña"""
    return pwd_context.hash(password)


# ==================== TOKEN UTILITIES ====================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Crea un JWT token"""
    to_encode = data.copy()
    
    # Asegurar que sub sea string para compatibilidad JWT
    if "sub" in to_encode:
        to_encode["sub"] = str(to_encode["sub"])
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt


def decode_access_token(token: str) -> TokenData:
    """Decodifica un JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        username: str = payload.get("username")
        role: str = payload.get("role")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido"
            )
        
        return TokenData(user_id=user_id, username=username, role=role)
    
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se pudo validar las credenciales",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ==================== USER AUTHENTICATION ====================

def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """Autentica un usuario por username/email y password"""
    # Buscar por username o email
    user = db.query(User).filter(
        (User.username == username) | (User.email == username)
    ).first()
    
    if not user:
        return None
    
    if not verify_password(password, user.hashed_password):
        return None
    
    return user


# ==================== DEPENDENCIES ====================

async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    token_query: Optional[str] = Query(None, alias="token"),
    db: Session = Depends(get_db)
) -> User:
    """
    Obtiene el usuario actual desde el token JWT.
    Lanza excepción si el token es inválido o el usuario no existe.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Prioridad: Header > Query param
    final_token = token if token else token_query
    
    if not final_token:
        raise credentials_exception
    
    token_data = decode_access_token(final_token)
    
    user = db.query(User).filter(User.id == token_data.user_id).first()
    
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo"
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Verifica que el usuario esté activo"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo"
        )
    return current_user


# ==================== ROLE-BASED DEPENDENCIES ====================

async def get_current_student(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Verifica que el usuario actual sea estudiante"""
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere rol de estudiante"
        )
    return current_user


async def get_current_teacher(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Verifica que el usuario actual sea profesor"""
    if current_user.role != UserRole.TEACHER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere rol de profesor"
        )
    return current_user


async def get_current_admin(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Verifica que el usuario actual sea administrador"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere rol de administrador"
        )
    return current_user


async def get_current_teacher_or_admin(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Verifica que el usuario sea profesor o administrador"""
    if current_user.role not in [UserRole.TEACHER, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere rol de profesor o administrador"
        )
    return current_user


# ==================== VALIDATION UTILITIES ====================

def verify_course_access(
    user: User,
    course_id: int,
    db: Session,
    require_teacher: bool = False
) -> bool:
    """
    Verifica que un usuario tenga acceso a un curso.
    
    Args:
        user: Usuario a verificar
        course_id: ID del curso
        db: Sesión de base de datos
        require_teacher: Si True, verifica que sea el profesor del curso
    
    Returns:
        True si tiene acceso, False en caso contrario
    """
    from models import Course, Enrollment
    
    # Admins tienen acceso a todo
    if user.role == UserRole.ADMIN:
        return True
    
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        return False
    
    # Verificar si es el profesor del curso
    if require_teacher:
        return course.teacher_id == user.id
    
    # Profesores tienen acceso a sus cursos
    if user.role == UserRole.TEACHER and course.teacher_id == user.id:
        return True
    
    # Estudiantes solo si están inscritos
    if user.role == UserRole.STUDENT:
        enrollment = db.query(Enrollment).filter(
            Enrollment.student_id == user.id,
            Enrollment.course_id == course_id,
            Enrollment.status == "enrolled"
        ).first()
        return enrollment is not None
    
    return False


def verify_student_in_course(
    student_id: int,
    course_id: int,
    db: Session
) -> bool:
    """Verifica que un estudiante esté inscrito en un curso"""
    from models import Enrollment
    
    enrollment = db.query(Enrollment).filter(
        Enrollment.student_id == student_id,
        Enrollment.course_id == course_id,
        Enrollment.status == "enrolled"
    ).first()
    
    return enrollment is not None