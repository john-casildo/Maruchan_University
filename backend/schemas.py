from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime, date
from typing import Optional, List
from enum import Enum


# ==================== ENUMS ====================

class UserRoleEnum(str, Enum):
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"


class CourseStatusEnum(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    COMPLETED = "completed"


class EnrollmentStatusEnum(str, Enum):
    ENROLLED = "enrolled"
    DROPPED = "dropped"
    COMPLETED = "completed"


class AttendanceStatusEnum(str, Enum):
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"
    EXCUSED = "excused"


class MaterialTypeEnum(str, Enum):
    PDF = "pdf"
    VIDEO = "video"
    SLIDE = "slide"
    DOCUMENT = "document"
    LINK = "link"
    OTHER = "other"


# ==================== CARRERA SCHEMAS ====================

class CarreraBase(BaseModel):
    name: str = Field(..., max_length=200)
    description: Optional[str] = None
    duration_years: int = Field(default=4, ge=1, le=10)


class CarreraCreate(CarreraBase):
    pass


class CarreraUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    duration_years: Optional[int] = Field(None, ge=1, le=10)


class CarreraResponse(CarreraBase):
    id: int
    created_at: datetime
    students_count: Optional[int] = 0
    courses_count: Optional[int] = 0
    
    class Config:
        from_attributes = True


class CarreraList(BaseModel):
    id: int
    name: str
    
    class Config:
        from_attributes = True


# ==================== USER SCHEMAS ====================

class UserBase(BaseModel):
    email: EmailStr
    role: UserRoleEnum = UserRoleEnum.STUDENT
    first_name: str = Field(..., max_length=100)
    middle_name: Optional[str] = Field(None, max_length=100)
    last_name: str = Field(..., max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    carnet: Optional[str] = Field(None, max_length=50)
    carrera_id: Optional[int] = None
    birtdate: Optional[date] = None
    profile_pic_url: Optional[str] = None


class UserCreate(UserBase):
    username: str = Field(..., min_length=3, max_length=150)
    password: str = Field(..., min_length=8)
    password_confirm: str
    
    @validator('password_confirm')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('Las contraseñas no coinciden')
        return v


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = Field(None, max_length=100)
    middle_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    profile_pic_url: Optional[str] = None
    birtdate: Optional[date] = None
    carrera_id: Optional[int] = None


class UserResponse(UserBase):
    id: int
    username: str
    carrera: Optional[CarreraList] = None
    joined_date: datetime
    last_login: datetime
    is_active: bool
    full_name: Optional[str] = None
    
    class Config:
        from_attributes = True


class UserList(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role: UserRoleEnum
    carnet: Optional[str]
    is_active: bool
    
    class Config:
        from_attributes = True


class TeacherResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr
    profile_pic_url: Optional[str]
    courses_count: Optional[int] = 0
    
    class Config:
        from_attributes = True


# ==================== COURSE SCHEMAS ====================

class CourseBase(BaseModel):
    title: str = Field(..., max_length=200)
    description: Optional[str] = None
    code: str = Field(..., max_length=20)
    credits: int = Field(default=3, ge=1, le=10)
    semester: int = Field(..., ge=1, le=10)
    schedule: Optional[str] = Field(None, max_length=200)
    classroom: Optional[str] = Field(None, max_length=50)
    max_students: int = Field(default=30, ge=1)
    teacher_id: int
    carrera_id: Optional[int] = None
    start_date: date
    end_date: date


class CourseCreate(CourseBase):
    pass


class CourseUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    credits: Optional[int] = Field(None, ge=1, le=10)
    semester: Optional[int] = Field(None, ge=1, le=10)
    schedule: Optional[str] = Field(None, max_length=200)
    classroom: Optional[str] = Field(None, max_length=50)
    max_students: Optional[int] = Field(None, ge=1)
    teacher_id: Optional[int] = None
    status: Optional[CourseStatusEnum] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class CourseResponse(CourseBase):
    id: int
    teacher: TeacherResponse
    carrera: Optional[CarreraList] = None
    status: CourseStatusEnum
    enrolled_count: int = 0
    is_full: bool = False
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CourseList(BaseModel):
    id: int
    code: str
    title: str
    teacher_name: str
    teacher_id: int
    semester: int
    credits: int
    enrolled_count: int = 0
    status: CourseStatusEnum
    
    class Config:
        from_attributes = True


# ==================== ENROLLMENT SCHEMAS ====================

class EnrollmentBase(BaseModel):
    student_id: int
    course_id: int


class EnrollmentCreate(EnrollmentBase):
    pass


class EnrollmentUpdate(BaseModel):
    status: Optional[EnrollmentStatusEnum] = None
    grade: Optional[float] = Field(None, ge=0, le=100)


class EnrollmentResponse(EnrollmentBase):
    id: int
    student: UserList
    course: CourseList
    status: EnrollmentStatusEnum
    grade: Optional[float]
    enrolled_at: datetime
    status_update_date: datetime
    grade_assigned_date: Optional[datetime]
    
    class Config:
        from_attributes = True


class EnrollmentGrade(BaseModel):
    grade: float = Field(..., ge=0, le=100)


# ==================== ASSIGNMENT SCHEMAS ====================

class AssignmentBase(BaseModel):
    course_id: int
    title: str = Field(..., max_length=200)
    description: Optional[str] = None
    due_date: datetime
    attachment_path: Optional[str] = Field(None, max_length=500)
    max_score: float = Field(default=100.0, ge=0)
    weight: float = Field(default=1.0, ge=0)
    is_published: bool = True


class AssignmentCreate(AssignmentBase):
    pass


class AssignmentUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    attachment_path: Optional[str] = Field(None, max_length=500)
    max_score: Optional[float] = Field(None, ge=0)
    weight: Optional[float] = Field(None, ge=0)
    is_published: Optional[bool] = None


class AssignmentResponse(AssignmentBase):
    id: int
    course: CourseList
    is_overdue: bool = False
    submissions_count: int = 0
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class AssignmentList(BaseModel):
    id: int
    title: str
    course_code: str
    due_date: datetime
    max_score: float
    is_overdue: bool
    is_published: bool
    
    class Config:
        from_attributes = True


# ==================== SUBMISSION SCHEMAS ====================

class SubmissionBase(BaseModel):
    assignment_id: int
    student_id: int
    file_path: str = Field(..., max_length=500)


class SubmissionCreate(SubmissionBase):
    pass


class SubmissionUpdate(BaseModel):
    file_path: Optional[str] = Field(None, max_length=500)


class SubmissionGrade(BaseModel):
    grade: float = Field(..., ge=0)
    feedback_char: Optional[str] = None
    graded_by_id: int


class SubmissionResponse(SubmissionBase):
    id: int
    student: UserList
    assignment: AssignmentList
    submitted_at_date: datetime
    late: bool
    grade: Optional[float]
    feedback_char: Optional[str]
    graded_at: Optional[datetime]
    graded_by_name: Optional[str]
    
    class Config:
        from_attributes = True


# ==================== COURSE MATERIAL SCHEMAS ====================

class CourseMaterialBase(BaseModel):
    course_id: int
    title: str = Field(..., max_length=200)
    description: Optional[str] = None
    file_path: Optional[str] = Field(None, max_length=500)
    type: MaterialTypeEnum = MaterialTypeEnum.DOCUMENT
    is_visible: bool = True
    order: int = 0


class CourseMaterialCreate(CourseMaterialBase):
    uploaded_by_id: Optional[int] = None


class CourseMaterialUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    file_path: Optional[str] = Field(None, max_length=500)
    type: Optional[MaterialTypeEnum] = None
    is_visible: Optional[bool] = None
    order: Optional[int] = None


class CourseMaterialResponse(CourseMaterialBase):
    id: int
    course: CourseList
    uploaded_at: datetime
    uploaded_by_name: Optional[str]
    
    class Config:
        from_attributes = True


# ==================== ANNOUNCEMENT SCHEMAS ====================

class AnnouncementBase(BaseModel):
    course_id: int
    title: str = Field(..., max_length=200)
    content: str
    is_pinned: bool = False


class AnnouncementCreate(AnnouncementBase):
    author_id: int


class AnnouncementUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    content: Optional[str] = None
    is_pinned: Optional[bool] = None


class AnnouncementResponse(AnnouncementBase):
    id: int
    author: UserList
    course: CourseList
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== ATTENDANCE SCHEMAS ====================

class AttendanceBase(BaseModel):
    enrollment_id: int
    date: date
    status: AttendanceStatusEnum = AttendanceStatusEnum.PRESENT
    notes: Optional[str] = None


class AttendanceCreate(AttendanceBase):
    recorded_by_id: Optional[int] = None


class AttendanceUpdate(BaseModel):
    status: Optional[AttendanceStatusEnum] = None
    notes: Optional[str] = None


class AttendanceResponse(AttendanceBase):
    id: int
    student_name: str
    course_code: str
    recorded_by_name: Optional[str]
    recorded_at: datetime
    
    class Config:
        from_attributes = True


class AttendanceList(BaseModel):
    id: int
    enrollment_id: int
    student_name: str
    date: date
    status: AttendanceStatusEnum
    
    class Config:
        from_attributes = True


# ==================== BULK OPERATIONS ====================

class BulkAttendanceCreate(BaseModel):
    course_id: int
    date: date
    attendances: List[dict]  # [{enrollment_id: int, status: str}]
    recorded_by_id: int


# ==================== AUTH SCHEMAS ====================

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Optional[int] = None
    username: Optional[str] = None
    role: Optional[str] = None


class LoginRequest(BaseModel):
    username: str
    password: str


# ==================== STATS SCHEMAS ====================

class CourseStats(BaseModel):
    total_students: int
    total_assignments: int
    total_submissions: int
    average_grade: float
    completion_rate: float


class StudentStats(BaseModel):
    enrolled_courses: int
    completed_assignments: int
    pending_assignments: int
    average_grade: float
    attendance_rate: float


# ==================== RESPONSE WRAPPERS ====================

class PaginatedResponse(BaseModel):
    items: List[dict]
    total: int
    page: int
    page_size: int
    pages: int


class MessageResponse(BaseModel):
    message: str
    success: bool = True
    
    
# ==================== MESSAGE SCHEMAS ====================

class MessageCreate(BaseModel):
    receiver_id: int
    content: str

class ChatMessageResponse(BaseModel):
    id: int
    sender_id: int
    sender_name: str
    receiver_id: int
    content: str
    timestamp: datetime
    
    class Config:
        from_attributes = True
        
# ==================== USER PASSWORD UPDATE SCHEMA ====================        
class UserPasswordUpdate(BaseModel):
    password: str = Field(..., min_length=8)
    password_confirm: str

    @validator('password_confirm')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('Las contraseñas no coinciden')
        return v