import streamlit as st
import requests
import os
from datetime import datetime
from streamlit_option_menu import option_menu

# Configuración de la página
st.set_page_config(
    page_title="Maruchan University",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# URL de la API
API_URL = os.getenv("API_URL", "http://localhost:8000")

# CSS personalizado
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
    }
    .upload-section {
        border: 2px dashed #1f77b4;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)


# ==================== FUNCIONES DE API ====================

def login(username: str, password: str):
    """Login a la API"""
    try:
        response = requests.post(
            f"{API_URL}/api/auth/login",
            data={"username": username, "password": password}
        )
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"Error conectando con la API: {e}")
        return None


def get_current_user(token: str):
    """Obtiene información del usuario actual"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{API_URL}/api/auth/me", headers=headers)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"Error obteniendo usuario: {e}")
        return None


def get_my_courses(token: str):
    """Obtiene los cursos del usuario"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{API_URL}/api/courses/my-courses", headers=headers)
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        st.error(f"Error obteniendo cursos: {e}")
        return []


def upload_submission(token: str, assignment_id: int, file):
    """Sube una entrega"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        files = {"file": (file.name, file, file.type)}
        data = {"assignment_id": assignment_id}
        
        response = requests.post(
            f"{API_URL}/api/submissions/upload",
            headers=headers,
            files=files,
            data=data
        )
        
        return response.status_code == 201, response.json()
    except Exception as e:
        st.error(f"Error subiendo archivo: {e}")
        return False, {"detail": str(e)}


def download_submission(token: str, submission_id: int):
    """Descarga una entrega"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{API_URL}/api/submissions/{submission_id}/download",
            headers=headers
        )
        
        if response.status_code == 200:
            return response.content
        return None
    except Exception as e:
        st.error(f"Error descargando archivo: {e}")
        return None


def get_assignments(token: str, course_id: int = None):
    """Obtiene asignaciones"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        params = {"course_id": course_id} if course_id else {}
        
        response = requests.get(
            f"{API_URL}/api/assignments/",
            headers=headers,
            params=params
        )
        
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        st.error(f"Error obteniendo asignaciones: {e}")
        return []


def get_assignment_submissions(token: str, assignment_id: int):
    """Obtiene las entregas de una asignación"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{API_URL}/api/submissions/?assignment_id={assignment_id}",
            headers=headers
        )
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        st.error(f"Error obteniendo entregas: {e}")
        return []


def grade_submission_api(token: str, submission_id: int, grade_data: dict):
    """Califica una entrega"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.patch(
            f"{API_URL}/api/submissions/{submission_id}/grade",
            headers=headers,
            json=grade_data
        )
        
        if response.status_code == 200:
            return True, response.json()
        return False, response.json()
    except Exception as e:
        st.error(f"Error calificando entrega: {e}")
        return False, {"detail": str(e)}


def get_my_submissions(token: str):
    """Obtiene las entregas del usuario"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{API_URL}/api/submissions/my-submissions",
            headers=headers
        )
        
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        st.error(f"Error obteniendo entregas: {e}")
        return []


def create_assignment(token: str, assignment_data: dict):
    """Crea una nueva asignación"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(
            f"{API_URL}/api/assignments/",
            headers=headers,
            json=assignment_data
        )
        
        if response.status_code == 201:
            return True, response.json()
        return False, response.json()
    except Exception as e:
        st.error(f"Error creando asignación: {e}")
        return False, {"detail": str(e)}


def update_user_profile(token: str, user_id: int, user_data: dict, profile_pic_file=None):
    """Actualiza el perfil del usuario"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        # 1. Actualizar datos de texto
        response = requests.put(
            f"{API_URL}/api/users/{user_id}",
            headers=headers,
            json=user_data
        )
        
        if response.status_code != 200:
            return False, response.json()
            
        updated_user = response.json()
        
        # 2. Subir imagen si se proporciona
        if profile_pic_file:
            # Reiniciar el puntero del archivo por si acaso
            profile_pic_file.seek(0)
            files = {"file": (profile_pic_file.name, profile_pic_file, profile_pic_file.type)}
            
            img_response = requests.post(
                f"{API_URL}/api/users/{user_id}/profile-picture",
                headers=headers,
                files=files
            )
            
            if img_response.status_code == 200:
                updated_user = img_response.json()
            else:
                return False, {"detail": f"Datos actualizados, pero error en imagen: {img_response.text}"}
        
        return True, updated_user
    except Exception as e:
        st.error(f"Error actualizando perfil: {e}")
        return False, {"detail": str(e)}


def create_user(token: str, user_data: dict):
    """Crea un nuevo usuario"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(
            f"{API_URL}/api/users/",
            headers=headers,
            json=user_data
        )
        
        if response.status_code == 201:
            return True, response.json()
        return False, response.json()
    except Exception as e:
        st.error(f"Error creando usuario: {e}")
        return False, {"detail": str(e)}


def get_teachers(token: str):
    """Obtiene lista de profesores"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{API_URL}/api/users/?role=teacher", headers=headers)
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        st.error(f"Error obteniendo profesores: {e}")
        return []


def create_course_api(token: str, course_data: dict):
    """Crea un nuevo curso"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(
            f"{API_URL}/api/courses/",
            headers=headers,
            json=course_data
        )
        
        if response.status_code == 201:
            return True, response.json()
        return False, response.json()
    except Exception as e:
        st.error(f"Error creando curso: {e}")
        return False, {"detail": str(e)}


def get_all_courses(token: str):
    """Obtiene todos los cursos (Admin)"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{API_URL}/api/courses/", headers=headers)
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        st.error(f"Error obteniendo cursos: {e}")
        return []


def update_course_api(token: str, course_id: int, course_data: dict):
    """Actualiza un curso"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.put(
            f"{API_URL}/api/courses/{course_id}",
            headers=headers,
            json=course_data
        )
        if response.status_code == 200:
            return True, response.json()
        return False, response.json()
    except Exception as e:
        st.error(f"Error actualizando curso: {e}")
        return False, {"detail": str(e)}


def delete_course_api(token: str, course_id: int):
    """Elimina un curso"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.delete(
            f"{API_URL}/api/courses/{course_id}",
            headers=headers
        )
        if response.status_code == 200:
            return True, response.json()
        return False, response.json()
    except Exception as e:
        st.error(f"Error eliminando curso: {e}")
        return False, {"detail": str(e)}


def get_students(token: str):
    """Obtiene lista de estudiantes"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{API_URL}/api/users/?role=student", headers=headers)
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        st.error(f"Error obteniendo estudiantes: {e}")
        return []


def enroll_student_api(token: str, course_id: int, student_id: int):
    """Inscribe un estudiante en un curso"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        data = {"student_id": student_id, "course_id": course_id}
        response = requests.post(
            f"{API_URL}/api/enrollments/",
            headers=headers,
            json=data
        )
        
        if response.status_code == 201:
            return True, response.json()
        return False, response.json()
    except Exception as e:
        st.error(f"Error inscribiendo estudiante: {e}")
        return False, {"detail": str(e)}


def get_course_enrollments(token: str, course_id: int):
    """Obtiene las inscripciones de un curso"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{API_URL}/api/enrollments/?course_id={course_id}&status=enrolled",
            headers=headers
        )
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        st.error(f"Error obteniendo inscripciones: {e}")
        return []


# ==================== INICIALIZAR SESSION STATE ====================

if "token" not in st.session_state:
    st.session_state.token = None
if "user" not in st.session_state:
    st.session_state.user = None
if "flash_message" not in st.session_state:
    st.session_state.flash_message = None


# ==================== PÁGINA DE LOGIN ====================

def show_login():
    st.markdown('<h1 class="main-header">🎓 Maruchan University</h1>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### Iniciar Sesión")
        
        with st.form("login_form"):
            username = st.text_input("Usuario o Email", placeholder="tu-email@ejemplo.com")
            password = st.text_input("Contraseña", type="password")
            submit = st.form_submit_button("Ingresar", use_container_width=True)
            
            if submit:
                if username and password:
                    with st.spinner("Autenticando..."):
                        result = login(username, password)
                        
                        if result:
                            token = result["access_token"]
                            user = get_current_user(token)
                            
                            if user:
                                st.session_state.token = token
                                st.session_state.user = user
                                st.success("✅ Login exitoso!")
                                st.rerun()
                            else:
                                st.error("❌ Error al obtener perfil de usuario")
                        else:
                            st.error("❌ Credenciales incorrectas")
                else:
                    st.warning("⚠️ Por favor ingresa usuario y contraseña")
        
        st.markdown("---")
        st.info("💡 **Usuario demo:** admin@maruchan.edu / admin123")


# ==================== PÁGINA PRINCIPAL ====================

def show_main_app():
    # Mostrar mensajes flash si existen
    if st.session_state.flash_message:
        msg_type, msg_text = st.session_state.flash_message
        if msg_type == "success":
            st.success(msg_text)
        elif msg_type == "error":
            st.error(msg_text)
        elif msg_type == "warning":
            st.warning(msg_text)
        elif msg_type == "info":
            st.info(msg_text)
        # Limpiar mensaje después de mostrarlo
        st.session_state.flash_message = None

    # Verificar si el usuario está cargado
    if st.session_state.user is None:
        if st.session_state.token:
            st.session_state.user = get_current_user(st.session_state.token)
        
        if st.session_state.user is None:
            st.session_state.token = None
            st.rerun()
            return

    user = st.session_state.user
    
    if user is None:
        return

    # Sidebar
    with st.sidebar:
        st.markdown(f"### 👤 {user.get('full_name', 'Usuario')}")
        st.caption(f"Rol: {user.get('role', 'N/A')}")
        st.markdown("---")
        
        if user.get('role') == 'admin':
            menu_options = ["Dashboard", "Perfil", "Administración"]
            menu_icons = ["house", "person", "gear"]
        else:
            menu_options = ["Dashboard", "Mis Cursos", "Tareas", "Entregas", "Calificaciones", "Perfil"]
            menu_icons = ["house", "book", "clipboard-check", "upload", "graph-up", "person"]
        
        selected = option_menu(
            menu_title="Menú Principal",
            options=menu_options,
            icons=menu_icons,
            menu_icon="cast",
            default_index=0,
        )
        
        st.markdown("---")
        
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            st.session_state.token = None
            st.session_state.user = None
            st.rerun()
    
    # Contenido principal
    if selected == "Dashboard":
        show_dashboard()
    elif selected == "Mis Cursos":
        show_courses()
    elif selected == "Tareas":
        show_assignments()
    elif selected == "Entregas":
        show_submissions()
    elif selected == "Calificaciones":
        show_grades()
    elif selected == "Perfil":
        show_profile()
    elif selected == "Administración":
        show_admin_panel()


def show_dashboard():
    st.title("📊 Dashboard")
    
    # Obtener estadísticas
    courses = get_my_courses(st.session_state.token)
    assignments = get_assignments(st.session_state.token)
    submissions = get_my_submissions(st.session_state.token)
    
    # Métricas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Cursos Inscritos", len(courses))
    
    with col2:
        pending = len([a for a in assignments if a['id'] not in [s['assignment_id'] for s in submissions]])
        st.metric("Tareas Pendientes", pending)
    
    with col3:
        st.metric("Entregas Realizadas", len(submissions))
    
    with col4:
        graded = len([s for s in submissions if s['grade'] is not None])
        st.metric("Tareas Calificadas", graded)
    
    st.markdown("---")
    
    # Próximas tareas
    st.subheader("📅 Próximas Entregas")
    
    if assignments:
        for assignment in assignments[:5]:
            with st.expander(f"📝 {assignment['title']} - {assignment['course_code']}"):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"**Fecha límite:** {assignment['due_date']}")
                    st.write(f"**Puntos:** {assignment['max_score']}")
                
                with col2:
                    if assignment['is_overdue']:
                        st.error("⏰ Vencida")
                    else:
                        st.success("✅ A tiempo")
    else:
        st.info("No hay tareas pendientes")


def show_courses():
    st.title("📚 Mis Cursos")
    
    courses = get_my_courses(st.session_state.token)
    user = st.session_state.user
    # Permitir a admin y profesores ver las herramientas de gestión
    is_teacher = user.get('role') in ['teacher', 'admin']
    
    if courses:
        for course in courses:
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.subheader(f"{course['code']} - {course['title']}")
                    st.caption(f"Profesor: {course['teacher_name']}")
                
                with col2:
                    st.metric("Créditos", course['credits'])
                
                with col3:
                    st.metric("Semestre", course['semester'])
                
                # Sección de gestión para profesores y admins
                if is_teacher:
                    with st.expander("⚙️ Gestión del Curso"):
                        # Usamos tabs para organizar las acciones
                        tab_students, tab_assignments = st.tabs(["👥 Estudiantes", "📝 Crear Tarea"])
                        
                        # --- TAB ESTUDIANTES ---
                        with tab_students:
                            st.write(f"**Estudiantes Inscritos:** {course['enrolled_count']}")
                            
                            # Mostrar lista de estudiantes inscritos
                            enrollments = get_course_enrollments(st.session_state.token, course['id'])
                            if enrollments:
                                st.markdown("##### Lista de Estudiantes")
                                for enrollment in enrollments:
                                    student = enrollment['student']
                                    with st.container():
                                        col_s1, col_s2 = st.columns([3, 1])
                                        with col_s1:
                                            st.write(f"👤 {student['full_name']} ({student['email']})")
                                            if student.get('carnet'):
                                                st.caption(f"Carnet: {student['carnet']}")
                                        with col_s2:
                                            st.caption(f"Inscrito: {enrollment['enrolled_at'][:10]}")
                                    st.divider()
                            else:
                                st.info("No hay estudiantes inscritos en este curso.")

                            st.markdown("#### Inscribir Estudiante")
                            all_students = get_students(st.session_state.token)
                            
                            if all_students:
                                # Filtrar estudiantes ya inscritos
                                enrolled_ids = [e['student']['id'] for e in enrollments]
                                available_students = [s for s in all_students if s['id'] not in enrolled_ids]
                                
                                if available_students:
                                    student_opts = {s['id']: f"{s['full_name']} ({s['carnet'] or 'S/C'})" for s in available_students}
                                    
                                    with st.form(f"enroll_student_course_{course['id']}"):
                                        sel_student = st.selectbox(
                                            "Seleccionar Estudiante",
                                            options=list(student_opts.keys()),
                                            format_func=lambda x: student_opts[x],
                                            key=f"sel_std_{course['id']}"
                                        )
                                        
                                        if st.form_submit_button("Inscribir Alumno"):
                                            with st.spinner("Inscribiendo..."):
                                                success, res = enroll_student_api(st.session_state.token, course['id'], sel_student)
                                                if success:
                                                    st.success("Estudiante inscrito exitosamente")
                                                    st.rerun()
                                                else:
                                                    st.error(f"Error: {res.get('detail')}")
                                else:
                                    st.info("Todos los estudiantes registrados ya están inscritos en este curso.")
                            else:
                                st.info("No hay estudiantes registrados en el sistema.")

                        # --- TAB TAREAS ---
                        with tab_assignments:
                            st.markdown("#### Nueva Asignación")
                            with st.form(f"quick_assignment_{course['id']}"):
                                qa_title = st.text_input("Título", key=f"qa_title_{course['id']}")
                                
                                qa_c1, qa_c2 = st.columns(2)
                                with qa_c1:
                                    qa_date = st.date_input("Fecha entrega", key=f"qa_date_{course['id']}")
                                    qa_time = st.time_input("Hora entrega", key=f"qa_time_{course['id']}")
                                with qa_c2:
                                    qa_score = st.number_input("Puntos", value=100.0, key=f"qa_score_{course['id']}")
                                    qa_weight = st.number_input("Peso (1.0 = 100%)", value=1.0, key=f"qa_weight_{course['id']}")
                                
                                qa_desc = st.text_area("Instrucciones", key=f"qa_desc_{course['id']}")
                                
                                if st.form_submit_button("Publicar Tarea"):
                                    if qa_title:
                                        due_dt = datetime.combine(qa_date, qa_time)
                                        assign_data = {
                                            "course_id": course['id'],
                                            "title": qa_title,
                                            "description": qa_desc,
                                            "due_date": due_dt.isoformat(),
                                            "max_score": qa_score,
                                            "weight": qa_weight,
                                            "is_published": True
                                        }
                                        
                                        with st.spinner("Creando tarea..."):
                                            success, res = create_assignment(st.session_state.token, assign_data)
                                            if success:
                                                st.session_state.flash_message = ("success", "✅ Tarea creada exitosamente!")
                                                st.rerun()
                                            else:
                                                error_msg = res.get('detail') if isinstance(res, dict) else str(res)
                                                st.error(f"Error: {error_msg}")
                                    else:
                                        st.warning("El título es obligatorio")

                st.markdown("---")
    else:
        st.info("No estás inscrito en ningún curso (o no tienes cursos asignados si eres profesor).")


def show_assignments():
    st.title("📋 Tareas y Asignaciones")
    
    user = st.session_state.user
    is_teacher = user.get('role') in ['teacher', 'admin']
    
    # Selector de curso
    courses = get_my_courses(st.session_state.token)
    course_options = {c['id']: f"{c['code']} - {c['title']}" for c in courses}
    
    # Sección para crear tarea (Solo profesores)
    if is_teacher:
        with st.expander("➕ Crear Nueva Tarea", expanded=False):
            with st.form("create_assignment_form"):
                st.subheader("Nueva Asignación")
                
                c_col1, c_col2 = st.columns(2)
                with c_col1:
                    new_course_id = st.selectbox(
                        "Curso",
                        options=list(course_options.keys()),
                        format_func=lambda x: course_options[x]
                    )
                    new_title = st.text_input("Título de la tarea")
                    new_due_date = st.date_input("Fecha de entrega")
                    new_due_time = st.time_input("Hora de entrega")
                
                with c_col2:
                    new_max_score = st.number_input("Puntos máximos", min_value=0.0, value=100.0)
                    new_weight = st.number_input("Peso en nota final", min_value=0.0, value=1.0)
                    new_is_published = st.checkbox("Publicar inmediatamente", value=True)
                
                new_description = st.text_area("Descripción e instrucciones")
                
                submitted = st.form_submit_button("Crear Tarea")
                
                if submitted:
                    if new_title and new_course_id:
                        # Combinar fecha y hora
                        due_datetime = datetime.combine(new_due_date, new_due_time)
                        
                        assignment_data = {
                            "course_id": new_course_id,
                            "title": new_title,
                            "description": new_description,
                            "due_date": due_datetime.isoformat(),
                            "max_score": new_max_score,
                            "weight": new_weight,
                            "is_published": new_is_published
                        }
                        
                        with st.spinner("Creando tarea..."):
                            success, result = create_assignment(st.session_state.token, assignment_data)
                            
                            if success:
                                st.session_state.flash_message = ("success", "✅ Tarea creada exitosamente!")
                                st.rerun()
                            else:
                                error_msg = result.get('detail') if isinstance(result, dict) else str(result)
                                st.error(f"❌ Error: {error_msg}")
                    else:
                        st.warning("⚠️ Por favor completa los campos obligatorios")
        
        st.markdown("---")

    selected_course = st.selectbox(
        "Filtrar por curso",
        options=[None] + list(course_options.keys()),
        format_func=lambda x: "Todos los cursos" if x is None else course_options[x]
    )
    
    # Obtener asignaciones
    assignments = get_assignments(st.session_state.token, selected_course)
    submissions = get_my_submissions(st.session_state.token)
    submitted_ids = [s['assignment_id'] for s in submissions]
    
    if assignments:
        for assignment in assignments:
            is_submitted = assignment['id'] in submitted_ids
            
            # Título del expander diferente para profes y alumnos
            if is_teacher:
                expander_title = f"📝 {assignment['title']} - {assignment['course_code']}"
            else:
                expander_title = f"{'✅' if is_submitted else '📝'} {assignment['title']} - {assignment['course_code']}"
            
            with st.expander(expander_title, expanded=not is_submitted if not is_teacher else False):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write(f"**Descripción:** {assignment.get('description', 'Sin descripción')}")
                    st.write(f"**Fecha límite:** {assignment['due_date']}")
                    st.write(f"**Puntos máximos:** {assignment['max_score']}")
                
                with col2:
                    if assignment['is_overdue']:
                        st.error("⏰ VENCIDA")
                    else:
                        st.success("✅ A tiempo")
                    
                    if not is_teacher:
                        if is_submitted:
                            st.info("Ya entregada")
                
                # Botón para subir entrega (Solo estudiantes)
                if not is_teacher and not is_submitted:
                    st.markdown("### 📤 Subir Entrega")
                    uploaded_file = st.file_uploader(
                        "Selecciona tu archivo",
                        key=f"upload_{assignment['id']}"
                    )
                    
                    if uploaded_file:
                        if st.button(f"Enviar Tarea", key=f"submit_{assignment['id']}"):
                            with st.spinner("Subiendo archivo..."):
                                success, response = upload_submission(
                                    st.session_state.token,
                                    assignment['id'],
                                    uploaded_file
                                )
                                
                                if success:
                                    st.session_state.flash_message = ("success", "✅ Archivo subido exitosamente!")
                                    st.rerun()
                                else:
                                    st.error(f"❌ Error: {response.get('detail', 'Error desconocido')}")
                
                # Información extra para profesores
                if is_teacher:
                    st.markdown("### 📥 Entregas de Estudiantes")
                    submissions = get_assignment_submissions(st.session_state.token, assignment['id'])
                    
                    if submissions:
                        st.write(f"Total entregas: {len(submissions)}")
                        
                        for sub in submissions:
                            with st.container():
                                col_sub1, col_sub2, col_sub3 = st.columns([2, 1, 1])
                                with col_sub1:
                                    st.write(f"👤 **{sub['student']['full_name']}**")
                                    st.caption(f"Fecha: {sub['submitted_at_date'][:16].replace('T', ' ')}")
                                
                                with col_sub2:
                                    if sub['late']:
                                        st.warning("⏰ Tardía")
                                    else:
                                        st.success("✅ A tiempo")
                                
                                with col_sub3:
                                    # Generar URL de descarga directa
                                    # Fix for Docker environment:
                                    base_url = API_URL.rstrip("/")
                                    if "backend" in base_url:
                                         base_url = base_url.replace("backend", "localhost")
                                    
                                    download_url = f"{base_url}/api/submissions/{sub['id']}/download?token={st.session_state.token}"
                                    
                                    st.link_button("📥 Descargar", download_url)
                            
                            # Formulario de calificación
                            with st.popover(f"📝 Calificar a {sub['student']['full_name']}"):
                                with st.form(f"grade_form_{sub['id']}"):
                                    g_col1, g_col2 = st.columns(2)
                                    with g_col1:
                                        current_grade = sub['grade'] if sub['grade'] is not None else 0.0
                                        new_grade = st.number_input(
                                            f"Nota (Max: {assignment['max_score']})", 
                                            min_value=0.0, 
                                            max_value=float(assignment['max_score']),
                                            value=float(current_grade),
                                            key=f"grade_input_{sub['id']}"
                                        )
                                    with g_col2:
                                        st.write(f"**Estado:** {'Calificado' if sub['grade'] is not None else 'Pendiente'}")
                                        if sub['graded_by_name']:
                                            st.caption(f"Por: {sub['graded_by_name']}")
                                    
                                    new_feedback = st.text_area(
                                        "Feedback / Comentarios", 
                                        value=sub['feedback_char'] if sub['feedback_char'] else "",
                                        key=f"feedback_{sub['id']}"
                                    )
                                    
                                    if st.form_submit_button("Guardar Calificación"):
                                        grade_data = {
                                            "grade": new_grade,
                                            "feedback_char": new_feedback,
                                            "graded_by_id": user['id']
                                        }
                                        
                                        with st.spinner("Guardando nota..."):
                                            success, res = grade_submission_api(st.session_state.token, sub['id'], grade_data)
                                            if success:
                                                st.session_state.flash_message = ("success", f"✅ Nota guardada para {sub['student']['full_name']}")
                                                st.rerun()
                                            else:
                                                st.error(f"Error: {res.get('detail')}")

                            st.divider()
                    else:
                        st.info("No hay entregas para esta tarea aún.")
    else:
        st.info("No hay tareas disponibles")


def show_submissions():
    st.title("📤 Mis Entregas")
    
    submissions = get_my_submissions(st.session_state.token)
    
    if submissions:
        for submission in submissions:
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.subheader(submission['assignment']['title'])
                    st.caption(f"Curso: {submission['assignment']['course_code']}")
                    st.write(f"📅 Entregado: {submission['submitted_at_date']}")
                
                with col2:
                    if submission['late']:
                        st.warning("⏰ Tardía")
                    else:
                        st.success("✅ A tiempo")
                
                with col3:
                    if submission['grade'] is not None:
                        st.metric("Nota", f"{submission['grade']}/{submission['assignment']['max_score']}")
                    else:
                        st.info("Sin calificar")
                
                # Botón de descarga
                # Generar URL de descarga directa
                base_url = API_URL.rstrip("/")
                if "backend" in base_url:
                        base_url = base_url.replace("backend", "localhost")
                
                download_url = f"{base_url}/api/submissions/{submission['id']}/download?token={st.session_state.token}"
                
                st.link_button("📥 Descargar", download_url)
                
                # Feedback
                if submission['feedback_char']:
                    st.info(f"💬 Feedback: {submission['feedback_char']}")
                
                st.markdown("---")
    else:
        st.info("No has realizado entregas todavía")


def show_grades():
    st.title("📊 Mis Calificaciones")
    
    submissions = get_my_submissions(st.session_state.token)
    graded = [s for s in submissions if s['grade'] is not None]
    
    if graded:
        # Tabla de calificaciones
        import pandas as pd
        
        data = {
            "Curso": [s['assignment']['course_code'] for s in graded],
            "Tarea": [s['assignment']['title'] for s in graded],
            "Nota": [s['grade'] for s in graded],
            "Máximo": [s['assignment']['max_score'] for s in graded],
            "Porcentaje": [f"{(s['grade']/s['assignment']['max_score']*100):.1f}%" for s in graded]
        }
        
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True)
        
        # Estadísticas
        avg_percentage = sum(s['grade']/s['assignment']['max_score'] for s in graded) / len(graded) * 100
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Promedio General", f"{avg_percentage:.1f}%")
        
        with col2:
            st.metric("Tareas Calificadas", len(graded))
        
        with col3:
            pending = len([s for s in submissions if s['grade'] is None])
            st.metric("Pendientes de Calificar", pending)
    else:
        st.info("Aún no tienes calificaciones")


def show_profile():
    st.title("👤 Mi Perfil")
    
    user = st.session_state.user
    
    if user is None:
        st.error("No se pudo cargar la información del usuario")
        return

    col1, col2 = st.columns([1, 2])
    
    with col1:
        if user.get('profile_pic_url'):
            base_url = API_URL.rstrip("/")
            # Fix for Docker environment:
            # API_URL might be http://backend:8000 which is not accessible from browser
            # We need to replace it with localhost or the public URL
            if "backend" in base_url:
                 base_url = base_url.replace("backend", "localhost")
            
            image_url = f"{base_url}{user['profile_pic_url']}"
            st.image(image_url, width=200)
        else:
            st.image("https://via.placeholder.com/200", width=200)
        st.caption("Foto de perfil")
    
    with col2:
        st.subheader(user.get('full_name', 'Usuario'))
        st.write(f"**Usuario:** {user.get('username', 'N/A')}")
        st.write(f"**Rol:** {user.get('role', 'N/A')}")
        st.write(f"**Miembro desde:** {user.get('joined_date', 'N/A')}")

    st.markdown("---")
    st.subheader("✏️ Editar Información")
    
    with st.form("edit_profile_form"):
        col_a, col_b = st.columns(2)
        
        with col_a:
            new_first_name = st.text_input("Nombre", value=user.get('first_name', ''))
            new_last_name = st.text_input("Apellido", value=user.get('last_name', ''))
            new_email = st.text_input("Email", value=user.get('email', ''))
        
        with col_b:
            new_phone = st.text_input("Teléfono", value=user.get('phone') or '')
            new_middle_name = st.text_input("Segundo Nombre", value=user.get('middle_name') or '')
            # new_birthdate = st.date_input("Fecha de Nacimiento", value=user.get('birtdate')) # Requiere manejo de fechas
        
        st.markdown("### Cambiar Foto")
        new_profile_pic = st.file_uploader("Subir nueva foto", type=['png', 'jpg', 'jpeg'])
        
        submit_update = st.form_submit_button("Guardar Cambios")
        
        if submit_update:
            update_data = {
                "first_name": new_first_name,
                "last_name": new_last_name,
                "email": new_email,
                "phone": new_phone if new_phone else None,
                "middle_name": new_middle_name if new_middle_name else None
            }
            
            with st.spinner("Actualizando perfil..."):
                success, result = update_user_profile(
                    st.session_state.token, 
                    user['id'], 
                    update_data,
                    profile_pic_file=new_profile_pic
                )
                
                if success:
                    # Actualizar sesión con datos frescos del servidor
                    updated_user = get_current_user(st.session_state.token)
                    if updated_user:
                        st.session_state.user = updated_user
                    else:
                        st.session_state.user = result
                        
                    st.session_state.flash_message = ("success", "✅ Perfil actualizado exitosamente!")
                    st.rerun()
                else:
                    st.error(f"❌ Error: {result.get('detail', 'Error desconocido')}")


def show_admin_panel():
    st.title("🛠️ Panel de Administración")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Crear Usuario", "Crear Curso", "Inscripciones", "Gestión de Usuarios", "Gestión de Cursos"])
    
    with tab1:
        st.subheader("Registrar Nuevo Usuario")
        
        with st.form("create_user_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                new_username = st.text_input("Nombre de Usuario")
                new_email = st.text_input("Email")
                new_password = st.text_input("Contraseña", type="password")
                new_password_confirm = st.text_input("Confirmar Contraseña", type="password")
            
            with col2:
                new_first_name = st.text_input("Nombre")
                new_last_name = st.text_input("Apellido")
                new_role = st.selectbox("Rol", ["student", "teacher", "admin"])
                new_carnet = st.text_input("Carnet (Solo estudiantes)")
            
            submit_create = st.form_submit_button("Crear Usuario")
            
            if submit_create:
                if new_password != new_password_confirm:
                    st.error("❌ Las contraseñas no coinciden")
                elif not new_username or not new_email or not new_password:
                    st.warning("⚠️ Por favor completa los campos obligatorios")
                else:
                    user_data = {
                        "username": new_username,
                        "email": new_email,
                        "password": new_password,
                        "password_confirm": new_password_confirm,
                        "first_name": new_first_name,
                        "last_name": new_last_name,
                        "role": new_role,
                        "carnet": new_carnet if new_carnet else None
                    }
                    
                    with st.spinner("Creando usuario..."):
                        success, result = create_user(st.session_state.token, user_data)
                        
                        if success:
                            st.success(f"✅ Usuario {new_username} creado exitosamente!")
                        else:
                            st.error(f"❌ Error: {result.get('detail', 'Error desconocido')}")

    with tab2:
        st.subheader("Registrar Nuevo Curso")
        
        # Obtener profesores para el selectbox
        teachers = get_teachers(st.session_state.token)
        teacher_options = {t['id']: f"{t['full_name']} ({t['email']})" for t in teachers}
        
        with st.form("create_course_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                c_title = st.text_input("Nombre del Curso")
                c_code = st.text_input("Código (ej. PROG101)")
                c_credits = st.number_input("Créditos", min_value=1, max_value=10, value=4)
                c_semester = st.number_input("Semestre", min_value=1, max_value=12, value=1)
                c_start_date = st.date_input("Fecha de Inicio")
            
            with col2:
                c_schedule = st.text_input("Horario (ej. Lun/Mie 10:00)")
                c_classroom = st.text_input("Aula")
                c_max_students = st.number_input("Cupo Máximo", min_value=1, value=30)
                c_end_date = st.date_input("Fecha de Finalización")
                
                if teachers:
                    c_teacher_id = st.selectbox(
                        "Profesor Asignado",
                        options=list(teacher_options.keys()),
                        format_func=lambda x: teacher_options[x]
                    )
                else:
                    st.warning("No hay profesores registrados. Crea uno primero.")
                    c_teacher_id = None

            c_description = st.text_area("Descripción")
            
            submit_course = st.form_submit_button("Crear Curso")
            
            if submit_course:
                if not c_title or not c_code or not c_teacher_id:
                    st.warning("⚠️ Completa los campos obligatorios (Título, Código, Profesor)")
                elif c_end_date <= c_start_date:
                    st.error("⚠️ La fecha de finalización debe ser posterior a la de inicio")
                else:
                    course_data = {
                        "title": c_title,
                        "code": c_code,
                        "description": c_description,
                        "credits": c_credits,
                        "semester": c_semester,
                        "schedule": c_schedule,
                        "classroom": c_classroom,
                        "max_students": c_max_students,
                        "teacher_id": c_teacher_id,
                        "start_date": c_start_date.isoformat(),
                        "end_date": c_end_date.isoformat()
                    }
                    
                    with st.spinner("Creando curso..."):
                        success, result = create_course_api(st.session_state.token, course_data)
                        
                        if success:
                            st.success(f"✅ Curso {c_code} creado exitosamente y asignado al profesor.")
                        else:
                            st.error(f"❌ Error: {result.get('detail', 'Error desconocido')}")

    with tab3:
        st.subheader("Inscribir Estudiantes")
        
        # Obtener datos
        all_courses = get_all_courses(st.session_state.token)
        all_students = get_students(st.session_state.token)
        
        if not all_courses:
            st.warning("No hay cursos disponibles.")
        elif not all_students:
            st.warning("No hay estudiantes registrados.")
        else:
            course_opts = {c['id']: f"{c['code']} - {c['title']}" for c in all_courses}
            student_opts = {s['id']: f"{s['full_name']} ({s['carnet'] or 'S/C'})" for s in all_students}
            
            with st.form("enroll_student_form"):
                col1, col2 = st.columns(2)
                with col1:
                    selected_course_id = st.selectbox(
                        "Seleccionar Curso",
                        options=list(course_opts.keys()),
                        format_func=lambda x: course_opts[x]
                    )
                with col2:
                    selected_student_id = st.selectbox(
                        "Seleccionar Estudiante",
                        options=list(student_opts.keys()),
                        format_func=lambda x: student_opts[x]
                    )
                
                submit_enroll = st.form_submit_button("Inscribir Estudiante")
                
                if submit_enroll:
                    with st.spinner("Procesando inscripción..."):
                        success, res = enroll_student_api(st.session_state.token, selected_course_id, selected_student_id)
                        if success:
                            st.success(f"✅ Estudiante inscrito correctamente en el curso.")
                        else:
                            st.error(f"❌ Error: {res.get('detail', 'Error desconocido')}")

    with tab4:
        st.info("Funcionalidad de gestión de usuarios en desarrollo")

    with tab5:
        st.subheader("Administrar Cursos Existentes")
        all_courses = get_all_courses(st.session_state.token)
        teachers = get_teachers(st.session_state.token)
        teacher_options = {t['id']: f"{t['full_name']} ({t['email']})" for t in teachers}
        
        if all_courses:
            for course in all_courses:
                with st.expander(f"{course['code']} - {course['title']}"):
                    # Formulario de edición
                    with st.form(f"edit_course_{course['id']}"):
                        col1, col2 = st.columns(2)
                        with col1:
                            e_title = st.text_input("Nombre", value=course['title'])
                            e_code = st.text_input("Código", value=course['code'])
                            e_credits = st.number_input("Créditos", value=course['credits'])
                            
                            # Selector de profesor
                            st.write(f"**Profesor actual:** {course.get('teacher_name', 'N/A')}")
                            
                            if teacher_options:
                                current_teacher_index = 0
                                if course.get('teacher_id') in teacher_options:
                                    current_teacher_index = list(teacher_options.keys()).index(course['teacher_id'])
                                
                                e_teacher_id = st.selectbox(
                                    "Cambiar Profesor",
                                    options=list(teacher_options.keys()),
                                    format_func=lambda x: teacher_options[x],
                                    index=current_teacher_index,
                                    key=f"edit_teacher_{course['id']}"
                                )
                            else:
                                st.warning("No hay lista de profesores disponible.")
                                e_teacher_id = course.get('teacher_id')

                        with col2:
                            e_semester = st.number_input("Semestre", value=course['semester'])
                            e_schedule = st.text_input("Horario", value=course.get('schedule', ''))
                            e_classroom = st.text_input("Aula", value=course.get('classroom', ''))
                        
                        e_description = st.text_area("Descripción", value=course.get('description', ''))
                        
                        if st.form_submit_button("💾 Guardar Cambios"):
                            update_data = {
                                "title": e_title,
                                "code": e_code,
                                "credits": e_credits,
                                "semester": e_semester,
                                "schedule": e_schedule,
                                "classroom": e_classroom,
                                "description": e_description,
                                "teacher_id": e_teacher_id
                            }
                            with st.spinner("Actualizando..."):
                                success, res = update_course_api(st.session_state.token, course['id'], update_data)
                                if success:
                                    st.success("Curso actualizado")
                                    st.rerun()
                                else:
                                    st.error(f"Error: {res}")
                    
                    # Botón de eliminar fuera del form para evitar conflictos
                    col_del, _ = st.columns([1, 3])
                    with col_del:
                        if st.button("🗑️ Eliminar Curso", key=f"del_course_{course['id']}"):
                            with st.spinner("Eliminando..."):
                                success, res = delete_course_api(st.session_state.token, course['id'])
                                if success:
                                    st.success("Curso eliminado")
                                    st.rerun()
                                else:
                                    st.error(f"Error: {res}")
        else:
            st.info("No hay cursos registrados.")


# ==================== MAIN ====================

def main():
    if st.session_state.token is None:
        show_login()
    else:
        show_main_app()


if __name__ == "__main__":
    main()