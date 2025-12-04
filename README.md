# 🎓 Maruchan University - Sistema de Gestión Universitaria

Sistema completo de gestión académica con FastAPI, PostgreSQL y Streamlit en Docker.

## 🏗️ Arquitectura

```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│   Frontend      │─────▶│   Backend       │─────▶│   Database      │
│   Streamlit     │      │   FastAPI       │      │   PostgreSQL    │
│   :8501         │      │   :8000         │      │   :5432         │
└─────────────────┘      └─────────────────┘      └─────────────────┘
                                │
                                ▼
                         ┌─────────────────┐
                         │  File Storage   │
                         │  Docker Volume  │
                         └─────────────────┘
```

## ✨ Características Principales

### 👥 Roles de Usuario
- **🛡️ Administrador:** Gestión total de usuarios, cursos y sistema.
- **👨‍🏫 Profesor:** Gestión de cursos asignados, creación/edición de tareas, calificación y feedback.
- **🎓 Estudiante:** Inscripción a cursos, envío de tareas, visualización de notas, comunidad.

### 📚 Gestión Académica
- **Cursos:** Creación, edición y asignación de profesores.
- **Inscripciones:** Control de estudiantes matriculados por curso.
- **Tareas:** Creación y edición completa de asignaciones (título, descripción, fecha, puntos, peso, publicación).
- **Entregas:** Subida de archivos, control de entregas tardías.
- **Calificaciones:** Sistema de notas con feedback detallado.

### 🛠️ Funcionalidades Técnicas
- **Autenticación:** JWT seguro con roles y permisos.
- **Archivos:** Subida y descarga directa de archivos (tareas/materiales/fotos de perfil).
- **Notificaciones:** Mensajes flash (toasts) para feedback inmediato.
- **Interfaz:** UI moderna y responsiva con gradientes, animaciones y diseño por roles.

---

## 🚀 Actualización v3.0 (Diciembre 2025)

### 🎨 1. Interfaz Renovada por Roles
Cada rol tiene su propia interfaz optimizada con estética moderna:

**Portal de Estudiantes (`student_app.py`):**
- Dashboard personalizado con estadísticas
- Mis Cursos con información detallada
- Tareas con subida de archivos
- Calificaciones y feedback
- Comunidad (Chat)
- Perfil editable

**Portal de Profesores/Admin (`app.py`):**
- Dashboard con métricas visuales
- Gestión de cursos con tabs organizados
- **Gestión completa de tareas** (crear, editar, eliminar)
- Calificación de entregas con popover
- Comunidad (Chat) con indicadores de estado
- Perfil con tabs de seguridad

### ✏️ 2. Edición Completa de Tareas (Profesores)
Los profesores ahora pueden editar TODOS los campos de una tarea después de crearla:
- 📌 Título
- 📋 Descripción
- 📅 Fecha y hora de entrega
- 🎯 Puntos máximos
- ⚖️ Peso en nota final
- 🌐 Estado de publicación (publicada/borrador)
- 🗑️ Eliminación con confirmación

### 💬 3. Módulo de Comunidad (Chat)
Sistema de comunicación entre usuarios:
- **Mensajería:** Envío y recepción de mensajes entre todos los roles.
- **Estado de Actividad:** Indicadores 🟢 En línea / ⚪ Desconectado.
- **Estadísticas:** Contadores de usuarios en línea y total.
- **Auto-refresco:** Actualización automática cada 3 segundos.

### 🎯 4. Sistema de Botones por Color
- 🔴 **Rojo:** Acciones destructivas (Eliminar, Cerrar Sesión)
- 🟢 **Verde:** Acciones positivas (Guardar, Crear, Inscribir)
- 🔵 **Azul:** Acciones generales (Navegar, Filtrar)

### 📊 5. Dashboards Diferenciados
Cada rol ve información relevante:
- **Admin:** Total usuarios, cursos, tareas, entregas, usuarios activos
- **Profesor:** Mis cursos, mis estudiantes, tareas creadas, próximas entregas
- **Estudiante:** Cursos inscritos, tareas pendientes, calificaciones

---

## 🚀 Inicio Rápido con Docker

### 1. Clonar el repositorio

```bash
git clone <tu-repositorio>
cd Maruchan_University
```

### 2. Construir y levantar los contenedores

```bash
# Levantar todos los servicios
docker-compose up -d

# Ver logs
docker-compose logs -f

# Ver estado
docker-compose ps
```

### 3. Aplicar migraciones

```bash
docker-compose exec backend alembic upgrade head
```

### 4. Crear usuario administrador

```bash
docker-compose exec backend python crear_admin.py
```

**Credenciales iniciales:**
- 📧 **Email:** admin@maruchan.edu
- 🔑 **Password:** admin123

### 5. (Opcional) Crear usuarios de demo

```bash
docker-compose exec backend python crear_usuarios_demo.py
```

### 6. Acceder a las aplicaciones

| Servicio | URL | Descripción |
|----------|-----|-------------|
| 🎨 Frontend | http://localhost:8501 | Aplicación principal |
| 📡 API | http://localhost:8000 | Backend FastAPI |
| 📚 API Docs | http://localhost:8000/docs | Documentación Swagger |

---

## 📁 Estructura del Proyecto

```
Maruchan_University/
├── docker-compose.yml          # Orquestación de contenedores
├── init-db.sh                  # Script de inicialización DB
├── setup-migrations.sh         # Script de migraciones
├── README.md                   # Este archivo
│
├── backend/                    # API FastAPI
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py                 # Punto de entrada
│   ├── database.py             # Conexión a PostgreSQL
│   ├── models.py               # Modelos SQLAlchemy
│   ├── schemas.py              # Schemas Pydantic
│   ├── dependencies.py         # Dependencias de autenticación
│   ├── crear_admin.py          # Script crear admin
│   ├── crear_usuarios_demo.py  # Script usuarios de prueba
│   ├── reset_admin_password.py # Reset de contraseña
│   │
│   ├── routers/
│   │   ├── users.py            # CRUD usuarios + perfiles
│   │   ├── courses.py          # CRUD cursos
│   │   ├── enrollments.py      # Inscripciones
│   │   ├── assignments.py      # Tareas (CRUD completo)
│   │   ├── submissions.py      # Entregas + calificaciones
│   │   ├── materials.py        # Materiales de curso
│   │   └── chat.py             # Sistema de mensajería
│   │
│   ├── alembic/                # Migraciones de DB
│   │   └── versions/
│   │
│   └── maruchan_storage/       # Almacenamiento de archivos
│       ├── submissions/
│       ├── materials/
│       └── profiles/
│
└── frontend/                   # App Streamlit
    ├── Dockerfile
    ├── requirements.txt
    ├── app.py                  # Portal Admin/Profesor
    ├── student_app.py          # Portal Estudiante
    ├── utils.py                # Utilidades compartidas
    │
    ├── student_pages/          # Páginas del estudiante
    │   ├── dashboard.py
    │   ├── courses.py
    │   ├── assignments.py
    │   ├── grades.py
    │   ├── community.py        # Chat
    │   └── profile.py
    │
    └── .streamlit/
        └── config.toml
```

---

## 🐳 Comandos Docker Útiles

### Gestión de Contenedores

```bash
# Iniciar servicios
docker-compose up -d

# Detener servicios
docker-compose down

# Reiniciar un servicio específico
docker-compose restart backend
docker-compose restart frontend

# Ver logs en tiempo real
docker-compose logs -f backend

# Ejecutar comando en contenedor
docker-compose exec backend python crear_admin.py
```

### Base de Datos

```bash
# Conectarse a PostgreSQL
docker-compose exec db psql -U maruchan_user -d maruchan_db

# Backup de base de datos
docker-compose exec db pg_dump -U maruchan_user maruchan_db > backup.sql

# Aplicar migraciones
docker-compose exec backend alembic upgrade head

# Crear nueva migración
docker-compose exec backend alembic revision --autogenerate -m "descripcion"
```

### Reconstruir Después de Cambios

```bash
# Reconstruir sin cache
docker-compose build --no-cache

# Reconstruir y levantar
docker-compose up -d --build
```

### Limpiar Todo (⚠️ BORRA DATOS)

```bash
# Detener y eliminar contenedores y volúmenes
docker-compose down -v

# Eliminar todo (contenedores, imágenes, volúmenes)
docker-compose down -v --rmi all
```

---

## 📤 API Endpoints Principales

### Autenticación
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/auth/login` | Iniciar sesión |
| GET | `/api/auth/me` | Usuario actual |

### Usuarios
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/users/` | Listar usuarios |
| POST | `/api/users/` | Crear usuario |
| PUT | `/api/users/{id}` | Actualizar usuario |
| DELETE | `/api/users/{id}` | Eliminar usuario |
| POST | `/api/users/{id}/profile-picture` | Subir foto de perfil |

### Cursos
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/courses/` | Listar cursos |
| POST | `/api/courses/` | Crear curso |
| PUT | `/api/courses/{id}` | Actualizar curso |
| DELETE | `/api/courses/{id}` | Eliminar curso |

### Tareas (Assignments)
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/assignments/` | Listar tareas |
| POST | `/api/assignments/` | Crear tarea |
| PUT | `/api/assignments/{id}` | **Editar tarea** |
| DELETE | `/api/assignments/{id}` | Eliminar tarea |
| GET | `/api/assignments/{id}/stats` | Estadísticas |

### Entregas (Submissions)
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/submissions/upload` | Subir entrega |
| GET | `/api/submissions/{id}/download` | Descargar archivo |
| PUT | `/api/submissions/{id}/grade` | Calificar entrega |

### Chat
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/chat/users/online` | Usuarios en línea |
| GET | `/api/chat/history/{user_id}` | Historial de mensajes |
| POST | `/api/chat/send` | Enviar mensaje |

---

## 🔐 Seguridad

### Variables Sensibles

❌ **NO commitear** archivos `.env` con credenciales reales

✅ Cambiar contraseñas por defecto en producción:
- `admin@maruchan.edu / admin123`
- `POSTGRES_PASSWORD`
- `SECRET_KEY`

### Generar SECRET_KEY Segura

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## 🐛 Troubleshooting

### Error: "Cannot connect to database"
```bash
docker-compose ps db          # Verificar estado
docker-compose logs db        # Ver logs
docker-compose restart db     # Reiniciar
```

### Frontend no conecta con Backend
```bash
docker network inspect maruchan_network
docker-compose exec frontend env | grep API_URL
```

### Limpiar y reiniciar todo
```bash
docker-compose down -v
docker-compose up -d --build
docker-compose exec backend alembic upgrade head
docker-compose exec backend python crear_admin.py
```

---

## 📊 Funcionalidades por Rol

| Funcionalidad | Admin | Profesor | Estudiante |
|---------------|:-----:|:--------:|:----------:|
| Ver Dashboard | ✅ | ✅ | ✅ |
| Gestionar Usuarios | ✅ | ❌ | ❌ |
| Crear Cursos | ✅ | ❌ | ❌ |
| Editar Cursos | ✅ | ❌ | ❌ |
| Crear Tareas | ✅ | ✅ | ❌ |
| Editar Tareas | ✅ | ✅ | ❌ |
| Eliminar Tareas | ✅ | ✅ | ❌ |
| Calificar Entregas | ✅ | ✅ | ❌ |
| Inscribir Estudiantes | ✅ | ✅ | ❌ |
| Ver Mis Cursos | ✅ | ✅ | ✅ |
| Subir Entregas | ❌ | ❌ | ✅ |
| Ver Calificaciones | ❌ | ❌ | ✅ |
| Chat/Comunidad | ✅ | ✅ | ✅ |
| Editar Perfil | ✅ | ✅ | ✅ |

---

## 📝 Próximas Funcionalidades

- [ ] Notificaciones por email
- [ ] Exportar reportes PDF
- [ ] Dashboard con gráficos avanzados
- [ ] Foros de discusión
- [ ] Calendario de entregas
- [ ] App móvil

---

## 📄 Licencia

MIT License

---

Desarrollado con ❤️ para Maruchan University | Diciembre 2025
