# 🧠 Registro de Decisiones del Proyecto (ADR)

Este documento recopila las decisiones técnicas y de diseño tomadas durante el desarrollo de **Maruchan University**. Sirve para entender el "por qué" de la arquitectura actual.

## 1. Stack Tecnológico

### Backend: **FastAPI**
*   **Decisión:** Usar FastAPI en lugar de Django o Flask.
*   **Motivo:**
    *   **Velocidad:** Es asíncrono (`async/await`) nativamente, ideal para I/O (lectura de archivos/BD).
    *   **Documentación:** Genera automáticamente Swagger UI (`/docs`), lo que facilitó probar los endpoints sin crear una UI primero.
    *   **Validación:** Pydantic asegura que los datos de entrada/salida sean correctos automáticamente.

### Frontend: **Streamlit**
*   **Decisión:** Usar Streamlit en lugar de React/Vue/Angular.
*   **Motivo:**
    *   **Velocidad de Desarrollo:** Permite crear interfaces de datos completas usando solo Python.
    *   **Simplicidad:** Evita la complejidad de gestionar un estado en el cliente (JavaScript) y una API REST compleja para este alcance.
    *   **Foco:** Nos permitió centrarnos en la lógica de negocio (inscripciones, notas) más que en CSS/HTML.

### Base de Datos: **PostgreSQL**
*   **Decisión:** Usar PostgreSQL con SQLAlchemy ORM.
*   **Motivo:**
    *   Necesitábamos una base de datos relacional robusta para manejar la integridad de datos (ej: no borrar un curso si tiene alumnos inscritos).
    *   SQLAlchemy permite trabajar con objetos Python en lugar de escribir SQL crudo, facilitando el mantenimiento.

---

## 2. Arquitectura e Infraestructura

### Contenedorización con **Docker Compose**
*   **Decisión:** Separar cada servicio (Frontend, Backend, DB) en su propio contenedor.
*   **Motivo:**
    *   **Aislamiento:** Las dependencias de Python del frontend no chocan con las del backend.
    *   **Reproducibilidad:** "Funciona en mi máquina" -> Funciona en cualquier máquina con Docker.
    *   **Red Interna:** Los servicios se comunican en una red privada (`maruchan_network`), exponiendo solo lo necesario.

### Gestión de Archivos (Storage)
*   **Decisión:** Usar el sistema de archivos local (Volumen Docker) en lugar de S3/Cloud.
*   **Motivo:**
    *   Mantener el proyecto autocontenido y sin dependencias de servicios de pago externos para esta fase.
    *   **Implementación:** Se mapeó un volumen `maruchan_files` a `/app/maruchan_storage` para que los archivos sobrevivan si se reinician los contenedores.

---

## 3. Autenticación y Seguridad

### JWT (JSON Web Tokens)
*   **Decisión:** Autenticación sin estado (Stateless).
*   **Motivo:** El servidor no necesita guardar "sesiones" en memoria. El token contiene la información del usuario y su rol.

### Token en URL (Query Param)
*   **Decisión:** Permitir recibir el token vía URL (`?token=xyz`) además de en los Headers.
*   **Motivo:**
    *   **Problema:** Los navegadores no pueden enviar Headers personalizados (Authorization: Bearer...) en un enlace simple (`<a>` o `st.link_button`).
    *   **Solución:** Para permitir descargas directas con un clic, pasamos el token en la URL temporalmente para validar la petición.

### Roles de Usuario (RBAC)
*   **Decisión:** Implementar roles estrictos (Admin, Teacher, Student).
*   **Motivo:** Seguridad. Un estudiante no debe poder ver las entregas de otros ni calificarse a sí mismo. Esto se valida en cada endpoint del Backend (`dependencies.py`).

---

## 4. Frontend y Experiencia de Usuario (UX)

### Descargas Directas (`st.link_button`)
*   **Decisión:** Cambiar de `st.download_button` a `st.link_button`.
*   **Motivo:**
    *   **Antes:** `st.download_button` cargaba el archivo entero en la memoria RAM del servidor Streamlit antes de enviarlo al usuario. Lento e ineficiente para archivos grandes.
    *   **Ahora:** `st.link_button` genera un enlace directo al Backend. El navegador descarga el archivo directamente desde la API, sin pasar por el servidor de Streamlit.

### Ventanas Emergentes (`st.popover`)
*   **Decisión:** Usar Popovers para los formularios de calificación.
*   **Motivo:**
    *   **Problema:** Streamlit no permite poner un "Expander" (desplegable) dentro de otro. Queríamos tener la lista de tareas desplegable y dentro el formulario de calificación.
    *   **Solución:** El `st.popover` actúa como una ventana modal que sí puede estar dentro de un expander, resolviendo el error de anidamiento y limpiando la interfaz.

### Mensajes Flash (`st.session_state`)
*   **Decisión:** Implementar un sistema de notificaciones persistente.
*   **Motivo:**
    *   En Streamlit, al recargar la página (`st.rerun()`) para actualizar datos, los mensajes de éxito (`st.success`) se borraban inmediatamente.
    *   Creamos una lógica que guarda el mensaje en `session_state` y lo muestra *después* de la recarga.

---

## 5. Base de Datos

### Migraciones con **Alembic**
*   **Decisión:** Usar Alembic para gestionar cambios en la BD.
*   **Motivo:** Permite evolucionar el esquema (ej: agregar columna `teacher_id`) sin borrar la base de datos ni perder datos existentes.

### Relaciones Clave
*   **Decisión:** `Course` tiene un solo `Teacher`.
*   **Decisión:** `Enrollment` es una tabla intermedia con estado (`enrolled`, `dropped`) y nota final.
*   **Decisión:** `Submission` vincula `Student` y `Assignment`, permitiendo múltiples intentos (aunque la lógica actual sobrescribe el archivo para simplificar).
