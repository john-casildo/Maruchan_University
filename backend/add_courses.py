from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models import Course, User, UserRole, CourseStatus
from datetime import date, timedelta
import random

def create_sample_courses():
    db = SessionLocal()
    try:
        # 1. Buscar un profesor o admin
        teacher = db.query(User).filter(
            (User.role == UserRole.TEACHER) | (User.role == UserRole.ADMIN)
        ).first()
        
        if not teacher:
            print("❌ No se encontró ningún profesor o administrador para asignar los cursos.")
            return

        print(f"👨‍🏫 Asignando cursos al usuario: {teacher.username} ({teacher.role.value})")

        # 2. Lista de cursos a crear
        courses_data = [
            {
                "title": "Introducción a la Programación",
                "code": "PROG101",
                "description": "Fundamentos de lógica de programación y algoritmos con Python.",
                "credits": 4,
                "semester": 1,
                "schedule": "Lun/Mie 08:00 - 10:00",
                "classroom": "Lab A1",
                "max_students": 30
            },
            {
                "title": "Base de Datos I",
                "code": "DB101",
                "description": "Diseño y gestión de bases de datos relacionales con SQL.",
                "credits": 3,
                "semester": 2,
                "schedule": "Mar/Jue 10:00 - 12:00",
                "classroom": "Lab B2",
                "max_students": 25
            },
            {
                "title": "Desarrollo Web Frontend",
                "code": "WEB201",
                "description": "Creación de interfaces modernas con HTML, CSS, JavaScript y React.",
                "credits": 4,
                "semester": 3,
                "schedule": "Lun/Mie 14:00 - 16:00",
                "classroom": "Lab C1",
                "max_students": 30
            },
            {
                "title": "Estructura de Datos",
                "code": "PROG201",
                "description": "Estudio de estructuras de datos lineales y no lineales.",
                "credits": 4,
                "semester": 2,
                "schedule": "Vie 08:00 - 12:00",
                "classroom": "Aula 101",
                "max_students": 40
            },
            {
                "title": "Ingeniería de Software",
                "code": "SOFT301",
                "description": "Metodologías de desarrollo, ciclo de vida del software y gestión de proyectos.",
                "credits": 3,
                "semester": 4,
                "schedule": "Mar/Jue 16:00 - 18:00",
                "classroom": "Aula 202",
                "max_students": 35
            }
        ]

        count = 0
        for data in courses_data:
            # Verificar si ya existe
            existing = db.query(Course).filter(Course.code == data["code"]).first()
            if existing:
                print(f"⚠️ El curso {data['code']} ya existe. Saltando...")
                continue

            new_course = Course(
                **data,
                teacher_id=teacher.id,
                status=CourseStatus.ACTIVE,
                start_date=date.today(),
                end_date=date.today() + timedelta(days=120)
            )
            db.add(new_course)
            count += 1
        
        db.commit()
        print(f"✅ Se han creado {count} cursos exitosamente.")

    except Exception as e:
        print(f"❌ Error al crear cursos: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_sample_courses()
