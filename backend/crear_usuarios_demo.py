# =================================================================
# SCRIPT: Crear 5 Estudiantes y 5 Profesores de Prueba
# =================================================================
import sys
import os
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal, engine, Base
from models import User, UserRole
from dependencies import get_password_hash


def create_tables():
    """Crea las tablas si no existen"""
    print("🛠️  Verificando/Creando tablas en la base de datos...")
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Tablas listas.")
        time.sleep(2)
    except Exception as e:
        print(f"⚠️  Advertencia al crear tablas: {e}")


def create_demo_teachers():
    """Crea 5 profesores de prueba"""
    db = None
    
    teachers_data = [
        {
            "username": "carlos.mendez",
            "email": "carlos.mendez@maruchan.edu",
            "password": "profesor123",
            "first_name": "Carlos",
            "last_name": "Méndez",
            "phone": "+506 8888-1001"
        },
        {
            "username": "ana.rodriguez",
            "email": "ana.rodriguez@maruchan.edu",
            "password": "profesor123",
            "first_name": "Ana",
            "last_name": "Rodríguez",
            "phone": "+506 8888-1002"
        },
        {
            "username": "luis.fernandez",
            "email": "luis.fernandez@maruchan.edu",
            "password": "profesor123",
            "first_name": "Luis",
            "last_name": "Fernández",
            "phone": "+506 8888-1003"
        },
        {
            "username": "maria.castro",
            "email": "maria.castro@maruchan.edu",
            "password": "profesor123",
            "first_name": "María",
            "last_name": "Castro",
            "phone": "+506 8888-1004"
        },
        {
            "username": "pedro.jimenez",
            "email": "pedro.jimenez@maruchan.edu",
            "password": "profesor123",
            "first_name": "Pedro",
            "last_name": "Jiménez",
            "phone": "+506 8888-1005"
        }
    ]
    
    try:
        db = SessionLocal()
        created_count = 0
        
        print("\n👨‍🏫 Creando Profesores...")
        print("-" * 50)
        
        for teacher_data in teachers_data:
            # Verificar si ya existe
            existing = db.query(User).filter(
                User.email == teacher_data["email"]
            ).first()
            
            if existing:
                print(f"   ⚠️  {teacher_data['email']} ya existe, omitiendo...")
                continue
            
            teacher = User(
                username=teacher_data["username"],
                email=teacher_data["email"],
                hashed_password=get_password_hash(teacher_data["password"]),
                role=UserRole.TEACHER,
                first_name=teacher_data["first_name"],
                last_name=teacher_data["last_name"],
                phone=teacher_data.get("phone"),
                is_active=True
            )
            
            db.add(teacher)
            created_count += 1
            print(f"   ✅ {teacher_data['first_name']} {teacher_data['last_name']} ({teacher_data['email']})")
        
        db.commit()
        print(f"\n   📊 Total profesores creados: {created_count}")
        
    except Exception as e:
        print(f"❌ Error creando profesores: {e}")
        if db:
            db.rollback()
    finally:
        if db:
            db.close()


def create_demo_students():
    """Crea 5 estudiantes de prueba"""
    db = None
    
    students_data = [
        {
            "username": "juan.perez",
            "email": "juan.perez@maruchan.edu",
            "password": "estudiante123",
            "first_name": "Juan",
            "last_name": "Pérez",
            "carnet": "2024-0001",
            "phone": "+506 7777-2001"
        },
        {
            "username": "sofia.mora",
            "email": "sofia.mora@maruchan.edu",
            "password": "estudiante123",
            "first_name": "Sofía",
            "last_name": "Mora",
            "carnet": "2024-0002",
            "phone": "+506 7777-2002"
        },
        {
            "username": "diego.vargas",
            "email": "diego.vargas@maruchan.edu",
            "password": "estudiante123",
            "first_name": "Diego",
            "last_name": "Vargas",
            "carnet": "2024-0003",
            "phone": "+506 7777-2003"
        },
        {
            "username": "valentina.ruiz",
            "email": "valentina.ruiz@maruchan.edu",
            "password": "estudiante123",
            "first_name": "Valentina",
            "last_name": "Ruiz",
            "carnet": "2024-0004",
            "phone": "+506 7777-2004"
        },
        {
            "username": "mateo.sanchez",
            "email": "mateo.sanchez@maruchan.edu",
            "password": "estudiante123",
            "first_name": "Mateo",
            "last_name": "Sánchez",
            "carnet": "2024-0005",
            "phone": "+506 7777-2005"
        }
    ]
    
    try:
        db = SessionLocal()
        created_count = 0
        
        print("\n👨‍🎓 Creando Estudiantes...")
        print("-" * 50)
        
        for student_data in students_data:
            # Verificar si ya existe
            existing = db.query(User).filter(
                User.email == student_data["email"]
            ).first()
            
            if existing:
                print(f"   ⚠️  {student_data['email']} ya existe, omitiendo...")
                continue
            
            student = User(
                username=student_data["username"],
                email=student_data["email"],
                hashed_password=get_password_hash(student_data["password"]),
                role=UserRole.STUDENT,
                first_name=student_data["first_name"],
                last_name=student_data["last_name"],
                carnet=student_data.get("carnet"),
                phone=student_data.get("phone"),
                is_active=True
            )
            
            db.add(student)
            created_count += 1
            print(f"   ✅ {student_data['first_name']} {student_data['last_name']} ({student_data['carnet']})")
        
        db.commit()
        print(f"\n   📊 Total estudiantes creados: {created_count}")
        
    except Exception as e:
        print(f"❌ Error creando estudiantes: {e}")
        if db:
            db.rollback()
    finally:
        if db:
            db.close()


def show_summary():
    """Muestra un resumen de las credenciales creadas"""
    print("\n" + "=" * 60)
    print("📋 RESUMEN DE USUARIOS CREADOS")
    print("=" * 60)
    
    print("\n👨‍🏫 PROFESORES (Contraseña: profesor123)")
    print("-" * 50)
    print("   • carlos.mendez@maruchan.edu")
    print("   • ana.rodriguez@maruchan.edu")
    print("   • luis.fernandez@maruchan.edu")
    print("   • maria.castro@maruchan.edu")
    print("   • pedro.jimenez@maruchan.edu")
    
    print("\n👨‍🎓 ESTUDIANTES (Contraseña: estudiante123)")
    print("-" * 50)
    print("   • juan.perez@maruchan.edu      (Carnet: 2024-0001)")
    print("   • sofia.mora@maruchan.edu      (Carnet: 2024-0002)")
    print("   • diego.vargas@maruchan.edu    (Carnet: 2024-0003)")
    print("   • valentina.ruiz@maruchan.edu  (Carnet: 2024-0004)")
    print("   • mateo.sanchez@maruchan.edu   (Carnet: 2024-0005)")
    
    print("\n" + "=" * 60)
    print("⚠️  IMPORTANTE: Cambia las contraseñas en producción")
    print("=" * 60)


# =================================================================
# ENTRY POINT
# =================================================================
if __name__ == "__main__":
    print("🎓 Maruchan University - Creación de Usuarios Demo")
    print("=" * 60)
    
    # Verificar tablas
    create_tables()
    
    # Crear profesores
    create_demo_teachers()
    
    # Crear estudiantes
    create_demo_students()
    
    # Mostrar resumen
    show_summary()
    
    print("\n🚀 ¡Usuarios demo listos para usar!")
