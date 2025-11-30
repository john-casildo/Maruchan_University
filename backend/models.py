from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Date, 
    Float, Text, ForeignKey, Enum, UniqueConstraint, Index
)
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from database import Base


# ==================== ENUMS ====================

class UserRole(str, enum.Enum):
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"


class CourseStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    COMPLETED = "completed"


class EnrollmentStatus(str, enum.Enum):
    ENROLLED = "enrolled"
    DROPPED = "dropped"
    COMPLETED = "completed"


class AttendanceStatus(str, enum.Enum):
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"
    EXCUSED = "excused"


class MaterialType(str, enum.Enum):
    PDF = "pdf"
    VIDEO = "video"
    SLIDE = "slide"
    DOCUMENT = "document"
    LINK = "link"
    OTHER = "other"


# ==================== MODELS ====================

class Carrera(Base):
    __tablename__ = "carreras"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    duration_years = Column(Integer, default=4)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones
    students = relationship("User", back_populates="carrera", foreign_keys="User.carrera_id")
    courses = relationship("Course", back_populates="carrera")
    
    def __repr__(self):
        return f"<Carrera {self.name}>"


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(150), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.STUDENT, nullable=False, index=True)
    
    # Información personal
    first_name = Column(String(100), nullable=False)
    middle_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    carnet = Column(String(50), unique=True, nullable=True, index=True)
    profile_pic_url = Column(String(500), nullable=True)
    birtdate = Column(Date, nullable=True)
    
    # Relaciones
    carrera_id = Column(Integer, ForeignKey("carreras.id"), nullable=True)
    carrera = relationship("Carrera", back_populates="students", foreign_keys=[carrera_id])
    
    # Timestamps
    joined_date = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relaciones inversas
    courses_taught = relationship("Course", back_populates="teacher")
    enrollments = relationship("Enrollment", back_populates="student")
    submissions = relationship("Submission", back_populates="student", foreign_keys="Submission.student_id")
    graded_submissions = relationship("Submission", back_populates="graded_by", foreign_keys="Submission.graded_by_id")
    uploaded_materials = relationship("CourseMaterial", back_populates="uploaded_by")
    announcements = relationship("Announcement", back_populates="author")
    recorded_attendances = relationship("Attendance", back_populates="recorded_by")
    
    __table_args__ = (
        Index('idx_user_email', 'email'),
        Index('idx_user_carnet', 'carnet'),
        Index('idx_user_role', 'role'),
    )
    
    def __repr__(self):
        return f"<User {self.first_name} {self.last_name} ({self.role.value})>"
    
    @property
    def full_name(self):
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"


class Course(Base):
    __tablename__ = "courses"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    code = Column(String(20), unique=True, nullable=False, index=True)
    
    # Configuración académica
    credits = Column(Integer, default=3, nullable=False)
    semester = Column(Integer, nullable=False)
    schedule = Column(String(200), nullable=True)
    classroom = Column(String(50), nullable=True)
    max_students = Column(Integer, default=30)
    
    # Relaciones
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    teacher = relationship("User", back_populates="courses_taught")
    
    carrera_id = Column(Integer, ForeignKey("carreras.id"), nullable=True)
    carrera = relationship("Carrera", back_populates="courses")
    
    # Estado y fechas
    status = Column(Enum(CourseStatus), default=CourseStatus.ACTIVE, nullable=False, index=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones inversas
    enrollments = relationship("Enrollment", back_populates="course", cascade="all, delete-orphan")
    assignments = relationship("Assignment", back_populates="course", cascade="all, delete-orphan")
    materials = relationship("CourseMaterial", back_populates="course", cascade="all, delete-orphan")
    announcements = relationship("Announcement", back_populates="course", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_course_code', 'code'),
        Index('idx_course_teacher', 'teacher_id'),
        Index('idx_course_status', 'status'),
    )
    
    def __repr__(self):
        return f"<Course {self.code} - {self.title}>"
    
    @property
    def is_full(self):
        enrolled = sum(1 for e in self.enrollments if e.status == EnrollmentStatus.ENROLLED)
        return enrolled >= self.max_students


class Enrollment(Base):
    __tablename__ = "enrollments"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Relaciones
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    student = relationship("User", back_populates="enrollments")
    
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    course = relationship("Course", back_populates="enrollments")
    
    joined_id = Column(Integer, ForeignKey("enrollments.id"), nullable=True)
    
    # Estado y calificación
    status = Column(Enum(EnrollmentStatus), default=EnrollmentStatus.ENROLLED, nullable=False)
    grade = Column(Float, nullable=True)
    
    # Timestamps
    enrolled_at = Column(DateTime, default=datetime.utcnow)
    status_update_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    grade_assigned_date = Column(DateTime, nullable=True)
    
    # Relaciones inversas
    attendances = relationship("Attendance", back_populates="enrollment", cascade="all, delete-orphan")
    
    __table_args__ = (
        UniqueConstraint('student_id', 'course_id', name='uq_student_course'),
        Index('idx_enrollment_student_status', 'student_id', 'status'),
        Index('idx_enrollment_course_status', 'course_id', 'status'),
    )
    
    def __repr__(self):
        return f"<Enrollment {self.student.full_name} - {self.course.code}>"


class Assignment(Base):
    __tablename__ = "assignments"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Relación con curso
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    course = relationship("Course", back_populates="assignments")
    
    # Información de la asignación
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    due_date = Column(DateTime, nullable=False)
    attachment_path = Column(String(500), nullable=True)
    
    # Calificación
    max_score = Column(Float, default=100.0)
    weight = Column(Float, default=1.0)
    
    # Estado
    is_published = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones inversas
    submissions = relationship("Submission", back_populates="assignment", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_assignment_course_due', 'course_id', 'due_date'),
        Index('idx_assignment_published', 'is_published'),
    )
    
    def __repr__(self):
        return f"<Assignment {self.course.code} - {self.title}>"
    
    @property
    def is_overdue(self):
        return datetime.utcnow() > self.due_date


class Submission(Base):
    __tablename__ = "submissions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Relaciones
    assignment_id = Column(Integer, ForeignKey("assignments.id"), nullable=False)
    assignment = relationship("Assignment", back_populates="submissions")
    
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    student = relationship("User", back_populates="submissions", foreign_keys=[student_id])
    
    # Información de la entrega
    file_path = Column(String(500), nullable=False)
    submitted_at_date = Column(DateTime, default=datetime.utcnow)
    late = Column(Boolean, default=False, index=True)
    
    # Calificación
    grade = Column(Float, nullable=True)
    feedback_char = Column(Text, nullable=True)
    graded_at = Column(DateTime, nullable=True)
    
    graded_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    graded_by = relationship("User", back_populates="graded_submissions", foreign_keys=[graded_by_id])
    
    __table_args__ = (
        UniqueConstraint('assignment_id', 'student_id', name='uq_assignment_student'),
        Index('idx_submission_assignment_student', 'assignment_id', 'student_id'),
        Index('idx_submission_late', 'late'),
    )
    
    def __repr__(self):
        return f"<Submission {self.student.full_name} - {self.assignment.title}>"


class CourseMaterial(Base):
    __tablename__ = "course_materials"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Relación con curso
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    course = relationship("Course", back_populates="materials")
    
    # Información del material
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    file_path = Column(String(500), nullable=True)
    type = Column(Enum(MaterialType), default=MaterialType.DOCUMENT)
    
    # Metadatos
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    uploaded_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    uploaded_by = relationship("User", back_populates="uploaded_materials")
    
    is_visible = Column(Boolean, default=True)
    order = Column(Integer, default=0)
    
    __table_args__ = (
        Index('idx_material_course_visible', 'course_id', 'is_visible'),
    )
    
    def __repr__(self):
        return f"<CourseMaterial {self.course.code} - {self.title}>"


class Announcement(Base):
    __tablename__ = "announcements"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Relación con curso
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    course = relationship("Course", back_populates="announcements")
    
    # Contenido
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    
    # Autor
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    author = relationship("User", back_populates="announcements")
    
    # Estado
    is_pinned = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Announcement {self.course.code} - {self.title}>"


class Attendance(Base):
    __tablename__ = "attendance"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Relación con inscripción
    enrollment_id = Column(Integer, ForeignKey("enrollments.id"), nullable=False)
    enrollment = relationship("Enrollment", back_populates="attendances")
    
    # Información de asistencia
    date = Column(Date, nullable=False)
    status = Column(Enum(AttendanceStatus), default=AttendanceStatus.PRESENT)
    notes = Column(Text, nullable=True)
    
    # Quién registró
    recorded_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    recorded_by = relationship("User", back_populates="recorded_attendances")
    recorded_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        UniqueConstraint('enrollment_id', 'date', name='uq_enrollment_date'),
    )
    
    def __repr__(self):
        return f"<Attendance {self.enrollment.student.full_name} - {self.date}>"
    
# ==================== Mensajería ====================
class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    is_read = Column(Boolean, default=False)

    # Relaciones
    sender = relationship("User", foreign_keys=[sender_id], backref="sent_messages")
    receiver = relationship("User", foreign_keys=[receiver_id], backref="received_messages")
    
