# =================================================================
# 1. IMPORTS
# =================================================================
import sys
import os
import time
# Agregamos el directorio actual al path para evitar errores de importación
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime
# CRÍTICO: Asegúrate de importar SessionLocal, engine, y Base
from database import SessionLocal, engine, Base 
from models import User, UserRole
from dependencies import get_password_hash 


# =================================================================
# 2. FUNCIÓN DE CREACIÓN DE TABLAS (Se llama ANTES que cualquier consulta)
# =================================================================
def create_tables():
    """Crea las tablas si no existen (Soluciona el error UndefinedTable)"""
    print("🛠️  Verificando/Creando tablas en la base de datos...")
    try:
        # ESTA ES LA LÍNEA MÁGICA
        Base.metadata.create_all(bind=engine)
        print("✅ Tablas listas.")
        
        # 💥 AÑADIMOS UNA PEQUEÑA PAUSA 💥
        print("⏳ Esperando 3 segundos para sincronización de DB...")
        time.sleep(3) 
        
    except Exception as e:
        print(f"⚠️  Advertencia al crear tablas: {e}") 
        print("   (Esto es normal si el contenedor DB aún está despertando).")


# =================================================================
# 3. FUNCIÓN PRINCIPAL DE CREACIÓN DE ADMIN (TU CÓDIGO)
# =================================================================
def create_admin_user():
    # 1. Inicializar la variable db
    db = None 
    
    try:
        # 2. Asignar la sesión dentro del try
        db = SessionLocal() 

        # Verificar si ya existe un admin (esto consulta la DB)
        existing_admin = db.query(User).filter(
            User.email == "admin@maruchan.edu"
        ).first()
        
        if existing_admin:
                print("⚠️  Usuario admin ya existe")
                print(f"   Email: {existing_admin.email}")
                print(f"   Username: {existing_admin.username}")
                return
        
        # Crear usuario admin
        print("PTR: Creando usuario admin...")
        admin = User(
            username="admin",
            email="admin@maruchan.edu",
            hashed_password=get_password_hash("admin123"),
            role=UserRole.ADMIN, # Asegúrate que tu modelo User acepte este Enum o string
            first_name="Super",
            last_name="Administrador",
            # middle_name="", # Descomenta si tu base de datos tiene este campo
            is_active=True,
            # joined_date=datetime.utcnow() # Descomenta si tu modelo tiene este campo
        )

        db.add(admin)
        db.commit()

        print("=" * 60)
        print("✅ Usuario administrador creado exitosamente!")
        print("=" * 60)
        print(f"📧 Email: admin@maruchan.edu")
        print(f"👤 Username: admin")
        print(f"🔑 Password: admin123")
        print("=" * 60)
        print("⚠️  IMPORTANTE: Cambia la contraseña después del primer login")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error creando admin: {e}")
        # Si hubo un error en la transacción, hacemos rollback (solo si db existe)
        if db:
            db.rollback() 
    
    finally:
        # 3. Solo cerrar la sesión si fue abierta correctamente
        if db:
            db.close()


def create_demo_users():
    # 1. Inicializar la variable db
    db = None 
    
    try:
        # 2. Asignar la sesión dentro del try
        db = SessionLocal()

        # Profesor
        teacher = User(
            username="profesor1",
            email="profesor@maruchan.edu",
            hashed_password=get_password_hash("profesor123"),
            role=UserRole.TEACHER,
            first_name="Juan",
            last_name="Pérez",
            is_active=True
        )
        
        # Estudiante
        student = User(
            username="estudiante1",
            email="estudiante@maruchan.edu",
            hashed_password=get_password_hash("estudiante123"),
            role=UserRole.STUDENT,
            first_name="María",
            last_name="González",
            # carnet="2024-001", # Descomenta si tu modelo tiene campo carnet
            is_active=True
        )
        
        db.add(teacher)
        db.add(student)
        db.commit()
        
        print("\n✅ Usuarios de prueba creados:")
        print("   👨‍🏫 Profesor: profesor@maruchan.edu / profesor123")
        print("   👨‍🎓 Estudiante: estudiante@maruchan.edu / estudiante123")

    except Exception as e:
        print(f"⚠️  Error creando usuarios demo: {e}")
        # Si hubo un error en la transacción, hacemos rollback (solo si db existe)
        if db:
            db.rollback()
    
    finally:
        # 3. Solo cerrar la sesión si fue abierta correctamente
        if db:
            db.close()

# =================================================================
# 4. ENTRY POINT (Orden de Ejecución)
# =================================================================
if __name__ == "__main__":
    print("🎓 Maruchan University - Setup Inicial")
    print("=" * 60)
    
    # 💥 ESTO DEBE SER LA PRIMERA LLAMADA DENTRO DEL BLOQUE 💥
    create_tables()

    # Ahora sí, podemos consultar la DB
    create_admin_user()
    
    create_demo_users() # (Si tienes la función, la llamas aquí)
    
    print("\n🚀 Listo para usar el sistema!")