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
    initial_sidebar_state="expanded" # Menú siempre visible
)

# URL de la API
API_URL = os.getenv("API_URL", "http://localhost:8000")

try:
    from student_app import run_student_app
    STUDENT_APP_AVAILABLE = True
except ImportError:
    STUDENT_APP_AVAILABLE = False
    st.warning("⚠️ No se encontró student_app.py. La interfaz de estudiantes no está disponible.")


# --- ESTILOS CSS MEJORADOS Y COMBINADOS ---

st.markdown("""
    <style>
    /* Importar fuentes */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    
    * {
        font-family: 'Poppins', sans-serif !important;
    }
    
    /* --- ANIMACIONES --- */
    @keyframes gradient-animation {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    @keyframes slide-up {
        from { transform: translateY(30px); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
    }
    
    @keyframes fade-in {
        from { opacity: 0; }
        to { opacity: 1; }
    }

    /* --- ESTILOS GENERALES --- */
    .main-header {
        font-size: 4rem;
        font-weight: 900;
        background: linear-gradient(270deg, #0077b6, #48cae4, #00b4d8, #0077b6);
        background-size: 300% 300%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: gradient-animation 4s ease infinite;
        text-align: center;
        margin-bottom: 0.5rem;
        padding-top: 1rem;
        letter-spacing: -1px;
    }

    .sub-header {
        font-size: 1.6rem;
        font-weight: 300;
        color: var(--text-color);
        text-align: center;
        margin-bottom: 3rem;
        opacity: 0.9;
    }

    /* Tarjetas mejoradas */
    .feature-card {
        background: linear-gradient(145deg, rgba(0, 119, 182, 0.08), rgba(72, 202, 228, 0.04));
        border: 2px solid rgba(0, 119, 182, 0.15);
        padding: 30px;
        border-radius: 20px;
        border-left: 5px solid #0077b6;
        box-shadow: 0 8px 20px rgba(0,0,0,0.08);
        height: 100%;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        animation: slide-up 0.8s ease-out;
    }
    
    .feature-card:hover {
        transform: translateY(-10px) scale(1.02);
        background: linear-gradient(145deg, rgba(0, 119, 182, 0.12), rgba(72, 202, 228, 0.08));
        border-left: 5px solid #48cae4;
        box-shadow: 0 16px 32px rgba(0, 119, 182, 0.2);
    }
    
    .card-icon { font-size: 2.5rem; margin-bottom: 15px; display: block; }

    /* --- SISTEMA DE COLORES DE BOTONES --- */
    
    /* Reglas base para TODOS los botones (incluyendo formularios) */
    .stButton > button,
    .stFormSubmitButton > button {
        border-radius: 12px;
        font-weight: 600;
        width: 100%;
        padding: 12px 24px;
        transition: all 0.3s ease;
        border: none !important;
        color: white !important;
        font-size: 1rem;
    }
    .stButton > button:hover,
    .stFormSubmitButton > button:hover { 
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
    }

    /* 1. ROJO (type="primary"): Eliminar, Cancelar, Acciones destructivas */
    div.stButton > button[kind="primary"],
    div.stFormSubmitButton > button[kind="primary"],
    [data-testid="stFormSubmitButton"] > button[kind="primary"] {
        background: linear-gradient(135deg, #d90429 0%, #ef233c 100%) !important;
        box-shadow: 0 4px 12px rgba(217, 4, 41, 0.4) !important;
        color: white !important;
    }
    div.stButton > button[kind="primary"]:hover,
    div.stFormSubmitButton > button[kind="primary"]:hover,
    [data-testid="stFormSubmitButton"] > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #b00020 0%, #d90429 100%) !important;
    }

    /* 2. AZUL (type="secondary" - Default): Acciones generales */
    div.stButton > button[kind="secondary"] {
        background: linear-gradient(135deg, #48cae4 0%, #0096c7 100%);
        box-shadow: 0 4px 12px rgba(72, 202, 228, 0.4);
    }
    div.stButton > button[kind="secondary"]:hover {
        background: linear-gradient(135deg, #0096c7 0%, #0077b6 100%);
    }

    /* 3. VERDE (Clase personalizada): Guardar, Crear, Inscribir */
    .btn-green + div.stButton > button,
    .btn-green + div.stFormSubmitButton > button {
        background: linear-gradient(135deg, #2a9d8f 0%, #06d6a0 100%) !important;
        box-shadow: 0 4px 12px rgba(42, 157, 143, 0.4) !important;
    }
    
    .btn-green + div.stButton > button:hover,
    .btn-green + div.stFormSubmitButton > button:hover {
        background: linear-gradient(135deg, #1f7a6f 0%, #05b589 100%) !important;
    }

    /* 4. ESPECIAL (Clase personalizada): Login, Inicio */
    .btn-special + div.stButton > button {
        background: linear-gradient(270deg, #0077b6, #48cae4, #00b4d8, #0077b6) !important;
        background-size: 300% 300% !important;
        animation: gradient-animation 3s ease infinite !important;
        box-shadow: 0 4px 16px rgba(0, 119, 182, 0.4) !important;
        font-size: 1.1rem !important;
    }

    /* Extra: Botones de enlace (Descargas) */
    .stLinkButton > a {
        background: linear-gradient(135deg, #48cae4 0%, #0077b6 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        text-align: center !important;
        padding: 12px 24px !important;
        transition: all 0.3s ease !important;
    }
    
    .stLinkButton > a:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 16px rgba(0, 119, 182, 0.3) !important;
    }
    
    /* Expanders mejorados */
    .stExpander {
        border: 2px solid rgba(0, 119, 182, 0.2);
        border-radius: 12px;
        margin-bottom: 12px;
        transition: all 0.3s ease;
    }
    
    .stExpander:hover {
        border-color: #0077b6;
        box-shadow: 0 6px 12px rgba(0, 119, 182, 0.15);
        transform: translateX(4px);
    }
    
    /* Tabs mejorados */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(0, 119, 182, 0.05);
        padding: 8px;
        border-radius: 12px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 12px 24px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #0077b6, #48cae4);
        color: white;
        box-shadow: 0 4px 8px rgba(0, 119, 182, 0.3);
    }
    
    /* Métricas (st.metric) */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(0, 119, 182, 0.1), rgba(72, 202, 228, 0.05));
        padding: 20px;
        border-radius: 12px;
        border: 2px solid rgba(0, 119, 182, 0.2);
        transition: all 0.3s ease;
    }
    
    [data-testid="stMetric"]:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 16px rgba(0, 119, 182, 0.2);
        border-color: #0077b6;
    }
    
    /* Mensajes */
    .stSuccess {
        background: linear-gradient(135deg, rgba(6, 214, 160, 0.1), rgba(6, 214, 160, 0.05));
        border-left: 5px solid #06d6a0;
        border-radius: 8px;
        padding: 16px;
    }
    
    .stWarning {
        background: linear-gradient(135deg, rgba(255, 209, 102, 0.1), rgba(255, 209, 102, 0.05));
        border-left: 5px solid #ffd166;
        border-radius: 8px;
        padding: 16px;
    }
    
    .stError {
        background: linear-gradient(135deg, rgba(239, 71, 111, 0.1), rgba(239, 71, 111, 0.05));
        border-left: 5px solid #ef476f;
        border-radius: 8px;
        padding: 16px;
    }
    
    .stInfo {
        background: linear-gradient(135deg, rgba(72, 202, 228, 0.1), rgba(72, 202, 228, 0.05));
        border-left: 5px solid #48cae4;
        border-radius: 8px;
        padding: 16px;
    }
    
    /* File uploader */
    .stFileUploader {
        border: 3px dashed rgba(0, 119, 182, 0.3);
        border-radius: 16px;
        padding: 30px;
        transition: all 0.3s ease;
        background: rgba(0, 119, 182, 0.02);
    }
    
    .stFileUploader:hover {
        border-color: #0077b6;
        background: rgba(0, 119, 182, 0.05);
        transform: scale(1.01);
    }
    
    /* Selectbox */
    .stSelectbox > div > div {
        border-radius: 12px;
        border: 2px solid rgba(0, 119, 182, 0.3);
        transition: all 0.3s ease;
    }
    
    .stSelectbox > div > div:hover {
        border-color: #0077b6;
        box-shadow: 0 4px 8px rgba(0, 119, 182, 0.15);
    }
    
    /* Dividers */
    hr {
        margin: 2rem 0;
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, #0077b6, transparent);
        opacity: 0.3;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(0, 119, 182, 0.05);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #0077b6, #48cae4);
        border-radius: 10px;
    }
    
    /* Sidebar mejorado */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(0, 119, 182, 0.03), rgba(72, 202, 228, 0.02));
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

def update_assignment(token, assignment_id, assignment_data):
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.put(f"{API_URL}/api/assignments/{assignment_id}", headers=headers, json=assignment_data)
        if response.status_code == 200: return True, response.json()
        return False, response.json()
    except Exception as e: return False, {"detail": str(e)}

def delete_assignment(token, assignment_id):
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.delete(f"{API_URL}/api/assignments/{assignment_id}", headers=headers)
        if response.status_code == 200: return True, response.json()
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

def drop_student_api(token, enrollment_id):
    """Desincribe a un estudiante de un curso"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.patch(f"{API_URL}/api/enrollments/{enrollment_id}/drop", headers=headers)
        if response.status_code == 200: return True, response.json()
        return False, response.json()
    except Exception as e: return False, {"detail": str(e)}


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
            search = st.text_input("🔍 Buscar por nombre...", placeholder="Ej: Juan Pérez o correo@email.com")
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
                                new_username = st.text_input("Usuario", value=current_u_data.get('username', ''), placeholder="nombre_usuario")
                                new_name = st.text_input("Primer Nombre", value=current_u_data.get('first_name', ''), placeholder="Ingrese el primer nombre")
                                new_last = st.text_input("Apellido(s)", value=current_u_data.get('last_name', ''), placeholder="Ingrese el/los apellido(s)")
                                new_email = st.text_input("Email", value=current_u_data['email'], placeholder="correo@maruchan.edu")
                                new_phone = st.text_input("Teléfono", value=current_u_data.get('phone', ''), placeholder="+506 8888-8888")
                                
                                # Botón VERDE para guardar
                                set_btn_style("green")
                                if st.form_submit_button("💾 Guardar Cambios", type="secondary"):
                                    update_data = {"first_name": new_name, "last_name": new_last, "email": new_email, "phone": new_phone, "username": new_username if new_username else None}
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
                                new_p = st.text_input("Nueva contraseña", type="password", placeholder="Mínimo 8 caracteres")
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
                    c_title = st.text_input("Nombre", placeholder="Ej: Programación I")
                    c_code = st.text_input("Código", placeholder="Ej: CS101")
                    c_credits = st.number_input("Créditos", 1, 10, 4)
                    c_semester = st.number_input("Semestre", 1, 12, 1)
                    c_start_date = st.date_input("Inicio")
                with c2:
                    c_schedule = st.text_input("Horario", placeholder="Ej: Lun-Mie 10:00-12:00")
                    c_classroom = st.text_input("Aula", placeholder="Ej: Edificio A, Sala 101")
                    c_max_students = st.number_input("Cupo", 1, 100, 30)
                    c_end_date = st.date_input("Fin")
                    if teachers:
                        c_teacher_id = st.selectbox("Profesor", options=list(teacher_options.keys()), format_func=lambda x: teacher_options[x]) 
                    else:
                        st.warning("No hay profesores.")
                        c_teacher_id = None
                
                c_desc = st.text_area("Descripción", placeholder="Breve descripción del curso y objetivos principales...")
                
                # APLICAMOS ESTILO VERDE AL BOTÓN DE CREAR
                set_btn_style("green")
                if st.form_submit_button("✅ Crear Curso", type="secondary"):
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
                            e_title = st.text_input("Nombre", value=course['title'], placeholder="Nombre del curso")
                            e_code = st.text_input("Código", value=course['code'], placeholder="Código único")
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
                            e_schedule = st.text_input("Horario", value=course.get('schedule', ''), placeholder="Ej: Lun-Mie 10:00-12:00")
                            e_classroom = st.text_input("Aula", value=course.get('classroom', ''), placeholder="Ej: Edificio A, Sala 101")
                            e_max_students = st.number_input("Cupo", value=course.get('max_students', 30))
                        
                        e_desc = st.text_area("Descripción", value=course.get('description', ''), placeholder="Descripción del curso...")
                        
                        # Botón VERDE para guardar
                        set_btn_style("green")
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
                if st.form_submit_button("✅ Inscribir Estudiante", type="secondary"):
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
                    new_username = st.text_input("Usuario", placeholder="Ej: jperez")
                    new_email = st.text_input("Email Oficial", placeholder="usuario@maruchan.edu")
                    new_pass = st.text_input("Contraseña", type="password", placeholder="Mínimo 8 caracteres")
                    new_pass2 = st.text_input("Confirmar Contraseña", type="password", placeholder="Repita la contraseña")
                with c2:
                    new_name = st.text_input("Nombre(s)", placeholder="Ej: Juan Carlos")
                    new_lastname = st.text_input("Apellido(s)", placeholder="Ej: Pérez López")
                    new_role = st.selectbox("Rol Institucional", ["student", "teacher", "admin"])
                    new_carnet = st.text_input("Carnet (Solo estudiantes)", placeholder="Ej: 2024001234")
                
                # APLICAMOS ESTILO VERDE
                set_btn_style("green")
                submitted = st.form_submit_button("💾 Guardar Usuario en Base de Datos", type="secondary")
                
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
    user = st.session_state.user
    
    # Header con estilo
    st.markdown("""
        <div style="background: linear-gradient(135deg, #0077b6 0%, #48cae4 100%); 
                    padding: 30px; border-radius: 16px; margin-bottom: 25px;
                    box-shadow: 0 8px 24px rgba(0, 119, 182, 0.3);">
            <h1 style="color: white; margin: 0; font-size: 2.5rem;">💬 Comunidad Universitaria</h1>
            <p style="color: rgba(255,255,255,0.9); margin: 10px 0 0 0; font-size: 1.1rem;">
                Conecta con profesores, estudiantes y administradores
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Obtener datos necesarios
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
        # Panel de contactos estilizado
        st.markdown("""
            <div style="background: linear-gradient(145deg, rgba(0, 119, 182, 0.08), rgba(72, 202, 228, 0.04));
                        padding: 15px; border-radius: 12px; border: 2px solid rgba(0, 119, 182, 0.15);
                        margin-bottom: 15px;">
                <h3 style="color: #0077b6; margin: 0;">📇 Contactos</h3>
            </div>
        """, unsafe_allow_html=True)
        
        # Estadísticas de conexión
        online_count = len([uid for uid in user_map.keys() if uid in online_ids])
        st.markdown(f"""
            <div style="display: flex; gap: 10px; margin-bottom: 15px;">
                <div style="background: #06d6a022; padding: 8px 12px; border-radius: 8px; flex: 1; text-align: center;">
                    <span style="color: #06d6a0; font-weight: bold;">🟢 {online_count}</span>
                    <span style="color: #666; font-size: 0.8rem;"> en línea</span>
                </div>
                <div style="background: #88888822; padding: 8px 12px; border-radius: 8px; flex: 1; text-align: center;">
                    <span style="color: #888; font-weight: bold;">👥 {len(user_map)}</span>
                    <span style="color: #666; font-size: 0.8rem;"> total</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔄 Actualizar", type="secondary", use_container_width=True):
            st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)
        
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
            st.info("📭 No hay otros usuarios registrados.")
            selected_user_id = None
        else:
            def format_user_option(uid):
                user = user_map[uid]
                status = "🟢" if uid in online_ids else "⚪"
                role_map = {"admin": "🛡️", "teacher": "👨‍🏫", "student": "🎓"}
                role_icon = role_map.get(user['role'], "👤")
                return f"{status} {role_icon} {user['full_name']}"

            selected_user_id = st.radio(
                "Seleccionar chat:",
                options=contact_options,
                format_func=format_user_option,
                label_visibility="collapsed"
            )
    
    with col_chat:
        if selected_user_id:
            # Mostrar info del usuario seleccionado
            target_user = user_map[selected_user_id]
            is_online = selected_user_id in online_ids
            status_badge = "🟢 En línea" if is_online else "⚪ Desconectado"
            role_map = {"admin": "Administrador", "teacher": "Profesor", "student": "Estudiante"}
            
            st.markdown(f"""
                <div style="background: linear-gradient(145deg, rgba(0, 119, 182, 0.08), rgba(72, 202, 228, 0.04));
                            padding: 15px 20px; border-radius: 12px; margin-bottom: 15px;
                            border: 2px solid rgba(0, 119, 182, 0.15);">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <h3 style="margin: 0; color: #0077b6;">💬 {target_user['full_name']}</h3>
                            <span style="color: #666; font-size: 0.9rem;">{role_map.get(target_user['role'], target_user['role'])}</span>
                        </div>
                        <span style="background: {'#06d6a0' if is_online else '#888'}22; 
                                    color: {'#06d6a0' if is_online else '#888'}; 
                                    padding: 5px 12px; border-radius: 15px; font-size: 0.85rem;">
                            {status_badge}
                        </span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            show_active_chat(selected_user_id, user_map, my_id)
        else:
            st.markdown("""
                <div style="background: #f8f9fa; padding: 40px; border-radius: 16px; text-align: center;">
                    <div style="font-size: 4rem; margin-bottom: 15px;">💬</div>
                    <h3 style="color: #666;">Selecciona un contacto</h3>
                    <p style="color: #888;">Elige a alguien de la lista para iniciar una conversación</p>
                </div>
            """, unsafe_allow_html=True)

# ==================== LOGIN ====================

def show_login():
    if st.button("⬅️ Volver al Inicio", type="secondary"):
        st.session_state.page = "landing"
        st.rerun()

    st.markdown('<h2 style="text-align: center; color: #0077b6;">🔐 Acceso al Sistema</h2>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            username = st.text_input("Usuario o Email", placeholder="Ingrese su usuario o correo")
            password = st.text_input("Contraseña", type="password", placeholder="Ingrese su contraseña")
            
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
        
        # Botón de recuperar credenciales
        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("🔑 ¿Olvidaste tu contraseña o usuario?"):
            st.markdown("""
                <div style="
                    background: linear-gradient(135deg, rgba(0, 119, 182, 0.1), rgba(72, 202, 228, 0.05));
                    padding: 20px;
                    border-radius: 12px;
                    border-left: 4px solid #0077b6;
                ">
                    <h4 style="color: #0077b6; margin-top: 0;">📧 Recuperar Credenciales</h4>
                    <p style="color: #666; margin-bottom: 15px;">
                        Ingresa tu correo institucional y te enviaremos las instrucciones para recuperar tu acceso.
                    </p>
                </div>
            """, unsafe_allow_html=True)
            
            recovery_email = st.text_input("Correo electrónico", placeholder="tu.correo@maruchan.edu", key="recovery_email")
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("📧 Recuperar Contraseña", type="primary", use_container_width=True):
                    if recovery_email and "@" in recovery_email:
                        st.success("✅ Si el correo existe en el sistema, recibirás un enlace de recuperación.")
                        st.info("📬 Revisa tu bandeja de entrada y spam.")
                    else:
                        st.warning("⚠️ Ingresa un correo válido")
            
            with col_btn2:
                if st.button("👤 Recuperar Usuario", type="secondary", use_container_width=True):
                    if recovery_email and "@" in recovery_email:
                        st.success("✅ Si el correo existe, recibirás tu nombre de usuario.")
                        st.info("📬 Revisa tu bandeja de entrada.")
                    else:
                        st.warning("⚠️ Ingresa un correo válido")
            
            st.markdown("---")
            st.caption("💡 **¿Necesitas más ayuda?** Contacta al administrador del sistema.")

# ==================== MAIN APP ====================

def show_main_app_router():
    """
    Router SOLO para Admin y Profesores
    Los estudiantes NUNCA deben llegar aquí
    """
    
    # Validación de usuario
    user = st.session_state.user
    if not user:
        st.session_state.page = "login"
        st.rerun()
        return
    
    # Bloquear estudiantes
    if user.get('role') == 'student':
        st.error("⚠️ Esta interfaz es solo para administradores y profesores")
        st.info("Redirigiendo a tu panel estudiantil...")
        st.rerun()
        return
    
    # Gestión de notificaciones TOAST
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
        st.session_state.flash_message = None

    # Sidebar común
    with st.sidebar:
        st.image("https://img.icons8.com/fluency/96/noodles.png", width=80)
        st.write(f"Hola, **{user.get('first_name')}** 👋")
        
        # Mostrar rol del usuario
        if user['role'] == 'admin':
            st.caption("🛡️ Administrador")
        elif user['role'] == 'teacher':
            st.caption("👨‍🏫 Profesor")
        
        # Definición de menús
        if user['role'] == 'admin':
            menu_options = ["Dashboard", "Admin", "Comunidad", "Perfil"]
            menu_icons = ["house", "gear", "chat-dots", "person"]
        elif user['role'] == 'teacher':
            menu_options = ["Dashboard", "Mis Cursos", "Tareas", "Comunidad", "Perfil"]
            menu_icons = ["house", "book", "clipboard-check", "chat-dots", "person"]
        else:
            st.error("Rol no autorizado")
            return

        # Lógica para mantener la posición en el menú
        default_index = 0
        if "current_menu_selection" in st.session_state:
            try:
                default_index = menu_options.index(st.session_state.current_menu_selection)
            except ValueError:
                default_index = 0

        # Renderizar el menú
        selected_menu = option_menu(
            "Menú", 
            menu_options, 
            icons=menu_icons, 
            menu_icon="cast", 
            default_index=default_index,
            key="main_nav_menu"
        )

        # Guardar la selección actual
        st.session_state.current_menu_selection = selected_menu

        # Botón de Salir
        if st.button("Cerrar Sesión", type="primary"):
            st.session_state.token = None
            st.session_state.user = None
            st.session_state.page = "landing"
            if "current_menu_selection" in st.session_state:
                del st.session_state.current_menu_selection
            st.rerun()

    # Enrutamiento de vistas internas
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
    user = st.session_state.user
    role = user.get('role', 'student')
    
    if role == 'admin':
        show_admin_dashboard()
    elif role == 'teacher':
        show_teacher_dashboard()
    else:
        show_student_dashboard()

def show_admin_dashboard():
    """Dashboard para administradores"""
    st.title("📊 Panel de Administración")
    st.markdown(f"**Bienvenido, {st.session_state.user.get('full_name', 'Admin')}**")
    
    # Obtener datos
    users = get_all_users(st.session_state.token) or []
    courses = get_all_courses(st.session_state.token) or []
    assignments = get_assignments(st.session_state.token) or []
    submissions = get_my_submissions(st.session_state.token) or []
    
    # Contar por roles
    students = [u for u in users if u.get('role') == 'student']
    teachers = [u for u in users if u.get('role') == 'teacher']
    admins = [u for u in users if u.get('role') == 'admin']
    active_users = [u for u in users if u.get('is_active', True)]
    
    st.markdown("### 👥 Usuarios del Sistema")
    col1, col2, col3, col4 = st.columns(4)
    with col1: 
        st.metric("👨‍🎓 Estudiantes", len(students))
    with col2: 
        st.metric("👨‍🏫 Profesores", len(teachers))
    with col3: 
        st.metric("🔑 Admins", len(admins))
    with col4: 
        st.metric("✅ Usuarios Activos", len(active_users))
    
    st.markdown("---")
    st.markdown("### 📚 Estadísticas Académicas")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📖 Total Cursos", len(courses))
    with col2:
        active_courses = [c for c in courses if c.get('status') == 'active']
        st.metric("🟢 Cursos Activos", len(active_courses))
    with col3:
        st.metric("📝 Total Tareas", len(assignments))
    with col4:
        graded = len([s for s in submissions if s.get('grade') is not None])
        st.metric("✅ Entregas Calificadas", graded)
    
    st.markdown("---")
    
    # Resumen de cursos
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown("### 📖 Cursos Recientes")
        if courses:
            for course in courses[:5]:
                with st.container():
                    st.write(f"**{course.get('code', 'N/A')}** - {course.get('title', 'Sin título')}")
                    st.caption(f"Profesor: {course.get('teacher_name', 'N/A')} | Inscritos: {course.get('enrolled_count', 0)}")
                    st.divider()
        else:
            st.info("No hay cursos registrados")
    
    with col_right:
        st.markdown("### 👨‍🎓 Estudiantes Recientes")
        if students:
            for student in students[:5]:
                with st.container():
                    st.write(f"**{student.get('full_name', 'N/A')}**")
                    st.caption(f"📧 {student.get('email', 'N/A')} | Carnet: {student.get('carnet', 'N/A')}")
                    st.divider()
        else:
            st.info("No hay estudiantes registrados")

def show_teacher_dashboard():
    """Dashboard para profesores"""
    user = st.session_state.user
    
    # Header con estilo
    st.markdown(f"""
        <div style="background: linear-gradient(135deg, #0077b6 0%, #48cae4 100%); 
                    padding: 30px; border-radius: 16px; margin-bottom: 25px;
                    box-shadow: 0 8px 24px rgba(0, 119, 182, 0.3);">
            <h1 style="color: white; margin: 0; font-size: 2.5rem;">👨‍🏫 Panel de Profesor</h1>
            <p style="color: rgba(255,255,255,0.9); margin: 10px 0 0 0; font-size: 1.2rem;">
                Bienvenido, <strong>{user.get('full_name', 'Profesor')}</strong>
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Obtener datos del profesor
    courses = get_my_courses(st.session_state.token) or []
    assignments = get_assignments(st.session_state.token) or []
    
    # Calcular estudiantes totales en mis cursos
    total_students = sum(c.get('enrolled_count', 0) for c in courses)
    
    # Tareas pendientes de calificar
    pending_grades = len([a for a in assignments if not a.get('is_overdue', False)])
    
    # ==================== MÉTRICAS CON ESTILO ====================
    st.markdown("### 📈 Mis Estadísticas")
    col1, col2, col3, col4 = st.columns(4)
    
    metrics = [
        ("📚", "Mis Cursos", len(courses), "#0077b6"),
        ("👨‍🎓", "Estudiantes", total_students, "#00b4d8"),
        ("📝", "Tareas Creadas", len(assignments), "#48cae4"),
        ("⏳", "Tareas Activas", pending_grades, "#06d6a0")
    ]
    
    for col, (icon, label, value, color) in zip([col1, col2, col3, col4], metrics):
        with col:
            st.markdown(f"""
                <div style="background: linear-gradient(135deg, {color}22, {color}11);
                            border-left: 4px solid {color}; padding: 20px; border-radius: 12px;
                            text-align: center; transition: all 0.3s ease;">
                    <div style="font-size: 2rem;">{icon}</div>
                    <div style="font-size: 2rem; font-weight: bold; color: {color};">{value}</div>
                    <div style="color: #666; font-size: 0.9rem;">{label}</div>
                </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ==================== CURSOS Y TAREAS ====================
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown("""
            <div style="background: linear-gradient(145deg, rgba(0, 119, 182, 0.08), rgba(72, 202, 228, 0.04));
                        padding: 20px; border-radius: 16px; border: 2px solid rgba(0, 119, 182, 0.15);">
                <h3 style="color: #0077b6; margin: 0 0 15px 0;">📖 Mis Cursos</h3>
            </div>
        """, unsafe_allow_html=True)
        
        if courses:
            for course in courses:
                progress_val = min(course.get('enrolled_count', 0) / max(course.get('max_students', 30), 1), 1.0)
                st.markdown(f"""
                    <div style="background: white; padding: 15px; border-radius: 10px; margin: 10px 0;
                                border-left: 4px solid #0077b6; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
                        <strong style="color: #0077b6;">{course.get('code', 'N/A')}</strong> - {course.get('title', 'Sin título')}
                        <br><span style="color: #888; font-size: 0.85rem;">
                            👥 {course.get('enrolled_count', 0)} estudiantes | 📅 {course.get('semester', 'N/A')}
                        </span>
                    </div>
                """, unsafe_allow_html=True)
                st.progress(progress_val)
        else:
            st.info("📭 No tienes cursos asignados")
    
    with col_right:
        st.markdown("""
            <div style="background: linear-gradient(145deg, rgba(0, 119, 182, 0.08), rgba(72, 202, 228, 0.04));
                        padding: 20px; border-radius: 16px; border: 2px solid rgba(0, 119, 182, 0.15);">
                <h3 style="color: #0077b6; margin: 0 0 15px 0;">📝 Tareas Recientes</h3>
            </div>
        """, unsafe_allow_html=True)
        
        if assignments:
            for assignment in assignments[:5]:
                status_color = "#ef476f" if assignment.get('is_overdue') else "#06d6a0"
                status_text = "🔴 Vencida" if assignment.get('is_overdue') else "🟢 Activa"
                due_date = assignment.get('due_date', 'N/A')[:10] if assignment.get('due_date') else 'N/A'
                
                st.markdown(f"""
                    <div style="background: white; padding: 15px; border-radius: 10px; margin: 10px 0;
                                border-left: 4px solid {status_color}; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <strong>{assignment.get('title', 'Sin título')}</strong>
                            <span style="background: {status_color}22; color: {status_color}; 
                                        padding: 3px 10px; border-radius: 12px; font-size: 0.8rem;">
                                {status_text}
                            </span>
                        </div>
                        <span style="color: #888; font-size: 0.85rem;">
                            📅 {due_date} | 🎯 {assignment.get('max_score', 0)} pts
                        </span>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("📭 No has creado tareas")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ==================== PRÓXIMAS ENTREGAS ====================
    st.markdown("""
        <div style="background: linear-gradient(135deg, #ffd16622, #ffd16611);
                    padding: 20px; border-radius: 16px; border: 2px solid #ffd16644;">
            <h3 style="color: #e6a100; margin: 0;">⏰ Próximas Entregas por Revisar</h3>
        </div>
    """, unsafe_allow_html=True)
    
    if assignments:
        upcoming = [a for a in assignments if not a.get('is_overdue', False)][:3]
        if upcoming:
            for assignment in upcoming:
                due_date = assignment.get('due_date', 'N/A')[:10] if assignment.get('due_date') else 'N/A'
                st.markdown(f"""
                    <div style="background: #fffbeb; padding: 12px 20px; border-radius: 8px; margin: 8px 0;
                                border-left: 4px solid #ffd166;">
                        📝 <strong>{assignment.get('title')}</strong> 
                        <span style="color: #888;">- {assignment.get('course_code', 'N/A')}</span>
                        <span style="float: right; color: #e6a100;">📅 Vence: {due_date}</span>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.success("✅ No hay tareas próximas a vencer")
    else:
        st.info("📭 No hay tareas pendientes")

def show_student_dashboard():
    """Dashboard para estudiantes (el original)"""
    st.title("📊 Mi Dashboard")
    # Obtener estadísticas
    courses = get_my_courses(st.session_state.token) or []
    assignments = get_assignments(st.session_state.token) or []
    submissions = get_my_submissions(st.session_state.token) or []
    
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
    user = st.session_state.user
    is_teacher = user.get('role') in ['teacher', 'admin']
    
    # Header con estilo
    if is_teacher:
        st.markdown("""
            <div style="background: linear-gradient(135deg, #0077b6 0%, #48cae4 100%); 
                        padding: 30px; border-radius: 16px; margin-bottom: 25px;
                        box-shadow: 0 8px 24px rgba(0, 119, 182, 0.3);">
                <h1 style="color: white; margin: 0; font-size: 2.5rem;">📚 Mis Cursos</h1>
                <p style="color: rgba(255,255,255,0.9); margin: 10px 0 0 0; font-size: 1.1rem;">
                    Gestiona tus cursos, estudiantes y tareas
                </p>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.title("📚 Mis Cursos")
    
    courses = get_my_courses(st.session_state.token)
    
    if courses:
        for course in courses:
            # ==================== TARJETA DE CURSO ====================
            st.markdown(f"""
                <div style="background: linear-gradient(145deg, rgba(0, 119, 182, 0.08), rgba(72, 202, 228, 0.04));
                            border: 2px solid rgba(0, 119, 182, 0.15); padding: 25px; border-radius: 16px; 
                            margin-bottom: 20px; border-left: 5px solid #0077b6;">
                    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                        <div>
                            <h2 style="margin: 0; color: #0077b6;">{course['code']} - {course['title']}</h2>
                            <p style="margin: 8px 0 0 0; color: #666;">
                                👨‍🏫 {course['teacher_name']} | 
                                📅 Semestre {course['semester']} | 
                                📖 {course['credits']} créditos
                            </p>
                        </div>
                        <div style="text-align: right;">
                            <div style="background: #0077b6; color: white; padding: 8px 16px; border-radius: 20px; display: inline-block;">
                                👥 {course['enrolled_count']} estudiantes
                            </div>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # Sección de gestión para profesores y admins
            if is_teacher:
                tab_students, tab_assignments = st.tabs(["👥 Gestionar Estudiantes", "📝 Crear Tarea Rápida"])
                
                # ==================== TAB ESTUDIANTES ====================
                with tab_students:
                    col_list, col_enroll = st.columns([2, 1])
                    
                    with col_list:
                        st.markdown("##### 📋 Estudiantes Inscritos")
                        enrollments = get_course_enrollments(st.session_state.token, course['id'])
                        
                        if enrollments:
                            for enrollment in enrollments:
                                student = enrollment['student']
                                col_info, col_action = st.columns([4, 1])
                                
                                with col_info:
                                    st.markdown(f"""
                                        <div style="background: white; padding: 12px 16px; border-radius: 8px; 
                                                    margin: 4px 0; border-left: 3px solid #06d6a0;
                                                    box-shadow: 0 2px 6px rgba(0,0,0,0.05);">
                                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                                <div>
                                                    <strong>👤 {student['full_name']}</strong>
                                                    <br><span style="color: #888; font-size: 0.85rem;">
                                                        📧 {student['email']} | 🎫 {student.get('carnet', 'S/C')}
                                                    </span>
                                                </div>
                                                <span style="color: #888; font-size: 0.8rem;">
                                                    📅 {enrollment['enrolled_at'][:10]}
                                                </span>
                                            </div>
                                        </div>
                                    """, unsafe_allow_html=True)
                                
                                with col_action:
                                    if st.button("🗑️", key=f"drop_{enrollment['id']}_{course['id']}", 
                                                help=f"Desinscribir a {student['full_name']}", type="primary"):
                                        st.session_state[f"confirm_drop_{enrollment['id']}"] = True
                                
                                # Confirmación de desinscripción
                                if st.session_state.get(f"confirm_drop_{enrollment['id']}", False):
                                    st.warning(f"⚠️ ¿Desinscribir a **{student['full_name']}** del curso?")
                                    col_yes, col_no = st.columns(2)
                                    with col_yes:
                                        if st.button("✅ Sí", key=f"yes_drop_{enrollment['id']}", type="primary"):
                                            success, res = drop_student_api(st.session_state.token, enrollment['id'])
                                            if success:
                                                del st.session_state[f"confirm_drop_{enrollment['id']}"]
                                                st.session_state.flash_message = ("success", f"🗑️ {student['full_name']} desinscrito del curso")
                                                st.rerun()
                                            else:
                                                st.error(f"Error: {res.get('detail')}")
                                    with col_no:
                                        if st.button("❌ No", key=f"no_drop_{enrollment['id']}", type="secondary"):
                                            del st.session_state[f"confirm_drop_{enrollment['id']}"]
                                            st.rerun()
                        else:
                            st.info("📭 No hay estudiantes inscritos en este curso.")
                    
                    with col_enroll:
                        st.markdown("##### ➕ Inscribir Estudiante")
                        all_students = get_students(st.session_state.token)
                        
                        if all_students:
                            enrollments = enrollments if enrollments else []
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
                                    
                                    set_btn_style("green")
                                    if st.form_submit_button("✅ Inscribir", type="secondary", use_container_width=True):
                                        with st.spinner("Inscribiendo..."):
                                            success, res = enroll_student_api(st.session_state.token, course['id'], sel_student)
                                            if success:
                                                st.session_state.flash_message = ("success", "✅ Estudiante inscrito!")
                                                st.rerun()
                                            else:
                                                st.error(f"Error: {res.get('detail')}")
                            else:
                                st.success("✅ Todos los estudiantes ya están inscritos")
                        else:
                            st.info("No hay estudiantes en el sistema")
                
                # ==================== TAB TAREAS ====================
                with tab_assignments:
                    st.markdown("##### 📝 Crear Nueva Tarea para este Curso")
                    
                    with st.form(f"quick_assignment_{course['id']}"):
                        qa_col1, qa_col2 = st.columns(2)
                        
                        with qa_col1:
                            qa_title = st.text_input("📌 Título", key=f"qa_title_{course['id']}", 
                                placeholder="Ej: Tarea 1 - Introducción")
                            qa_date = st.date_input("📅 Fecha entrega", key=f"qa_date_{course['id']}")
                            qa_time = st.time_input("⏰ Hora entrega", key=f"qa_time_{course['id']}")
                        
                        with qa_col2:
                            qa_score = st.number_input("🎯 Puntos", value=100.0, key=f"qa_score_{course['id']}")
                            qa_weight = st.number_input("⚖️ Peso", value=1.0, step=0.1, key=f"qa_weight_{course['id']}")
                            qa_published = st.checkbox("🌐 Publicar ahora", value=True, key=f"qa_pub_{course['id']}")
                        
                        qa_desc = st.text_area("📋 Instrucciones", key=f"qa_desc_{course['id']}", 
                            placeholder="Describa los objetivos y requisitos...", height=100)
                        
                        set_btn_style("green")
                        if st.form_submit_button("✨ Crear Tarea", type="secondary", use_container_width=True):
                            if qa_title:
                                due_dt = datetime.combine(qa_date, qa_time)
                                assign_data = {
                                    "course_id": course['id'],
                                    "title": qa_title,
                                    "description": qa_desc,
                                    "due_date": due_dt.isoformat(),
                                    "max_score": qa_score,
                                    "weight": qa_weight,
                                    "is_published": qa_published
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
                                st.warning("⚠️ El título es obligatorio")
            
            st.markdown("---")
    else:
        st.info("📭 No estás inscrito en ningún curso (o no tienes cursos asignados si eres profesor).")

def show_assignments():
    user = st.session_state.user
    is_teacher = user.get('role') in ['teacher', 'admin']
    
    # Header con estilo
    if is_teacher:
        st.markdown("""
            <div style="background: linear-gradient(135deg, #0077b6 0%, #48cae4 100%); 
                        padding: 30px; border-radius: 16px; margin-bottom: 25px;
                        box-shadow: 0 8px 24px rgba(0, 119, 182, 0.3);">
                <h1 style="color: white; margin: 0; font-size: 2.5rem;">📚 Gestión de Tareas</h1>
                <p style="color: rgba(255,255,255,0.9); margin: 10px 0 0 0; font-size: 1.1rem;">
                    Crea, edita y administra las tareas de tus cursos
                </p>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.title("📋 Tareas y Asignaciones")
    
    # Selector de curso
    courses = get_my_courses(st.session_state.token)
    course_options = {c['id']: f"{c['code']} - {c['title']}" for c in courses}
    
    # ==================== SECCIÓN CREAR TAREA (Solo profesores) ====================
    if is_teacher:
        with st.expander("➕ Crear Nueva Tarea", expanded=False):
            with st.form("create_assignment_form"):
                st.markdown("#### 📝 Nueva Asignación")
                
                c_col1, c_col2 = st.columns(2)
                with c_col1:
                    new_course_id = st.selectbox(
                        "📚 Curso",
                        options=list(course_options.keys()),
                        format_func=lambda x: course_options[x]
                    )
                    new_title = st.text_input("📌 Título de la tarea", placeholder="Ej: Proyecto Final - Módulo 1")
                    new_due_date = st.date_input("📅 Fecha de entrega")
                    new_due_time = st.time_input("⏰ Hora de entrega")
                
                with c_col2:
                    new_max_score = st.number_input("🎯 Puntos máximos", min_value=0.0, value=100.0)
                    new_weight = st.number_input("⚖️ Peso en nota final", min_value=0.0, value=1.0, step=0.1)
                    new_is_published = st.checkbox("🌐 Publicar inmediatamente", value=True)
                
                new_description = st.text_area("📋 Descripción e instrucciones", 
                    placeholder="Detalle los objetivos, requisitos y criterios de evaluación...",
                    height=120)
                
                set_btn_style("green")
                submitted = st.form_submit_button("✨ Crear Tarea", type="secondary", use_container_width=True)
                
                if submitted:
                    if new_title and new_course_id:
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

    # ==================== FILTRO Y LISTA DE TAREAS ====================
    col_filter1, col_filter2 = st.columns([3, 1])
    with col_filter1:
        selected_course = st.selectbox(
            "🔍 Filtrar por curso",
            options=[None] + list(course_options.keys()),
            format_func=lambda x: "📚 Todos los cursos" if x is None else course_options[x]
        )
    with col_filter2:
        if is_teacher:
            st.metric("📝 Total Tareas", len(get_assignments(st.session_state.token, selected_course) or []))
    
    # Obtener asignaciones
    assignments = get_assignments(st.session_state.token, selected_course)
    submissions = get_my_submissions(st.session_state.token)
    submitted_ids = [s['assignment_id'] for s in submissions]
    
    if assignments:
        for assignment in assignments:
            is_submitted = assignment['id'] in submitted_ids
            
            # ==================== TARJETA DE TAREA ====================
            status_color = "#ef476f" if assignment['is_overdue'] else "#06d6a0"
            status_icon = "🔴" if assignment['is_overdue'] else "🟢"
            published_badge = "📢 Publicada" if assignment.get('is_published', True) else "🔒 Borrador"
            
            if is_teacher:
                # Vista de profesor - Tarjeta estilizada
                st.markdown(f"""
                    <div style="background: linear-gradient(145deg, rgba(0, 119, 182, 0.08), rgba(72, 202, 228, 0.04));
                                border-left: 5px solid {status_color}; padding: 20px; border-radius: 12px; 
                                margin-bottom: 15px; transition: all 0.3s ease;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <h3 style="margin: 0; color: #0077b6;">{status_icon} {assignment['title']}</h3>
                                <p style="margin: 5px 0; color: #666;">📚 {assignment['course_code']} | 🎯 {assignment['max_score']} pts | ⚖️ Peso: {assignment.get('weight', 1.0)}</p>
                            </div>
                            <div style="text-align: right;">
                                <span style="background: {'#06d6a0' if assignment.get('is_published', True) else '#ffd166'}; 
                                            color: white; padding: 5px 12px; border-radius: 20px; font-size: 0.85rem;">
                                    {published_badge}
                                </span>
                            </div>
                        </div>
                        <p style="margin: 10px 0 0 0; color: #888;">📅 Fecha límite: {assignment['due_date'][:16].replace('T', ' ')}</p>
                    </div>
                """, unsafe_allow_html=True)
                
                # Tabs para organizar acciones del profesor
                tab_edit, tab_submissions = st.tabs(["✏️ Editar Tarea", "📥 Ver Entregas"])
                
                with tab_edit:
                    # ==================== FORMULARIO DE EDICIÓN ====================
                    with st.form(f"edit_assignment_{assignment['id']}"):
                        st.markdown("##### ✏️ Modificar Tarea")
                        
                        edit_col1, edit_col2 = st.columns(2)
                        with edit_col1:
                            edit_title = st.text_input("📌 Título", value=assignment['title'], key=f"edit_title_{assignment['id']}")
                            
                            # Parsear la fecha actual
                            try:
                                current_due = datetime.fromisoformat(assignment['due_date'].replace('Z', '+00:00'))
                            except:
                                current_due = datetime.now()
                            
                            edit_due_date = st.date_input("📅 Fecha", value=current_due.date(), key=f"edit_date_{assignment['id']}")
                            edit_due_time = st.time_input("⏰ Hora", value=current_due.time(), key=f"edit_time_{assignment['id']}")
                        
                        with edit_col2:
                            edit_max_score = st.number_input("🎯 Puntos", min_value=0.0, value=float(assignment['max_score']), key=f"edit_score_{assignment['id']}")
                            edit_weight = st.number_input("⚖️ Peso", min_value=0.0, value=float(assignment.get('weight', 1.0)), step=0.1, key=f"edit_weight_{assignment['id']}")
                            edit_is_published = st.checkbox("🌐 Publicada", value=assignment.get('is_published', True), key=f"edit_pub_{assignment['id']}")
                        
                        edit_description = st.text_area("📋 Descripción", 
                            value=assignment.get('description', '') or '', 
                            height=100, 
                            key=f"edit_desc_{assignment['id']}")
                        
                        # Botón Guardar (Verde)
                        set_btn_style("green")
                        save_btn = st.form_submit_button("💾 Guardar Cambios", type="secondary", use_container_width=True)
                        
                        st.markdown("<br>", unsafe_allow_html=True)
                        
                        # Botón Eliminar (Rojo) - Separado y centrado
                        _, col_delete, _ = st.columns([1, 2, 1])
                        with col_delete:
                            delete_btn = st.form_submit_button("🗑️ Eliminar Tarea", type="primary", use_container_width=True)
                        
                        if save_btn:
                            due_datetime = datetime.combine(edit_due_date, edit_due_time)
                            update_data = {
                                "title": edit_title,
                                "description": edit_description,
                                "due_date": due_datetime.isoformat(),
                                "max_score": edit_max_score,
                                "weight": edit_weight,
                                "is_published": edit_is_published
                            }
                            
                            with st.spinner("Guardando cambios..."):
                                success, result = update_assignment(st.session_state.token, assignment['id'], update_data)
                                if success:
                                    st.session_state.flash_message = ("success", f"✅ Tarea '{edit_title}' actualizada!")
                                    st.rerun()
                                else:
                                    st.error(f"❌ Error: {result.get('detail', 'Error desconocido')}")
                        
                        if delete_btn:
                            st.session_state[f"confirm_delete_{assignment['id']}"] = True
                    
                    # Confirmación de eliminación
                    if st.session_state.get(f"confirm_delete_{assignment['id']}", False):
                        st.warning(f"⚠️ ¿Estás seguro de eliminar '{assignment['title']}'? Esta acción no se puede deshacer.")
                        col_del1, col_del2 = st.columns(2)
                        with col_del1:
                            if st.button("✅ Sí, eliminar", key=f"confirm_yes_{assignment['id']}", type="primary"):
                                success, result = delete_assignment(st.session_state.token, assignment['id'])
                                if success:
                                    st.session_state.flash_message = ("success", "🗑️ Tarea eliminada")
                                    del st.session_state[f"confirm_delete_{assignment['id']}"]
                                    st.rerun()
                                else:
                                    st.error(f"❌ Error: {result.get('detail', 'No se puede eliminar')}")
                        with col_del2:
                            if st.button("❌ Cancelar", key=f"confirm_no_{assignment['id']}", type="secondary"):
                                del st.session_state[f"confirm_delete_{assignment['id']}"]
                                st.rerun()
                
                with tab_submissions:
                    # ==================== ENTREGAS DE ESTUDIANTES ====================
                    subs = get_assignment_submissions(st.session_state.token, assignment['id'])
                    
                    if subs:
                        st.markdown(f"**📊 Total entregas: {len(subs)}**")
                        
                        for sub in subs:
                            with st.container():
                                col_sub1, col_sub2, col_sub3, col_sub4 = st.columns([2, 1, 1, 1])
                                with col_sub1:
                                    st.markdown(f"👤 **{sub['student']['full_name']}**")
                                    st.caption(f"📅 {sub['submitted_at_date'][:16].replace('T', ' ')}")
                                
                                with col_sub2:
                                    if sub['late']:
                                        st.warning("⏰ Tardía")
                                    else:
                                        st.success("✅ A tiempo")
                                
                                with col_sub3:
                                    if sub['grade'] is not None:
                                        st.info(f"📊 {sub['grade']}/{assignment['max_score']}")
                                    else:
                                        st.caption("Sin calificar")
                                
                                with col_sub4:
                                    base_url = API_URL.rstrip("/")
                                    if "backend" in base_url:
                                         base_url = base_url.replace("backend", "localhost")
                                    download_url = f"{base_url}/api/submissions/{sub['id']}/download?token={st.session_state.token}"
                                    st.link_button("📥 Archivo", download_url)
                            
                            # Popover para calificar
                            with st.popover(f"📝 Calificar a {sub['student']['full_name']}", use_container_width=True):
                                with st.form(f"grade_form_{sub['id']}"):
                                    current_grade = sub['grade'] if sub['grade'] is not None else 0.0
                                    new_grade = st.number_input(
                                        f"🎯 Nota (Max: {assignment['max_score']})", 
                                        min_value=0.0, 
                                        max_value=float(assignment['max_score']),
                                        value=float(current_grade),
                                        key=f"grade_input_{sub['id']}"
                                    )
                                    
                                    new_feedback = st.text_area(
                                        "💬 Feedback", 
                                        value=sub['feedback_char'] if sub['feedback_char'] else "",
                                        key=f"feedback_{sub['id']}",
                                        placeholder="Comentarios sobre el trabajo...",
                                        height=80
                                    )
                                    
                                    set_btn_style("green")
                                    if st.form_submit_button("✅ Guardar Calificación", type="secondary", use_container_width=True):
                                        grade_data = {
                                            "grade": new_grade,
                                            "feedback_char": new_feedback,
                                            "graded_by_id": user['id']
                                        }
                                        
                                        success, res = grade_submission_api(st.session_state.token, sub['id'], grade_data)
                                        if success:
                                            st.session_state.flash_message = ("success", f"✅ Nota guardada para {sub['student']['full_name']}")
                                            st.rerun()
                                        else:
                                            st.error(f"Error: {res.get('detail')}")
                            
                            st.divider()
                    else:
                        st.info("📭 No hay entregas para esta tarea aún.")
                
                st.markdown("---")
            
            else:
                # ==================== VISTA DE ESTUDIANTE ====================
                expander_title = f"{'✅' if is_submitted else '📝'} {assignment['title']} - {assignment['course_code']}"
                
                with st.expander(expander_title, expanded=not is_submitted):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.markdown(f"**📋 Descripción:** {assignment.get('description', 'Sin descripción')}")
                        st.markdown(f"**📅 Fecha límite:** {assignment['due_date'][:16].replace('T', ' ')}")
                        st.markdown(f"**🎯 Puntos máximos:** {assignment['max_score']}")
                    
                    with col2:
                        if assignment['is_overdue']:
                            st.error("⏰ VENCIDA")
                        else:
                            st.success("✅ A tiempo")
                        
                        if is_submitted:
                            st.info("📨 Ya entregada")
                    
                    # Subir entrega
                    if not is_submitted:
                        st.markdown("---")
                        st.markdown("### 📤 Subir Entrega")
                        uploaded_file = st.file_uploader(
                            "Selecciona tu archivo",
                            key=f"upload_{assignment['id']}"
                        )
                        
                        if uploaded_file:
                            set_btn_style("green")
                            if st.button(f"📨 Enviar Tarea", key=f"submit_{assignment['id']}", type="secondary"):
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
    else:
        st.info("📭 No hay tareas disponibles")

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
    user = st.session_state.user
    
    if user is None:
        st.error("No se pudo cargar la información del usuario")
        return
    
    # Header con estilo
    role_map = {"admin": ("🛡️", "Administrador"), "teacher": ("👨‍🏫", "Profesor"), "student": ("🎓", "Estudiante")}
    role_icon, role_name = role_map.get(user.get('role'), ("👤", user.get('role', 'Usuario')))
    
    st.markdown(f"""
        <div style="background: linear-gradient(135deg, #0077b6 0%, #48cae4 100%); 
                    padding: 30px; border-radius: 16px; margin-bottom: 25px;
                    box-shadow: 0 8px 24px rgba(0, 119, 182, 0.3);">
            <h1 style="color: white; margin: 0; font-size: 2.5rem;">👤 Mi Perfil</h1>
            <p style="color: rgba(255,255,255,0.9); margin: 10px 0 0 0; font-size: 1.1rem;">
                Gestiona tu información personal y configuración
            </p>
        </div>
    """, unsafe_allow_html=True)

    # ==================== TARJETA DE PERFIL ====================
    col1, col2 = st.columns([1, 2])
    
    with col1:
        if user.get('profile_pic_url'):
            base_url = API_URL.rstrip("/")
            if "backend" in base_url:
                 base_url = base_url.replace("backend", "localhost")
            image_url = f"{base_url}{user['profile_pic_url']}"
            st.image(image_url, width=180)
        else:
            st.markdown("""
                <div style="width: 180px; height: 180px; background: linear-gradient(135deg, #0077b6, #48cae4);
                            border-radius: 50%; display: flex; align-items: center; justify-content: center;
                            margin: 0 auto; font-size: 4rem; color: white;">
                    👤
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown(f"""
            <div style="margin-top: 15px; text-align: center;">
                <span style="background: #0077b6; color: white; padding: 5px 15px; border-radius: 20px;">
                    {role_icon} {role_name}
                </span>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div style="background: linear-gradient(145deg, rgba(0, 119, 182, 0.08), rgba(72, 202, 228, 0.04));
                        padding: 25px; border-radius: 16px; border: 2px solid rgba(0, 119, 182, 0.15);">
                <h2 style="color: #0077b6; margin: 0 0 20px 0;">{user.get('full_name', 'Usuario')}</h2>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                    <div>
                        <span style="color: #888; font-size: 0.85rem;">👤 Usuario</span>
                        <div style="font-weight: 600; color: #333;">@{user.get('username', 'N/A')}</div>
                    </div>
                    <div>
                        <span style="color: #888; font-size: 0.85rem;">📧 Email</span>
                        <div style="font-weight: 600; color: #333;">{user.get('email', 'N/A')}</div>
                    </div>
                    <div>
                        <span style="color: #888; font-size: 0.85rem;">📅 Miembro desde</span>
                        <div style="font-weight: 600; color: #333;">{user.get('joined_date', 'N/A')}</div>
                    </div>
                    <div>
                        <span style="color: #888; font-size: 0.85rem;">📱 Teléfono</span>
                        <div style="font-weight: 600; color: #333;">{user.get('phone', 'No registrado')}</div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # ==================== TABS DE EDICIÓN ====================
    tab_info, tab_security = st.tabs(["✏️ Editar Información", "🔐 Seguridad"])
    
    with tab_info:
        st.markdown("""
            <div style="background: linear-gradient(145deg, rgba(6, 214, 160, 0.08), rgba(6, 214, 160, 0.04));
                        padding: 15px 20px; border-radius: 12px; margin-bottom: 20px;
                        border-left: 4px solid #06d6a0;">
                <strong style="color: #06d6a0;">✏️ Actualiza tu información personal</strong>
            </div>
        """, unsafe_allow_html=True)
        
        with st.form("edit_profile_form"):
            col_a, col_b = st.columns(2)
            
            with col_a:
                new_first_name = st.text_input("📝 Primer Nombre", value=user.get('first_name', ''), placeholder="Tu primer nombre")
                new_last_name = st.text_input("📝 Apellido(s)", value=user.get('last_name', ''), placeholder="Tu(s) apellido(s)")
                new_email = st.text_input("📧 Email", value=user.get('email', ''), placeholder="correo@maruchan.edu")
            
            with col_b:
                new_phone = st.text_input("📱 Teléfono", value=user.get('phone') or '', placeholder="+506 8888-8888")
                new_middle_name = st.text_input("📝 Segundo Nombre", value=user.get('middle_name') or '', placeholder="Opcional")
                new_username = st.text_input("👤 Nombre de Usuario", value=user.get('username', ''), placeholder="nuevo_usuario", help="Mínimo 3 caracteres")
            
            st.markdown("##### 📷 Cambiar Foto de Perfil")
            new_profile_pic = st.file_uploader("Subir nueva foto", type=['png', 'jpg', 'jpeg'])
            
            set_btn_style("green")
            submit_update = st.form_submit_button("💾 Guardar Cambios", type="secondary", use_container_width=True)
            
            if submit_update:
                update_data = {
                    "first_name": new_first_name,
                    "last_name": new_last_name,
                    "email": new_email,
                    "phone": new_phone if new_phone else None,
                    "middle_name": new_middle_name if new_middle_name else None,
                    "username": new_username if new_username and new_username != user.get('username') else None
                }
                
                with st.spinner("Actualizando perfil..."):
                    success, result = update_user_profile(
                        st.session_state.token, 
                        user['id'], 
                        update_data,
                        profile_pic_file=new_profile_pic
                    )
                    
                    if success:
                        updated_user = get_current_user(st.session_state.token)
                        if updated_user:
                            st.session_state.user = updated_user
                        else:
                            st.session_state.user = result
                        st.session_state.flash_message = ("success", "✅ Perfil actualizado exitosamente!")
                        st.rerun()
                    else:
                        st.error(f"❌ Error: {result.get('detail', 'Error desconocido')}")
    
    with tab_security:
        st.markdown("""
            <div style="background: linear-gradient(145deg, rgba(239, 71, 111, 0.08), rgba(239, 71, 111, 0.04));
                        padding: 15px 20px; border-radius: 12px; margin-bottom: 20px;
                        border-left: 4px solid #ef476f;">
                <strong style="color: #ef476f;">🔐 Cambia tu contraseña de forma segura</strong>
            </div>
        """, unsafe_allow_html=True)
        
        with st.form("change_my_pass_form", clear_on_submit=True):
            p1 = st.text_input("🔑 Nueva Contraseña", type="password", placeholder="Mínimo 8 caracteres")
            p2 = st.text_input("🔑 Confirmar Nueva Contraseña", type="password", placeholder="Repita la contraseña")
            
            set_btn_style("green")
            if st.form_submit_button("🔐 Actualizar Contraseña", type="secondary", use_container_width=True): 
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
    """
    Función principal que enruta a la interfaz correcta según el rol del usuario
    """
    
    if st.session_state.page == "landing":
        show_landing_page()
        return
    
    if st.session_state.page == "login":
        show_login()
        return
    
    if st.session_state.page == "app" and st.session_state.token and st.session_state.user:
        user_role = st.session_state.user.get('role')
        
        # ESTUDIANTES → student_app.py
        if user_role == 'student':
            if STUDENT_APP_AVAILABLE:
                run_student_app()
            else:
                st.error("⚠️ La interfaz de estudiantes no está disponible.")
                st.info("Asegúrate de que el archivo student_app.py esté en el mismo directorio que app.py")
                if st.button("Cerrar sesión"):
                    st.session_state.token = None
                    st.session_state.user = None
                    st.session_state.page = "landing"
                    st.rerun()
            return
        
        # ADMIN Y PROFESORES → app.py original
        elif user_role in ['admin', 'teacher']:
            show_main_app_router()
            return
        
        else:
            st.error("Rol de usuario no reconocido")
            if st.button("Volver al inicio"):
                st.session_state.page = "landing"
                st.rerun()
            return
    
    # Fallback
    st.session_state.page = "landing"
    st.rerun()


if __name__ == "__main__":
    main()