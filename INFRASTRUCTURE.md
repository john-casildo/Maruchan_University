# 🐳 Guía de Infraestructura y Docker - Maruchan University

Este documento explica detalladamente cómo funciona la infraestructura del proyecto basada en Docker y cómo se gestiona el almacenamiento de datos. Está diseñado para ayudarte a entender y explicar la arquitectura del sistema.

## 🏗️ Arquitectura General

El sistema utiliza **Docker Compose** para orquestar 4 servicios principales que funcionan de manera aislada pero interconectada.

```mermaid
graph TD
    User((Usuario))
    
    subgraph "Docker Host (Tu Computadora)"
        subgraph "Red Privada: maruchan_network"
            Frontend[Frontend Container\n(Streamlit :8501)]
            Backend[Backend Container\n(FastAPI :8000)]
            DB[(Database Container\nPostgreSQL :5432)]
            PgAdmin[PgAdmin Container\n(Gestión DB :5050)]
        end
        
        subgraph "Volúmenes (Persistencia)"
            VolDB[(postgres_data)]
            VolFiles[maruchan_files]
        end
    end

    User -->|Navegador| Frontend
    User -->|API Directa| Backend
    
    Frontend -->|HTTP Request| Backend
    Backend -->|SQL| DB
    Backend -->|Read/Write| VolFiles
    DB -->|Save Data| VolDB
```

---

## 📦 Servicios (Contenedores)

### 1. Base de Datos (`db`)
*   **Imagen:** `postgres:15-alpine` (Versión ligera de PostgreSQL).
*   **Función:** Almacena toda la información estructurada (usuarios, cursos, notas, relaciones).
*   **Puerto:** Expone el puerto `5432` internamente y externamente (para conectar herramientas locales).
*   **Salud (Healthcheck):** Tiene un sistema que avisa a los otros contenedores cuando está "lista" para recibir conexiones.

### 2. Backend (`backend`)
*   **Tecnología:** Python + FastAPI.
*   **Función:** Es el cerebro del sistema. Procesa la lógica, autenticación, subida de archivos y conecta con la base de datos.
*   **Dependencia:** Espera a que `db` esté saludable (`service_healthy`) antes de iniciar.
*   **Conexión:** Se conecta a la base de datos usando el nombre del servicio: `db` (Docker resuelve este nombre a la IP correcta automáticamente).

### 3. Frontend (`frontend`)
*   **Tecnología:** Python + Streamlit.
*   **Función:** Interfaz gráfica para el usuario.
*   **Comunicación:**
    *   Cuando el código Python del frontend necesita datos, hace peticiones HTTP a `http://backend:8000`.
    *   **Nota Importante:** Para las descargas directas desde el navegador del usuario, generamos enlaces que apuntan a `localhost` (o la IP pública), ya que el navegador no está dentro de la red de Docker.

### 4. PgAdmin (`pgadmin`)
*   **Imagen:** `dpage/pgadmin4`.
*   **Función:** Interfaz web para administrar la base de datos visualmente.
*   **Acceso:** Disponible en `http://localhost:5050`.

---

## 💾 Almacenamiento y Persistencia (Volúmenes)

Docker por defecto es efímero: si borras un contenedor, los datos dentro se pierden. Para evitar esto, usamos **Volúmenes**.

### 1. Base de Datos (`postgres_data`)
*   **Tipo:** Volumen nombrado de Docker.
*   **Ubicación en contenedor:** `/var/lib/postgresql/data`
*   **Propósito:** Aquí PostgreSQL guarda los archivos físicos de la base de datos.
*   **Ventaja:** Puedes destruir el contenedor `db` y volver a crearlo; mientras no borres el volumen, tus usuarios y cursos seguirán ahí.

### 2. Archivos del Sistema (`maruchan_files`)
*   **Tipo:** Volumen nombrado (o Bind Mount en desarrollo).
*   **Ubicación en contenedor:** `/app/maruchan_storage`
*   **Propósito:** Almacena los archivos subidos por los usuarios (PDFs de tareas, materiales de clase, fotos de perfil).
*   **Estructura interna:**
    ```
    /app/maruchan_storage/
    ├── submissions/    # Tareas entregadas por alumnos
    ├── materials/      # Material didáctico subido por profesores
    └── profiles/       # Fotos de perfil
    ```
*   **Funcionamiento:** Cuando un alumno sube una tarea, el Backend recibe el archivo y lo escribe en esta carpeta. La base de datos solo guarda la "ruta" (string), no el archivo binario.

---

## 🌐 Red (Networking)

*   **Nombre:** `maruchan_network`
*   **Tipo:** Bridge (Puente).
*   **Funcionamiento:** Crea una red privada virtual donde los contenedores pueden hablar entre sí usando sus nombres de servicio como si fueran dominios DNS.
    *   El `frontend` puede hacer ping a `backend`.
    *   El `backend` puede hacer ping a `db`.
    *   Esto aísla el tráfico de tu red doméstica y mejora la seguridad.

---

## 🔄 Ciclo de Vida de una Petición (Ejemplo: Subir Tarea)

1.  **Usuario** selecciona un PDF en el Frontend (Navegador).
2.  **Frontend** (Streamlit) recibe el archivo en memoria.
3.  **Frontend** envía el archivo mediante una petición `POST` al **Backend** (`http://backend:8000/api/submissions/upload`).
4.  **Backend**:
    *   Verifica el token de usuario (Autenticación).
    *   Guarda el archivo físico en el volumen `maruchan_files`.
    *   Guarda el registro (quién, qué archivo, fecha) en la **Base de Datos** (`db`).
5.  **Backend** responde "OK".
6.  **Frontend** muestra el mensaje de éxito "✅ Tarea subida".

---

## 🛠️ Comandos Clave para Explicar

*   `docker-compose up -d`: "Construye y levanta toda la infraestructura en segundo plano".
*   `docker-compose down`: "Apaga y elimina los contenedores y la red, pero **mantiene los volúmenes de datos** a salvo".
*   `docker-compose down -v`: "Apaga todo y **BORRA los volúmenes**. Esto es un 'Factory Reset', se pierden todos los datos".
*   `docker-compose logs -f`: "Muestra qué está pasando dentro de los contenedores en tiempo real".
