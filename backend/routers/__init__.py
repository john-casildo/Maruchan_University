# Este archivo permite importar los routers como módulo
from . import users, courses, enrollments, assignments, submissions, materials

__all__ = [
    "users",
    "courses", 
    "enrollments",
    "assignments",
    "submissions",
    "materials"
]