from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from datetime import timedelta
import uvicorn
import os

from database import get_db, check_db_connection, Base, engine
from dependencies import (
    authenticate_user,
    create_access_token,
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from schemas import Token, UserResponse
from models import User

# Importar routers
from routers import (
    users,
    courses,
    enrollments,
    assignments,
    submissions,
    materials,
    chat
)

# ==================== CREAR APLICACIÓN ====================

app = FastAPI(
    title="Maruchan University API",
    description="API para el sistema de gestión universitaria Maruchan University",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


# ==================== CONFIGURAR CORS ====================

# Lista de orígenes permitidos
#origins = [
#"http://localhost:3000",  # React/Next.js en desarrollo
#"http://localhost:5173",  # Vite en desarrollo
#"http://localhost:5174",
#"http://127.0.0.1:3000",
#"http://127.0.0.1:5173",
#"http://127.0.0.1:5174",
# Agregar tu dominio de producción aquí
# "https://maruchan-university.com",
#]

app.add_middleware(
    CORSMiddleware,
    #allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== CONFIGURAR DIRECTORIOS DE ARCHIVOS ====================

# Crear directorios si no existen
STORAGE_DIR = os.getenv("STORAGE_DIR", "./maruchan_storage")
os.makedirs(f"{STORAGE_DIR}/submissions", exist_ok=True)
os.makedirs(f"{STORAGE_DIR}/materials", exist_ok=True)
os.makedirs(f"{STORAGE_DIR}/profiles", exist_ok=True)

# Montar directorio estático para archivos (opcional, para desarrollo)
# En producción usar nginx o similar
app.mount("/files", StaticFiles(directory=STORAGE_DIR), name="files")


# ==================== EVENTOS DE INICIO/CIERRE ====================

@app.on_event("startup")
async def startup_event():
    """Se ejecuta al iniciar la aplicación"""
    print("=" * 60)
    print("🎓 Maruchan University - Sistema de Gestión Universitaria")
    print("=" * 60)
    print("🚀 Iniciando API...")
    
    # Verificar conexión a la base de datos
    if check_db_connection():
        print("✅ Conexión a base de datos establecida")
    else:
        print("❌ Error: No se pudo conectar a la base de datos")
        print("   Verifica tu DATABASE_URL en el archivo .env")
    
    # Crear tablas (solo en desarrollo, en producción usar Alembic)
    # Base.metadata.create_all(bind=engine)
    
    print("=" * 60)
    print("📚 Documentación disponible en:")
    print("   - Swagger UI: http://localhost:8000/docs")
    print("   - ReDoc: http://localhost:8000/redoc")
    print("=" * 60)
    print("✅ API lista para recibir requests")
    print("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    """Se ejecuta al cerrar la aplicación"""
    print("\n" + "=" * 60)
    print("👋 Cerrando Maruchan University API...")
    print("=" * 60)


# ==================== ENDPOINTS BÁSICOS ====================

@app.get("/")
async def root():
    """Endpoint raíz - Verificación de salud"""
    return {
        "message": "Bienvenido a Maruchan University API",
        "version": "1.0.0",
        "status": "online",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "auth": "/api/auth/*",
            "users": "/api/users/*",
            "courses": "/api/courses/*",
            "enrollments": "/api/enrollments/*",
            "assignments": "/api/assignments/*",
            "submissions": "/api/submissions/*",
            "materials": "/api/materials/*"
        }
    }


@app.get("/health")
async def health_check():
    """Verificación de salud del servicio"""
    db_status = check_db_connection()
    
    # Verificar directorios de almacenamiento
    storage_ok = os.path.exists(STORAGE_DIR)
    
    return {
        "status": "healthy" if (db_status and storage_ok) else "unhealthy",
        "database": "connected" if db_status else "disconnected",
        "storage": "ready" if storage_ok else "not_ready",
        "api": "running",
        "version": "1.0.0"
    }


# ==================== AUTENTICACIÓN ====================

@app.post("/api/auth/login", response_model=Token, tags=["Authentication"])
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Endpoint de login.
    
    Acepta username o email en el campo 'username'.
    Retorna un JWT token de acceso.
    
    **Ejemplo de uso:**
    ```json
    {
        "username": "usuario@ejemplo.com",
        "password": "tu_contraseña"
    }
    ```
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo. Contacta al administrador."
        )
    
    # Crear token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": user.id,
            "username": user.username,
            "role": user.role.value
        },
        expires_delta=access_token_expires
    )
    
    # Actualizar último login
    from datetime import datetime
    user.last_login = datetime.utcnow()
    db.commit()
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@app.post("/api/auth/logout", tags=["Authentication"])
async def logout(current_user: User = Depends(get_current_user)):
    """
    Endpoint de logout.
    
    Nota: Con JWT no hay logout real del lado del servidor.
    El cliente debe eliminar el token de su almacenamiento local.
    """
    return {
        "message": "Sesión cerrada exitosamente",
        "success": True,
        "user": current_user.username
    }


@app.get("/api/auth/me", response_model=UserResponse, tags=["Authentication"])
async def get_me(current_user: User = Depends(get_current_user)):
    """
    Obtiene información del usuario autenticado actualmente.
    
    Retorna toda la información del perfil del usuario.
    """
    return current_user


# ==================== INCLUIR ROUTERS ====================

# Router de usuarios
app.include_router(
    users.router,
    dependencies=[Depends(get_current_user)]
)

# Router de cursos
app.include_router(
    courses.router,
    dependencies=[Depends(get_current_user)]
)

# Router de inscripciones
app.include_router(
    enrollments.router,
    dependencies=[Depends(get_current_user)]
)

# Router de asignaciones/tareas
app.include_router(
    assignments.router,
    dependencies=[Depends(get_current_user)]
)

# Router de entregas (con upload de archivos)
app.include_router(
    submissions.router,
    dependencies=[Depends(get_current_user)]
)

# Router de materiales (con upload de archivos)
app.include_router(
    materials.router,
    dependencies=[Depends(get_current_user)]
)

# Router de chat y mensajería 
app.include_router(
    chat.router,
    dependencies=[Depends(get_current_user)]
)

from fastapi.responses import JSONResponse

# ==================== MANEJO DE ERRORES GLOBAL ====================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Manejo personalizado de excepciones HTTP"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "path": str(request.url)
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Manejo de excepciones no capturadas"""
    import traceback
    print(f"❌ Error no manejado: {exc}")
    print(traceback.format_exc())
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Error interno del servidor",
            "status_code": 500,
            "detail": str(exc) if os.getenv("DEBUG", "False") == "True" else "Error interno",
            "path": str(request.url)
        }
    )


# ==================== UTILIDADES ====================

@app.get("/api/info", tags=["Info"])
async def get_api_info():
    """Información general de la API"""
    return {
        "name": "Maruchan University API",
        "version": "1.0.0",
        "description": "Sistema de gestión universitaria completo",
        "features": [
            "Autenticación JWT",
            "Gestión de usuarios (estudiantes, profesores, admins)",
            "Gestión de cursos y carreras",
            "Sistema de inscripciones",
            "Asignaciones y entregas con archivos",
            "Materiales del curso con archivos",
            "Control de calificaciones",
            "Estadísticas y reportes"
        ],
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc"
        },
        "contact": {
            "name": "Maruchan University",
            "email": "admin@maruchan.edu"
        }
    }


@app.get("/api/stats/overview", tags=["Stats"])
async def get_overview_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Estadísticas generales del sistema (solo administradores)"""
    from models import Course, Enrollment, Assignment, Submission, UserRole
    
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden ver estas estadísticas"
        )
    
    total_users = db.query(User).count()
    total_students = db.query(User).filter(User.role == UserRole.STUDENT).count()
    total_teachers = db.query(User).filter(User.role == UserRole.TEACHER).count()
    total_courses = db.query(Course).count()
    active_courses = db.query(Course).filter(Course.status == "active").count()
    total_enrollments = db.query(Enrollment).filter(Enrollment.status == "enrolled").count()
    total_assignments = db.query(Assignment).count()
    total_submissions = db.query(Submission).count()
    
    return {
        "users": {
            "total": total_users,
            "students": total_students,
            "teachers": total_teachers,
            "admins": total_users - total_students - total_teachers
        },
        "courses": {
            "total": total_courses,
            "active": active_courses,
            "inactive": total_courses - active_courses
        },
        "enrollments": total_enrollments,
        "assignments": total_assignments,
        "submissions": total_submissions,
        "submission_rate": round((total_submissions / (total_assignments * total_enrollments) * 100) if (total_assignments * total_enrollments) > 0 else 0, 2)
    }


# ==================== EJECUTAR APLICACIÓN ====================

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload en desarrollo
        log_level="info"
    )