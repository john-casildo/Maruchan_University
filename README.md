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
- **Administrador:** Gestión total de usuarios, cursos y asignaciones.
- **Profesor:** Gestión de cursos asignados, creación de tareas, calificación y feedback.
- **Estudiante:** Inscripción a cursos, envío de tareas, visualización de notas.

### 📚 Gestión Académica
- **Cursos:** Creación, edición y asignación de profesores.
- **Inscripciones:** Control de estudiantes matriculados por curso.
- **Tareas:** Creación de asignaciones con fecha límite, puntaje y peso.
- **Entregas:** Subida de archivos, control de entregas tardías.
- **Calificaciones:** Sistema de notas con feedback detallado.

### 🛠️ Funcionalidades Técnicas
- **Autenticación:** JWT seguro con roles y permisos.
- **Archivos:** Subida y descarga directa de archivos (tareas/materiales).
- **Notificaciones:** Mensajes flash para feedback inmediato al usuario.
- **Interfaz:** UI moderna y responsiva con Streamlit.

## 🚀 Actualización v2.0 (27-30 Noviembre 2025)

Se han implementado nuevas capacidades de interacción y despliegue remoto:

### 🌐 1. Modo Online (Acceso Remoto)
Integración nativa con **Ngrok** para exponer la aplicación a internet de forma segura. Ahora es posible acceder a la plataforma desde cualquier dispositivo fuera de la red local mediante una URL pública generada automáticamente.

### 💬 2. Módulo de Comunidad (Chat)
Sistema de comunicación en tiempo real entre usuarios:
* **Mensajería Instantánea:** Envío y recepción de mensajes entre Admins, Profesores y Estudiantes.
* **Estado de Actividad:** Indicadores visuales de usuarios "En Línea" (🟢) y "Desconectados" (⚪).
* **Auto-refresco:** El chat se actualiza automáticamente cada 3 segundos o manualmente mediante botón.

### 🛠️ 3. Panel de Administración Renovado
* **Gestión de Usuarios:** Nueva tabla interactiva para buscar, filtrar y activar/desactivar usuarios.
* **Interfaz por Pestañas:** Organización limpia de Cursos, Inscripciones y Creación de usuarios.
* **Feedback Mejorado:** Notificaciones flotantes (*Toasts*) y validaciones de formulario visuales.

### ⚠️ Requisitos para esta versión
Para que las nuevas funciones (especialmente el Chat y el modo Online) funcionen, debes realizar dos pasos extra tras levantar los contenedores:

1.  **Configurar Token de Ngrok:**
    Edita el archivo `docker-compose.yml` y pega tu token en la variable `NGROK_AUTHTOKEN`.

2.  **Crear Tabla de Mensajes:**
    Ejecuta el siguiente comando para actualizar la base de datos:
    ```bash
    docker-compose exec backend alembic upgrade head
    ```

## 🚀 Inicio Rápido con Docker

### 1. Clonar el repositorio

```bash
git clone <tu-repositorio>
cd MaruchanUniversity
```

### 2. Configurar variables de entorno

```bash
cp .env.example .env
```

**Editar `.env` y generar SECRET_KEY:**
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 3. Construir y levantar los contenedores

```bash
# Levantar todos los servicios
docker-compose up -d

# Ver logs
docker-compose logs -f

# Ver estado
docker-compose ps
```

### 4. Aplicar migraciones (primera vez)

```bash
# Entrar al contenedor del backend
docker-compose exec backend bash

# Crear migración inicial
alembic revision --autogenerate -m "Initial migration"

# Aplicar migraciones
alembic upgrade head

# Salir
exit
```

### 5. Crear usuario administrador

```bash
docker-compose exec backend python crear_admin.py
```

Credenciales iniciales:
- **Email:** admin@maruchan.edu
- **Password:** admin123

### 6. Acceder a las aplicaciones

- 🎨 **Frontend (Streamlit):** http://localhost:8501
- 📡 **API (FastAPI):** http://localhost:8000
- 📚 **API Docs:** http://localhost:8000/docs
- 🗄️ **PgAdmin (opcional):** http://localhost:5050

## 📁 Estructura del Proyecto

```
MaruchanUniversity/
├── docker-compose.yml       # Orquestación de contenedores
├── .env                     # Variables de entorno
├── .env.example            # Plantilla de variables
├── init-db.sh              # Script de inicialización DB
│
├── backend/                # API FastAPI
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── dependencies.py
│   ├── crear_admin.py
│   │
│   ├── routers/
│   │   ├── users.py
│   │   ├── courses.py
│   │   ├── enrollments.py
│   │   ├── assignments.py
│   │   ├── submissions.py    # Upload/Download
│   │   └── materials.py      # Upload/Download
│   │
│   └── alembic/           # Migraciones
│       └── versions/
│
├── frontend/              # App Streamlit
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app.py            # App principal
│   └── .streamlit/
│       └── config.toml
│
└── maruchan_storage/     # Volumen de archivos (Docker)
    ├── submissions/      # Entregas de estudiantes
    ├── materials/        # Materiales de curso
    └── profiles/         # Fotos de perfil
```

## 🐳 Comandos Docker Útiles

### Gestión de contenedores

```bash
# Iniciar servicios
docker-compose up -d

# Detener servicios
docker-compose down

# Reiniciar un servicio
docker-compose restart backend
docker-compose restart frontend

# Ver logs en tiempo real
docker-compose logs -f backend

# Ver logs de todos los servicios
docker-compose logs -f

# Ejecutar comando en contenedor
docker-compose exec backend python crear_admin.py
```

### Gestión de volúmenes

```bash
# Listar volúmenes
docker volume ls

# Inspeccionar volumen de archivos
docker volume inspect maruchanuniversity_maruchan_files

# Limpiar volúmenes no usados (¡CUIDADO!)
docker volume prune
```

### Reconstruir después de cambios

```bash
# Reconstruir sin cache
docker-compose build --no-cache

# Reconstruir y levantar
docker-compose up -d --build

# Solo reconstruir backend
docker-compose build backend
```

### Base de datos

```bash
# Conectarse a PostgreSQL
docker-compose exec db psql -U maruchan_user -d maruchan_db

# Backup de base de datos
docker-compose exec db pg_dump -U maruchan_user maruchan_db > backup.sql

# Restaurar backup
docker-compose exec -T db psql -U maruchan_user maruchan_db < backup.sql
```

### Limpiar todo (CUIDADO: borra datos)

```bash
# Detener y eliminar contenedores, volúmenes y redes
docker-compose down -v

# Eliminar todo (contenedores, imágenes, volúmenes)
docker-compose down -v --rmi all
```

## 📤 Sistema de Archivos

### Subir archivos desde Streamlit

El frontend de Streamlit maneja automáticamente el upload de archivos:

1. Usuario selecciona archivo en la interfaz
2. Streamlit envía archivo al endpoint de FastAPI
3. FastAPI guarda en volumen Docker `maruchan_files`
4. Path se guarda en PostgreSQL

### Estructura de almacenamiento

```
maruchan_storage/
├── submissions/
│   └── assignment_1/
│       └── student_5/
│           └── 20240115_120000_tarea.pdf
│
└── materials/
    └── course_1/
        └── type_pdf/
            └── 20240115_100000_clase1.pdf
```

### Endpoints de archivos

**Subir entrega:**
```bash
POST /api/submissions/upload
Content-Type: multipart/form-data
- assignment_id: int
- file: File
```

**Descargar entrega:**
```bash
GET /api/submissions/{id}/download
Authorization: Bearer {token}
# O vía Query Param para descarga directa:
GET /api/submissions/{id}/download?token={token}
```

**Subir material:**
```bash
POST /api/materials/upload
Content-Type: multipart/form-data
- course_id: int
- title: string
- material_type: enum
- file: File
```

## 🔧 Desarrollo Local

### Backend sin Docker

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend sin Docker

```bash
cd frontend
pip install -r requirements.txt
streamlit run app.py
```

## 🧪 Testing

```bash
# Ejecutar tests en contenedor
docker-compose exec backend pytest

# Con cobertura
docker-compose exec backend pytest --cov=. --cov-report=html
```

## 📊 Monitoreo

### Ver recursos usados

```bash
# Uso de recursos por contenedor
docker stats

# Logs en tiempo real
docker-compose logs -f --tail=100
```

### Healthchecks

Los servicios tienen healthchecks configurados:

```bash
# Ver estado de salud
docker-compose ps

# Inspeccionar health de un contenedor
docker inspect maruchan_backend | grep -A 10 Health
```

## 🔐 Seguridad

### Variables sensibles

❌ **NO commitear** `.env` al repositorio
✅ Usar `.env.example` como plantilla
✅ Generar `SECRET_KEY` única:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Cambiar contraseñas por defecto

```python
# En producción, cambiar:
- admin@maruchan.edu / admin123
- POSTGRES_PASSWORD
- SECRET_KEY
- PGADMIN_PASSWORD
```

## 🚀 Despliegue en Producción

### 1. Configurar servidor

```bash
# Instalar Docker y Docker Compose
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
```

### 2. Clonar y configurar

```bash
git clone <repo>
cd MaruchanUniversity
cp .env.example .env
nano .env  # Configurar para producción
```

### 3. Cambiar configuraciones de producción

En `.env`:
```bash
ENVIRONMENT=production
DEBUG=False
```

### 4. Levantar servicios

```bash
docker-compose up -d
docker-compose exec backend python crear_admin.py
```

### 5. Configurar NGINX (opcional)

```nginx
server {
    listen 80;
    server_name maruchan.edu;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    location /api {
        proxy_pass http://localhost:8000;
    }
}
```

## 🐛 Troubleshooting

### Error: "Cannot connect to database"

```bash
# Verificar que DB esté corriendo
docker-compose ps db

# Ver logs de DB
docker-compose logs db

# Reiniciar servicio de DB
docker-compose restart db
```

### Error: "Permission denied" en archivos

```bash
# Verificar permisos del volumen
docker-compose exec backend ls -la /app/maruchan_storage

# Corregir permisos
docker-compose exec backend chmod -R 755 /app/maruchan_storage
```

### Frontend no conecta con Backend

```bash
# Verificar que estén en la misma red
docker network ls
docker network inspect maruchanuniversity_maruchan_network

# Verificar variable API_URL
docker-compose exec frontend env | grep API_URL
```

### Limpiar y reiniciar todo

```bash
docker-compose down -v
docker-compose up -d --build
docker-compose exec backend python crear_admin.py
```

## 📦 Backup y Restauración

### Backup completo

```bash
# Base de datos
docker-compose exec db pg_dump -U maruchan_user maruchan_db > backup_db.sql

# Archivos
docker run --rm -v maruchanuniversity_maruchan_files:/data -v $(pwd):/backup \
  alpine tar czf /backup/backup_files.tar.gz -C /data .
```

### Restaurar

```bash
# Base de datos
docker-compose exec -T db psql -U maruchan_user maruchan_db < backup_db.sql

# Archivos
docker run --rm -v maruchanuniversity_maruchan_files:/data -v $(pwd):/backup \
  alpine tar xzf /backup/backup_files.tar.gz -C /data
```

## 📝 Próximas Funcionalidades

- [ ] Notificaciones por email
- [ ] Sistema de foros
- [ ] Chat en tiempo real
- [ ] Exportar reportes PDF
- [ ] Dashboard con gráficos avanzados
- [ ] App móvil
- [ ] Integración con Zoom/Meet

## 🤝 Contribuir

Ver [CONTRIBUTING.md](CONTRIBUTING.md)

## 📄 Licencia

MIT License - Ver [LICENSE](LICENSE)

## 📞 Soporte

- Email: admin@maruchan.edu
- Issues: GitHub Issues
- Docs: http://localhost:8000/docs

---

Desarrollado con ❤️ para Maruchan University