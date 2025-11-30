import streamlit as st
import requests
import os
import pandas as pd # Necesario para tablas bonitas
from streamlit_autorefresh import st_autorefresh
from datetime import datetime
from streamlit_option_menu import option_menu

# Configuración de la página
st.set_page_config(
    page_title="Maruchan University",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed" # Colapsado al inicio para la landing page
)

# URL de la API
API_URL = os.getenv("API_URL", "http://localhost:8000")

# --- ESTILOS CSS MEJORADOS Y COMBINADOS ---

st.markdown("""
    <style>
    /* --- ANIMACIONES --- */
    @keyframes gradient-animation {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    @keyframes slide-up {
        from { transform: translateY(20px); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
    }

    /* --- ESTILOS GENERALES --- */
    .main-header {
        font-size: 4rem;
        font-weight: 900;
        background: linear-gradient(270deg, #e63946, #fca311, #e63946);
        background-size: 200% 200%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: gradient-animation 3s ease infinite;
        text-align: center;
        margin-bottom: 0.5rem;
        padding-top: 1rem;
    }

    .sub-header {
        font-size: 1.6rem;
        font-weight: 300;
        color: var(--text-color);
        text-align: center;
        margin-bottom: 3rem;
        opacity: 0.9;
    }

    /* Tarjetas */
    .feature-card {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(128, 128, 128, 0.2);
        padding: 30px;
        border-radius: 16px;
        border-top: 4px solid #e63946;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        height: 100%;
        transition: all 0.3s ease;
        animation: slide-up 0.8s ease-out;
    }
    
    .feature-card:hover {
        transform: translateY(-8px);
        background-color: rgba(255, 255, 255, 0.1);
        border-top: 4px solid #fca311;
    }
    
    .card-icon { font-size: 2.5rem; margin-bottom: 15px; display: block; }

    /* --- SISTEMA DE COLORES DE BOTONES --- */
    
    /* Reglas base para TODOS los botones */
    .stButton > button {
        border-radius: 25px;
        font-weight: bold;
        width: 100%;
        padding-top: 10px;
        padding-bottom: 10px;
        transition: transform 0.2s, box-shadow 0.2s;
        border: none !important;
        color: white !important; /* Texto blanco siempre */
    }
    .stButton > button:hover { transform: scale(1.03); }

    /* 1. ROJO (type="primary"): Eliminar, Salir, Desactivar */
    div.stButton > button[kind="primary"] {
        background: linear-gradient(90deg, #d90429 0%, #ef233c 100%);
        box-shadow: 0 4px 6px rgba(217, 4, 41, 0.3);
    }
    div.stButton > button[kind="primary"]:hover {
        background: linear-gradient(90deg, #b00020 0%, #d90429 100%);
    }

    /* 2. AZUL (type="secondary" - Default): Editar, Guardar Cambios, Botones generales */
    div.stButton > button[kind="secondary"] {
        background: linear-gradient(90deg, #0077b6 0%, #0096c7 100%);
        box-shadow: 0 4px 6px rgba(0, 119, 182, 0.3);
    }
    div.stButton > button[kind="secondary"]:hover {
        background: linear-gradient(90deg, #023e8a 0%, #0077b6 100%);
    }

    /* 3. VERDE (Clase personalizada): Crear, Inscribir, Enviar Tarea */
    /* Truco: Busca el span invisible .btn-green justo antes del botón */
    .btn-green + div.stButton > button {
        background: linear-gradient(90deg, #2a9d8f 0%, #264653 100%) !important;
        box-shadow: 0 4px 6px rgba(42, 157, 143, 0.3) !important;
    }

    /* 4. ESPECIAL (Clase personalizada): Login, Inicio */
    .btn-special + div.stButton > button {
        background: linear-gradient(270deg, #e63946, #fca311, #e63946) !important;
        background-size: 200% 200% !important;
        animation: gradient-animation 3s ease infinite !important;
        box-shadow: 0 4px 10px rgba(230, 57, 70, 0.4) !important;
        font-size: 1.1rem !important;
    }

    /* Extra: Botones de enlace (Descargas) en Azul también */
    .stLinkButton > a {
        background: linear-gradient(90deg, #48cae4 0%, #0077b6 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 25px !important;
        font-weight: bold !important;
        text-align: center !important;
    }
    
    </style>
""", unsafe_allow_html=True)

# ==================== FUNCIONES DE API ====================


def set_btn_style(style="green"):
    """
    Inyecta una marca invisible para que el CSS pinte el siguiente botón.
    Opciones: 'green' (Crear/Éxito), 'special' (Animado).
    """
    style_class = "btn-green" if style == "green" else "btn-special"
    st.markdown(f'<span class="{style_class}"></span>', unsafe_allow_html=True)

def change_password_api(token: str, user_id: int, new_password: str):
    """Llama al endpoint de cambio de contraseña"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        data = {
            "password": new_password,
            "password_confirm": new_password
        }
        response = requests.patch(
            f"{API_URL}/api/users/{user_id}/password",
            headers=headers,
            json=data
        )
        if response.status_code == 200:
            return True, response.json()
        return False, response.json()
    except Exception as e:
        return False, {"detail": str(e)}

def get_admins(token):
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{API_URL}/api/users/?role=admin", headers=headers)
        if response.status_code == 200:
            return response.json()
        return []
    except: return []
    
def update_user_admin_api(token: str, user_id: int, user_data: dict):
    """Permite al admin editar cualquier usuario"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.put(f"{API_URL}/api/users/{user_id}", headers=headers, json=user_data)
        if response.status_code == 200:
            return True, response.json()
        return False, response.json()
    except Exception as e:
        return False, {"detail": str(e)}

def delete_user_api(token: str, user_id: int):
    """Permite al admin eliminar un usuario permanentemente"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.delete(f"{API_URL}/api/users/{user_id}", headers=headers)
        if response.status_code == 200:
            return True, response.json()
        return False, response.json()
    except Exception as e:
        return False, {"detail": str(e)}

def get_online_users_api(token):
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{API_URL}/api/chat/users/online", headers=headers)
        return response.json() if response.status_code == 200 else []
    except: return []

def send_message_api(token, receiver_id, content):
    try:
        headers = {"Authorization": f"Bearer {token}"}
        data = {"receiver_id": receiver_id, "content": content}
        response = requests.post(f"{API_URL}/api/chat/send", headers=headers, json=data)
        return response.status_code == 200
    except: return False

def get_chat_history_api(token, other_user_id):
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{API_URL}/api/chat/history/{other_user_id}", headers=headers)
        return response.json() if response.status_code == 200 else []
    except: return []

def get_all_users(token: str):
    """Obtiene todos los usuarios para el admin"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{API_URL}/api/users/", headers=headers)
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        st.error(f"Error obteniendo usuarios: {e}")
        return []

def toggle_user_active_api(token: str, user_id: int):
    """Activa/Desactiva un usuario"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.patch(f"{API_URL}/api/users/{user_id}/toggle-active", headers=headers)
        return response.status_code == 200, response.json()
    except Exception as e:
        return False, {"detail": str(e)}

def login(username, password):
    try:
        response = requests.post(f"{API_URL}/api/auth/login", data={"username": username, "password": password})
        if response.status_code == 200: return response.json()
    except: return None
    return None

def get_current_user(token):
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{API_URL}/api/auth/me", headers=headers)
        if response.status_code == 200: return response.json()
    except: return None
    return None

def get_my_courses(token):
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{API_URL}/api/courses/my-courses", headers=headers)
        if response.status_code == 200: return response.json()
        return []
    except Exception as e: return []

def upload_submission(token, assignment_id, file):
    try:
        headers = {"Authorization": f"Bearer {token}"}
        files = {"file": (file.name, file, file.type)}
        data = {"assignment_id": assignment_id}
        response = requests.post(f"{API_URL}/api/submissions/upload", headers=headers, files=files, data=data)
        return response.status_code == 201, response.json()
    except Exception as e: return False, {"detail": str(e)}

def download_submission(token, submission_id):
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{API_URL}/api/submissions/{submission_id}/download", headers=headers)
        if response.status_code == 200: return response.content
        return None
    except Exception as e: return None

def get_assignments(token, course_id=None):
    try:
        headers = {"Authorization": f"Bearer {token}"}
        params = {"course_id": course_id} if course_id else {}
        response = requests.get(f"{API_URL}/api/assignments/", headers=headers, params=params)
        if response.status_code == 200: return response.json()
        return []
    except Exception as e: return []

def get_assignment_submissions(token, assignment_id):
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{API_URL}/api/submissions/?assignment_id={assignment_id}", headers=headers)
        if response.status_code == 200: return response.json()
        return []
    except Exception as e: return []

def grade_submission_api(token, submission_id, grade_data):
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.patch(f"{API_URL}/api/submissions/{submission_id}/grade", headers=headers, json=grade_data)
        if response.status_code == 200: return True, response.json()
        return False, response.json()
    except Exception as e: return False, {"detail": str(e)}

def get_my_submissions(token):
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{API_URL}/api/submissions/my-submissions", headers=headers)
        if response.status_code == 200: return response.json()
        return []
    except Exception as e: return []

def create_assignment(token, assignment_data):
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(f"{API_URL}/api/assignments/", headers=headers, json=assignment_data)
        if response.status_code == 201: return True, response.json()
        return False, response.json()
    except Exception as e: return False, {"detail": str(e)}

def update_user_profile(token, user_id, user_data, profile_pic_file=None):
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.put(f"{API_URL}/api/users/{user_id}", headers=headers, json=user_data)
        if response.status_code != 200: return False, response.json()
        updated_user = response.json()
        if profile_pic_file:
            profile_pic_file.seek(0)
            files = {"file": (profile_pic_file.name, profile_pic_file, profile_pic_file.type)}
            img_response = requests.post(f"{API_URL}/api/users/{user_id}/profile-picture", headers=headers, files=files)
            if img_response.status_code == 200: updated_user = img_response.json()
            else: return False, {"detail": "Error en imagen"}
        return True, updated_user
    except Exception as e: return False, {"detail": str(e)}

def create_user(token, user_data):
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(f"{API_URL}/api/users/", headers=headers, json=user_data)
        if response.status_code == 201: return True, response.json()
        return False, response.json()
    except Exception as e: return False, {"detail": str(e)}

def get_teachers(token):
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{API_URL}/api/users/?role=teacher", headers=headers)
        if response.status_code == 200: return response.json()
        return []
    except Exception as e: return []

def create_course_api(token, course_data):
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(f"{API_URL}/api/courses/", headers=headers, json=course_data)
        if response.status_code == 201: return True, response.json()
        return False, response.json()
    except Exception as e: return False, {"detail": str(e)}

def get_all_courses(token):
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{API_URL}/api/courses/", headers=headers)
        if response.status_code == 200: return response.json()
        return []
    except Exception as e: return []

def update_course_api(token, course_id, course_data):
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.put(f"{API_URL}/api/courses/{course_id}", headers=headers, json=course_data)
        if response.status_code == 200: return True, response.json()
        return False, response.json()
    except Exception as e: return False, {"detail": str(e)}

def delete_course_api(token, course_id):
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.delete(f"{API_URL}/api/courses/{course_id}", headers=headers)
        if response.status_code == 200: return True, response.json()
        return False, response.json()
    except Exception as e: return False, {"detail": str(e)}

def get_students(token):
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{API_URL}/api/users/?role=student", headers=headers)
        if response.status_code == 200: return response.json()
        return []
    except Exception as e: return []

def enroll_student_api(token, course_id, student_id):
    try:
        headers = {"Authorization": f"Bearer {token}"}
        data = {"student_id": student_id, "course_id": course_id}
        response = requests.post(f"{API_URL}/api/enrollments/", headers=headers, json=data)
        if response.status_code == 201: return True, response.json()
        return False, response.json()
    except Exception as e: return False, {"detail": str(e)}

def get_course_enrollments(token, course_id):
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{API_URL}/api/enrollments/?course_id={course_id}&status=enrolled", headers=headers)
        if response.status_code == 200: return response.json()
        return []
    except Exception as e: return []


# ==================== GESTIÓN DE ESTADO ====================

if "token" not in st.session_state:
    st.session_state.token = None
if "user" not in st.session_state:
    st.session_state.user = None
if "flash_message" not in st.session_state:
    st.session_state.flash_message = None
if "page" not in st.session_state:
    st.session_state.page = "landing" # Nueva variable para controlar la navegación

# ==================== LANDING PAGE ====================

def show_landing_page():
    st.write("") 
    st.markdown('<h1 class="main-header">🍜 Maruchan University</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-header">Formación académica lista en 3 minutos. <br>Nútrete de conocimiento.</p>', 
        unsafe_allow_html=True
    )
    
    with st.container():
        _, col_img, _ = st.columns([1, 6, 1]) 
        with col_img:
            st.image(
                "https://images.unsplash.com/photo-1523240795612-9a054b0db644?q=80&w=1470&auto=format&fit=crop", 
                caption="Campus Virtual de Alta Velocidad",
                use_column_width=True
            )
        
        st.write("")
        
        col_b1, col_b2, col_b3 = st.columns([1, 2, 1])
        with col_b2:
            st.markdown("### 🚀 Comienza tu viaje ahora")
            # BOTÓN ESPECIAL ANIMADO
            set_btn_style("special")
            if st.button("🔐 Acceder al Portal Estudiantil", use_container_width=True):
                st.session_state.page = "login"
                st.rerun()
            
    st.markdown("---")
    
    st.subheader("🎓 ¿Por qué elegirnos?")
    st.write("Olvídate de la burocracia. Aquí nos enfocamos en resultados inmediatos.")
    st.write("")
    
    c1, c2, c3 = st.columns(3, gap="medium")
    
    with c1:
        st.markdown("""
        <div class="feature-card">
            <span class="card-icon">⚡</span>
            <h3>Metodología Ágil</h3>
            <p>¿4 años de carrera? Aquí aprendes lo esencial mientras hierves el agua.</p>
        </div>""", unsafe_allow_html=True)
        
    with c2:
        st.markdown("""
        <div class="feature-card">
            <span class="card-icon">🌍</span>
            <h3>Global Networking</h3>
            <p>Conecta con una comunidad de "Noodle-Thinkers" alrededor del mundo.</p>
        </div>""", unsafe_allow_html=True)
        
    with c3:
        st.markdown("""
        <div class="feature-card">
            <span class="card-icon">🏆</span>
            <h3>Prestigio Instantáneo</h3>
            <p>Obtén certificaciones digitales verificables al instante.</p>
        </div>""", unsafe_allow_html=True)
    st.write("")

# ==================== PANEL DE ADMIN  ====================

import streamlit as st
import pandas as pd
# Asegúrate de importar tus funciones de API aquí (get_all_users, create_course_api, etc.)

# --- FUNCIÓN AUXILIAR PARA ESTILOS (BOTÓN VERDE) ---
def set_btn_style(color="green"):
    """
    Inyecta CSS para cambiar el color del siguiente botón primario o secundario renderizado.
    """
    color_map = {
        "green": {"bg": "#28a745", "hover": "#218838", "font": "white"},
        "blue":  {"bg": "#007bff", "hover": "#0069d9", "font": "white"},
    }
    style = color_map.get(color, color_map["green"])
    
    st.markdown(f"""
        <style>
        div.stButton > button:first-child {{
            background-color: {style['bg']} !important;
            color: {style['font']} !important;
            border-color: {style['bg']} !important;
        }}
        div.stButton > button:first-child:hover {{
            background-color: {style['hover']} !important;
            border-color: {style['hover']} !important;
        }}
        </style>
    """, unsafe_allow_html=True)

# --- FUNCIÓN PRINCIPAL DEL PANEL ---
def show_admin_panel():
    st.title("🛠️ Panel de Administración")
    st.info("Bienvenido al centro de control de Maruchan University.")
    
    tabs = st.tabs(["👥 Gestión de Usuarios", "📚 Cursos", "📝 Inscripciones", "➕ Crear Usuario"])
    
    # ==========================================
    # TAB 1: GESTIÓN DE USUARIOS
    # ==========================================
    with tabs[0]:
        st.subheader("Directorio de Usuarios")
        col_f1, col_f2 = st.columns([3, 1])
        with col_f1:
            search = st.text_input("🔍 Buscar por nombre...", placeholder="Ej: Juan Pérez")
        with col_f2:
            role_filter = st.selectbox("Filtrar por Rol", ["Todos", "student", "teacher", "admin"])
        
        users = get_all_users(st.session_state.token)
        
        if users:
            df = pd.DataFrame(users)
            if not df.empty:
                # Procesamiento visual
                df['Estado'] = df['is_active'].apply(lambda x: '🟢 Activo' if x else '🔴 Inactivo')
                
                # Filtros
                if role_filter != "Todos": 
                    df = df[df['role'] == role_filter]
                if search: 
                    df = df[df['full_name'].str.contains(search, case=False) | df['email'].str.contains(search, case=False)]
                
                # Tabla Principal
                st.dataframe(
                    df[['id', 'full_name', 'email', 'role', 'carnet', 'Estado']], 
                    use_container_width=True, 
                    hide_index=True
                )
                
                st.markdown("---")
                st.subheader("🔧 Acciones de Usuario")
                
                user_options = df['id'].tolist()
                if user_options:
                    user_labels = {uid: f"{df[df['id']==uid]['full_name'].values[0]} ({df[df['id']==uid]['role'].values[0]})" for uid in user_options}
                    selected_uid = st.selectbox("Seleccionar Usuario:", options=user_options, format_func=lambda x: user_labels[x])
                    current_u_data = df[df['id'] == selected_uid].iloc[0]
                    
                    col_edit, col_state, col_pass, col_delete = st.columns(4)
                    
                    # 1. EDITAR (Azul - Default)
                    with col_edit:
                        with st.popover("✏️ Editar Datos", use_container_width=True):
                            st.markdown(f"**Editando a:** {current_u_data['full_name']}")
                            with st.form(f"edit_user_{selected_uid}"):
                                new_name = st.text_input("Nombre", value=current_u_data.get('first_name', ''))
                                new_last = st.text_input("Apellido", value=current_u_data.get('last_name', ''))
                                new_email = st.text_input("Email", value=current_u_data['email'])
                                new_phone = st.text_input("Teléfono", value=current_u_data.get('phone', ''))
                                
                                # Botón AZUL (Secondary por defecto)
                                if st.form_submit_button("Guardar Cambios", type="secondary"):
                                    update_data = {"first_name": new_name, "last_name": new_last, "email": new_email, "phone": new_phone}
                                    with st.spinner("Actualizando..."):
                                        success, res = update_user_admin_api(st.session_state.token, selected_uid, update_data)
                                        if success:
                                            st.session_state.flash_message = ("success", "✅ Usuario actualizado")
                                            st.rerun()
                                        else: st.error(f"Error: {res.get('detail')}")

                    # 2. ESTADO (Rojo/Azul según estado)
                    with col_state:
                        is_active = current_u_data['is_active']
                        btn_label = "Desactivar Cuenta 🔴" if is_active else "Activar Cuenta 🟢"
                        # ROJO si desactiva, AZUL si activa
                        btn_type = "primary" if is_active else "secondary"
                        
                        if st.button(btn_label, use_container_width=True, type=btn_type):
                            success, msg = toggle_user_active_api(st.session_state.token, selected_uid)
                            if success:
                                st.session_state.flash_message = ("success", f"✅ Estado cambiado: {msg.get('message')}")
                                st.rerun()
                            else: st.error(msg.get('detail'))

                    # 3. RESET PASS (Azul)
                    with col_pass:
                        with st.popover("🔑 Reset Pass", use_container_width=True):
                            with st.form(f"reset_pass_{selected_uid}", clear_on_submit=True):
                                new_p = st.text_input("Nueva contraseña", type="password")
                                if st.form_submit_button("Cambiar", type="secondary"):
                                    if len(new_p) < 8: st.error("Mínimo 8 caracteres")
                                    else:
                                        success, msg = change_password_api(st.session_state.token, selected_uid, new_p)
                                        if success: st.success("✅ Contraseña restablecida")
                                        else: st.error(msg.get('detail'))

                    # 4. ELIMINAR (Rojo - Primary)
                    with col_delete:
                        with st.popover("🗑️ Eliminar", use_container_width=True):
                            st.error(f"¿Eliminar a **{current_u_data['full_name']}**?")
                            st.warning("Esta acción borrará notas y entregas.")
                            
                            if st.button("Sí, Eliminar", type="primary"):
                                if selected_uid == st.session_state.user['id']:
                                    st.error("No puedes auto-eliminarte")
                                else:
                                    success, res = delete_user_api(st.session_state.token, selected_uid)
                                    if success:
                                        st.session_state.flash_message = ("success", "✅ Usuario eliminado")
                                        st.rerun()
                                    else: st.error(res.get('detail'))
        else: st.warning("No se encontraron usuarios.")

    # ==========================================
    # TAB 2: GESTIÓN DE CURSOS
    # ==========================================
    with tabs[1]:
        st.subheader("Gestión de Cursos")
        
        # --- CREAR CURSO (Botón Verde) ---
        with st.expander("➕ Registrar Nuevo Curso"):
            teachers = get_teachers(st.session_state.token)
            teacher_options = {t['id']: f"{t['full_name']} ({t['email']})" for t in teachers}
            
            with st.form("create_course_form", clear_on_submit=True):
                c1, c2 = st.columns(2)
                with c1:
                    c_title = st.text_input("Nombre")
                    c_code = st.text_input("Código")
                    c_credits = st.number_input("Créditos", 1, 10, 4)
                    c_semester = st.number_input("Semestre", 1, 12, 1)
                    c_start_date = st.date_input("Inicio")
                with c2:
                    c_schedule = st.text_input("Horario")
                    c_classroom = st.text_input("Aula")
                    c_max_students = st.number_input("Cupo", 1, 100, 30)
                    c_end_date = st.date_input("Fin")
                    if teachers:
                        c_teacher_id = st.selectbox("Profesor", options=list(teacher_options.keys()), format_func=lambda x: teacher_options[x]) 
                    else:
                        st.warning("No hay profesores.")
                        c_teacher_id = None
                
                c_desc = st.text_area("Descripción")
                
                # APLICAMOS ESTILO VERDE AL BOTÓN DE CREAR
                set_btn_style("green")
                if st.form_submit_button("Crear Curso"):
                    if c_title and c_teacher_id:
                        data = {"title": c_title, "code": c_code, "credits": c_credits, "semester": c_semester, 
                                "start_date": c_start_date.isoformat(), "end_date": c_end_date.isoformat(),
                                "schedule": c_schedule, "classroom": c_classroom, "max_students": c_max_students,
                                "teacher_id": c_teacher_id, "description": c_desc}
                        success, res = create_course_api(st.session_state.token, data)
                        if success: 
                            st.session_state.flash_message = ("success", "✅ Curso creado exitosamente!")
                            st.rerun()
                        else: st.error(f"Error: {res}")
                    else: st.warning("Faltan datos obligatorios")

        # --- LISTADO / EDICIÓN ---
        st.markdown("---")
        st.write("### ✏️ Editar / Eliminar Cursos")
        all_courses = get_all_courses(st.session_state.token)
        
        if all_courses:
            for course in all_courses:
                with st.expander(f"📘 {course['code']} - {course['title']}"):
                    with st.form(f"edit_course_{course['id']}"):
                        ec1, ec2 = st.columns(2)
                        with ec1:
                            e_title = st.text_input("Nombre", value=course['title'])
                            e_code = st.text_input("Código", value=course['code'])
                            e_credits = st.number_input("Créditos", value=course['credits'])
                            
                            # Lógica para seleccionar el profesor actual
                            current_idx = 0
                            if teacher_options and course.get('teacher_id') in teacher_options:
                                current_idx = list(teacher_options.keys()).index(course['teacher_id'])
                            
                            e_teacher_id = st.selectbox("Profesor", options=list(teacher_options.keys()), 
                                                        index=current_idx, 
                                                        format_func=lambda x: teacher_options[x],
                                                        key=f"sel_t_{course['id']}")
                        with ec2:
                            e_semester = st.number_input("Semestre", value=course['semester'])
                            e_schedule = st.text_input("Horario", value=course.get('schedule', ''))
                            e_classroom = st.text_input("Aula", value=course.get('classroom', ''))
                            e_max_students = st.number_input("Cupo", value=course.get('max_students', 30))
                        
                        e_desc = st.text_area("Descripción", value=course.get('description', ''))
                        
                        # Botón secundario para guardar (Azul/Gris)
                        if st.form_submit_button("💾 Guardar Cambios", type="secondary", use_container_width=True):
                            update_data = {
                                "title": e_title, "code": e_code, "credits": e_credits,
                                "semester": e_semester, "schedule": e_schedule, "classroom": e_classroom,
                                "description": e_desc, "teacher_id": e_teacher_id, "max_students": e_max_students
                            }
                            success, res = update_course_api(st.session_state.token, course['id'], update_data)
                            if success:
                                st.session_state.flash_message = ("success", "✅ Curso actualizado")
                                st.rerun()
                            else: st.error(f"Error: {res}")

                    col_del, _ = st.columns([1, 3])
                    with col_del:
                        # Botón ROJO para eliminar
                        if st.button("🗑️ Eliminar Curso", key=f"del_course_{course['id']}", type="primary"):
                            success, res = delete_course_api(st.session_state.token, course['id'])
                            if success:
                                st.session_state.flash_message = ("success", "🗑️ Curso eliminado")
                                st.rerun()
                            else: st.error(res)

    # ==========================================
    # TAB 3: INSCRIPCIONES (Botón Verde)
    # ==========================================
    with tabs[2]:
        st.subheader("Inscribir Estudiantes")
        courses_list = get_all_courses(st.session_state.token)
        students_list = get_students(st.session_state.token)
        
        if courses_list and students_list:
            c_opts = {c['id']: f"{c['code']} - {c['title']}" for c in courses_list}
            s_opts = {s['id']: f"{s['full_name']} ({s['carnet'] or 'S/C'})" for s in students_list}
            
            with st.form("enroll_student_form_admin", clear_on_submit=True):
                col1, col2 = st.columns(2)
                with col1:
                    sel_c_id = st.selectbox("Curso", options=list(c_opts.keys()), format_func=lambda x: c_opts[x])
                with col2:
                    sel_s_id = st.selectbox("Estudiante", options=list(s_opts.keys()), format_func=lambda x: s_opts[x])
                
                # APLICAMOS ESTILO VERDE
                set_btn_style("green")
                if st.form_submit_button("Inscribir Estudiante"):
                    with st.spinner("Procesando..."):
                        success, res = enroll_student_api(st.session_state.token, sel_c_id, sel_s_id)
                        if success:
                            st.session_state.flash_message = ("success", "✅ Estudiante inscrito correctamente!")
                            st.rerun()
                        else: st.error(f"❌ Error: {res}")
        else:
            st.warning("Faltan datos de cursos o estudiantes.")

    # ==========================================
    # TAB 4: CREAR USUARIO (Botón Verde)
    # ==========================================
    with tabs[3]:
        st.subheader("Registrar Nuevo Miembro")
        with st.container(border=True):
            with st.form("create_user_form_polished", clear_on_submit=True):
                c1, c2 = st.columns(2)
                with c1:
                    new_username = st.text_input("Usuario")
                    new_email = st.text_input("Email Oficial")
                    new_pass = st.text_input("Contraseña", type="password")
                    new_pass2 = st.text_input("Confirmar Contraseña", type="password")
                with c2:
                    new_name = st.text_input("Nombre(s)")
                    new_lastname = st.text_input("Apellido(s)")
                    new_role = st.selectbox("Rol Institucional", ["student", "teacher", "admin"])
                    new_carnet = st.text_input("Carnet (Solo estudiantes)")
                
                # APLICAMOS ESTILO VERDE
                set_btn_style("green")
                submitted = st.form_submit_button("💾 Guardar Usuario en Base de Datos")
                
                if submitted:
                    if not new_username or not new_email or not new_pass:
                        st.warning("⚠️ Completa los campos obligatorios.")
                    elif new_pass != new_pass2:
                        st.error("❌ Las contraseñas no coinciden.")
                    else:
                        data = {
                            "username": new_username, "email": new_email, "password": new_pass,
                            "password_confirm": new_pass2, "first_name": new_name, "last_name": new_lastname,
                            "role": new_role, "carnet": new_carnet if new_carnet else None
                        }
                        with st.spinner("Creando usuario..."):
                            success, res = create_user(st.session_state.token, data)
                            if success:
                                st.session_state.flash_message = ("success", f"✅ Usuario {new_username} creado!")
                                st.rerun()
                            else: st.error(f"❌ Error: {res}")

# ==================== INTERFAZ DE CHAT ====================

def show_active_chat(selected_user_id, user_map, my_id):
    """
    Muestra el historial y el input con un botón manual de recarga.
    """
    target_user = user_map[selected_user_id]
    
    col_title, col_btn = st.columns([4, 1])
    
    with col_title:
        st.subheader(f"Chat con {target_user['full_name']}")
        
    with col_btn:
        # Botón para forzar la actualización inmediata
        if st.button("🔄 Actualizar", key="manual_refresh_chat", use_container_width=True):
            st.rerun()
    
    # --- CONTENEDOR DE MENSAJES ---
    chat_container = st.container(height=400)
    
    # Obtener historial REAL desde la API
    history = get_chat_history_api(st.session_state.token, selected_user_id)
    
    with chat_container:
        if not history:
            st.info("Aún no hay mensajes. ¡Sé el primero en saludar! 👋")
        else:
            for msg in history:
                is_me = msg['sender_id'] == my_id
                # Mostrar mensaje
                with st.chat_message("user" if is_me else "assistant", avatar="👤" if is_me else "🎓"):
                    st.write(msg['content'])
                    # Formato de hora simple
                    ts = msg['timestamp']
                    try:
                        time_str = ts.split("T")[1][:5]
                    except:
                        time_str = ts
                    st.caption(f"{time_str}")

    # --- INPUT DE MENSAJE ---
    if prompt := st.chat_input(f"Escribe a {target_user['full_name']}..."):
        if send_message_api(st.session_state.token, selected_user_id, prompt):
            st.rerun() # Recarga inmediata al enviar
        else:
            st.error("Error al enviar mensaje")

# ==================== VISTA PRINCIPAL DE COMUNIDAD (Mensajes) ====================

def show_chat_interface():
    st.title("💬 Comunidad Universitaria")
    
    # 1. Obtener datos necesarios (Esto NO se recarga solo, para no parpadear la lista)
    online_users = get_online_users_api(st.session_state.token)
    online_ids = [u['id'] for u in online_users]
    
    all_students = get_students(st.session_state.token)
    all_teachers = get_teachers(st.session_state.token)
    all_admins = get_admins(st.session_state.token)
    
    # Crear mapa de usuarios
    full_list = all_students + all_teachers + all_admins
    user_map = {u['id']: u for u in full_list}
    
    my_id = st.session_state.user['id']
    
    if my_id in user_map:
        del user_map[my_id]

    col_users, col_chat = st.columns([1, 2])
    
    with col_users:
        st.subheader("Contactos")
        
        if st.button("🔄 Actualizar Lista", type="secondary", use_container_width=True):
            st.rerun()
        
        contact_options = []
        # Prioridad 1: Online
        for uid, udata in user_map.items():
            if uid in online_ids:
                contact_options.append(uid)
        # Prioridad 2: Offline
        for uid, udata in user_map.items():
            if uid not in online_ids:
                contact_options.append(uid)
        
        if not contact_options:
            st.info("No hay otros usuarios registrados.")
            selected_user_id = None
        else:
            def format_user_option(uid):
                user = user_map[uid]
                status = "🟢" if uid in online_ids else "⚪"
                # Rol corto
                role_map = {"admin": "Admin", "teacher": "Prof.", "student": "Est."}
                role_str = role_map.get(user['role'], user['role'])
                return f"{status} {user['full_name']} ({role_str})"

            selected_user_id = st.radio(
                "Seleccionar chat:",
                options=contact_options,
                format_func=format_user_option
            )
    
    with col_chat:
        if selected_user_id:
            show_active_chat(selected_user_id, user_map, my_id)
        else:
            st.info("👈 Selecciona un usuario de la lista para ver el chat.")

# ==================== LOGIN ====================

def show_login():
    if st.button("⬅️ Volver al Inicio", type="secondary"):
        st.session_state.page = "landing"
        st.rerun()

    st.markdown('<h2 style="text-align: center; color: #1f77b4;">🔐 Acceso al Sistema</h2>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            username = st.text_input("Usuario o Email")
            password = st.text_input("Contraseña", type="password")
            
            # BOTÓN ESPECIAL ANIMADO
            set_btn_style("special")
            submit = st.form_submit_button("Ingresar", use_container_width=True)
            
            if submit:
                if username and password:
                    res = login(username, password)
                    if res:
                        st.session_state.token = res["access_token"]
                        st.session_state.user = get_current_user(res["access_token"])
                        st.session_state.page = "app"
                        st.rerun()
                    else: st.error("Credenciales inválidas")
                else: st.warning("Llena todos los campos")

# ==================== MAIN APP ====================

def show_main_app_router():
    # --- GESTIÓN DE NOTIFICACIONES TOAST (Esquina superior derecha) ---
    if st.session_state.flash_message:
        msg_type, msg_text = st.session_state.flash_message
        if msg_type == "success": 
            st.toast(msg_text, icon="✅")
        elif msg_type == "error": 
            st.toast(msg_text, icon="❌")
        elif msg_type == "warning": 
            st.toast(msg_text, icon="⚠️")
        elif msg_type == "info": 
            st.toast(msg_text, icon="ℹ️")
        # Limpiamos el mensaje inmediatamente
        st.session_state.flash_message = None

    user = st.session_state.user
    if not user:
        st.session_state.page = "login"
        st.rerun()
        return
    
    # Sidebar común
    with st.sidebar:
        st.image("https://img.icons8.com/fluency/96/noodles.png", width=80)
        st.write(f"Hola, **{user.get('first_name')}**")
        
        # --- DEFINICIÓN DE MENÚS ---
        if user['role'] == 'admin':
            menu_options = ["Dashboard", "Admin", "Comunidad", "Perfil"]
            menu_icons = ["house", "gear", "chat-dots", "person"]
        else:
            menu_options = ["Dashboard", "Mis Cursos", "Tareas", "Entregas", "Calificaciones", "Comunidad", "Perfil"]
            menu_icons = ["house", "book", "clipboard-check", "upload", "graph-up", "chat-dots", "person"]

        # --- LÓGICA PARA MANTENER LA POSICIÓN EN EL MENÚ ---
        # 1. Recuperar la última selección guardada, o usar la primera por defecto
        default_index = 0
        if "current_menu_selection" in st.session_state:
            try:
                # Buscamos el índice del menú guardado en la lista actual de opciones
                default_index = menu_options.index(st.session_state.current_menu_selection)
            except ValueError:
                default_index = 0 # Si el menú cambió o no existe, volver al inicio

        # 2. Renderizar el menú con el default_index calculado
        selected_menu = option_menu(
            "Menú", 
            menu_options, 
            icons=menu_icons, 
            menu_icon="cast", 
            default_index=default_index,
            key="main_nav_menu"
        )

        # 3. Guardar la selección actual para la próxima recarga
        st.session_state.current_menu_selection = selected_menu

        # Botón de Salir (Rojo/Primary)
        if st.button("Cerrar Sesión", type="primary"):
            st.session_state.token = None
            st.session_state.user = None
            st.session_state.page = "landing"
            # Limpiar selección de menú al salir
            if "current_menu_selection" in st.session_state:
                del st.session_state.current_menu_selection
            st.rerun()

    # Enrutamiento de vistas internas usando la variable selected_menu
    if selected_menu == "Admin" and user['role'] == 'admin': 
        show_admin_panel()
    elif selected_menu == "Dashboard": 
        show_dashboard()
    elif selected_menu == "Mis Cursos": 
        show_courses()
    elif selected_menu == "Tareas": 
        show_assignments()
    elif selected_menu == "Entregas": 
        show_submissions()
    elif selected_menu == "Calificaciones": 
        show_grades()
    elif selected_menu == "Perfil": 
        show_profile()
    elif selected_menu == "Comunidad": 
        show_chat_interface()
    else:
        st.write("Bienvenido a Maruchan University")

# ==================== VISTAS EXISTENTES ====================

def show_dashboard():
    st.title("📊 Dashboard")
    # Obtener estadísticas
    courses = get_my_courses(st.session_state.token)
    assignments = get_assignments(st.session_state.token)
    submissions = get_my_submissions(st.session_state.token)
    
    # Métricas
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Cursos Inscritos", len(courses))
    with col2: 
        pending = len([a for a in assignments if a['id'] not in [s['assignment_id'] for s in submissions]])
        st.metric("Tareas Pendientes", pending)
    with col3: st.metric("Entregas Realizadas", len(submissions))
    with col4: 
        graded = len([s for s in submissions if s['grade'] is not None])
        st.metric("Tareas Calificadas", graded)
    
    st.markdown("---")
    st.subheader("📅 Próximas Entregas")
    if assignments:
        for assignment in assignments[:5]:
            with st.expander(f"📝 {assignment['title']} - {assignment['course_code']}"):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**Fecha límite:** {assignment['due_date']}")
                    st.write(f"**Puntos:** {assignment['max_score']}")
                with col2:
                    if assignment['is_overdue']: st.error("⏰ Vencida")
                    else: st.success("✅ A tiempo")
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
                        # Se usan tabs para organizar las acciones
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
                st.subheader(submission['assignment']['title'])
                st.write(f"Nota: {submission['grade'] if submission['grade'] else 'Pendiente'}")
                st.markdown("---")
    else: st.info("Sin entregas.")

def show_grades():
    st.title("📊 Mis Calificaciones")
    submissions = get_my_submissions(st.session_state.token)
    graded = [s for s in submissions if s['grade'] is not None]
    if graded:
        data = [{"Tarea": s['assignment']['title'], "Nota": s['grade']} for s in graded]
        st.dataframe(pd.DataFrame(data), use_container_width=True)
    else: st.info("No tienes calificaciones.")

def show_profile():
    st.title("👤 Mi Perfil")
    
    user = st.session_state.user
    
    if user is None:
        st.error("No se pudo cargar la información del usuario")
        return

    col1, col2 = st.columns([1, 2])
    
    # --- SECCIÓN DE FOTO Y DATOS ---
    with col1:
        if user.get('profile_pic_url'):
            base_url = API_URL.rstrip("/")
            # Ajuste para entorno local si viene 'backend' en la URL
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
    
    # --- FORMULARIO DE EDICIÓN ---
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
        
        submit_update = st.form_submit_button("Guardar Cambios", type="secondary")
        
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
                        
                    #Usa flash message para que sobreviva al rerun
                    st.session_state.flash_message = ("success", "✅ Perfil actualizado exitosamente!")
                    st.rerun()
                else:
                    st.error(f"❌ Error: {result.get('detail', 'Error desconocido')}")
                    
    st.markdown("---")
    st.subheader("🔐 Seguridad")
    
    # --- FORMULARIO DE CONTRASEÑA ---
    with st.expander("Cambiar mi contraseña"):
        with st.form("change_my_pass_form", clear_on_submit=True):
            p1 = st.text_input("Nueva Contraseña", type="password")
            p2 = st.text_input("Confirmar Nueva Contraseña", type="password")
            
            # --- CORRECCIÓN AQUÍ ---
            set_btn_style("special") 
            if st.form_submit_button("Actualizar Contraseña"): 
                if p1 != p2:
                    st.error("Las contraseñas no coinciden")
                elif len(p1) < 8:
                    st.warning("La contraseña debe tener al menos 8 caracteres")
                else:
                    with st.spinner("Actualizando..."):
                        success, msg = change_password_api(st.session_state.token, user['id'], p1)
                        if success:
                            # Flash message y rerun para limpiar form
                            st.session_state.flash_message = ("success", "✅ Contraseña actualizada correctamente")
                            st.rerun()
                        else:
                            st.error(f"Error: {msg.get('detail')}")

# ==================== MAIN ====================

def main():
    if st.session_state.page == "landing":
        show_landing_page()
    elif st.session_state.page == "login":
        show_login()
    elif st.session_state.page == "app" and st.session_state.token:
        show_main_app_router()
    else:
        # Default fallback
        st.session_state.page = "landing"
        st.rerun()

if __name__ == "__main__":
    main()