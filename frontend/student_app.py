import streamlit as st
from streamlit_option_menu import option_menu

# ==================== IMPORTAR LAS PÁGINAS ====================
from student_pages import dashboard, courses, assignments, grades, profile, community

# ==================== ESTILOS CSS MEJORADOS ====================
st.markdown("""
    <style>
    /* Importar fuentes */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    
    * {
        font-family: 'Poppins', sans-serif !important;
    }
    
    /* Animaciones */
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
    
    /* Header principal */
    .student-header {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(270deg, #2a9d8f, #48cae4, #06d6a0, #2a9d8f);
        background-size: 300% 300%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: gradient-animation 4s ease infinite;
        text-align: center;
        margin-bottom: 1rem;
        letter-spacing: -1px;
    }
    
    /* Métricas mejoradas */
    .metric-student {
        background: linear-gradient(135deg, #2a9d8f 0%, #48cae4 100%);
        padding: 25px;
        border-radius: 16px;
        text-align: center;
        color: white;
        box-shadow: 0 8px 16px rgba(42, 157, 143, 0.3);
        transition: all 0.3s ease;
        animation: slide-up 0.6s ease-out;
    }
    
    .metric-student:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 12px 24px rgba(42, 157, 143, 0.4);
    }
    
    /* Tarjetas de curso */
    .course-card {
        background: linear-gradient(145deg, rgba(42, 157, 143, 0.1), rgba(72, 202, 228, 0.05));
        border-left: 5px solid #2a9d8f;
        padding: 25px;
        border-radius: 16px;
        margin-bottom: 20px;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        animation: slide-up 0.6s ease-out;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    }
    
    .course-card:hover {
        transform: translateX(10px) scale(1.02);
        box-shadow: 0 12px 24px rgba(42, 157, 143, 0.2);
        background: linear-gradient(145deg, rgba(42, 157, 143, 0.15), rgba(72, 202, 228, 0.1));
        border-left: 5px solid #48cae4;
    }
    
    /* Expanders mejorados */
    .stExpander {
        border: 2px solid rgba(42, 157, 143, 0.2);
        border-radius: 12px;
        margin-bottom: 12px;
        transition: all 0.3s ease;
    }
    
    .stExpander:hover {
        border-color: #2a9d8f;
        box-shadow: 0 6px 12px rgba(42, 157, 143, 0.15);
        transform: translateX(4px);
    }
    
    /* Botones mejorados */
    .stButton > button {
        border-radius: 12px;
        font-weight: 600;
        padding: 12px 24px;
        transition: all 0.3s ease;
        border: none !important;
        font-size: 1rem;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
    }
    
    div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #2a9d8f 0%, #06d6a0 100%);
        color: white !important;
        box-shadow: 0 4px 12px rgba(42, 157, 143, 0.4);
    }
    
    div.stButton > button[kind="secondary"] {
        background: linear-gradient(135deg, #48cae4 0%, #0096c7 100%);
        color: white !important;
        box-shadow: 0 4px 12px rgba(72, 202, 228, 0.4);
    }
    
    /* File uploader */
    .stFileUploader {
        border: 3px dashed rgba(42, 157, 143, 0.3);
        border-radius: 16px;
        padding: 30px;
        transition: all 0.3s ease;
        background: rgba(42, 157, 143, 0.02);
    }
    
    .stFileUploader:hover {
        border-color: #2a9d8f;
        background: rgba(42, 157, 143, 0.05);
        transform: scale(1.01);
    }
    
    /* Tabs mejorados */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(42, 157, 143, 0.05);
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
        background: linear-gradient(135deg, #2a9d8f, #48cae4);
        color: white;
        box-shadow: 0 4px 8px rgba(42, 157, 143, 0.3);
    }
    
    /* Métricas (st.metric) */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(42, 157, 143, 0.1), rgba(72, 202, 228, 0.05));
        padding: 20px;
        border-radius: 12px;
        border: 2px solid rgba(42, 157, 143, 0.2);
        transition: all 0.3s ease;
    }
    
    [data-testid="stMetric"]:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 16px rgba(42, 157, 143, 0.2);
        border-color: #2a9d8f;
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
    
    /* Dividers */
    hr {
        margin: 2rem 0;
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, #2a9d8f, transparent);
        opacity: 0.3;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(42, 157, 143, 0.05);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #2a9d8f, #48cae4);
        border-radius: 10px;
    }
    
    /* Selectbox */
    .stSelectbox > div > div {
        border-radius: 12px;
        border: 2px solid rgba(42, 157, 143, 0.3);
        transition: all 0.3s ease;
    }
    
    .stSelectbox > div > div:hover {
        border-color: #2a9d8f;
        box-shadow: 0 4px 8px rgba(42, 157, 143, 0.15);
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .student-header {
            font-size: 2.5rem;
        }
        .metric-student {
            padding: 20px;
        }
    }
    </style>
""", unsafe_allow_html=True)

# ==================== FUNCIÓN PRINCIPAL ====================

def run_student_app():
    """Función principal que ejecuta toda la interfaz del estudiante"""
    
    # Gestión de notificaciones
    if st.session_state.get('flash_message'):
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

    user = st.session_state.user
    if not user or user['role'] != 'student':
        st.error("Acceso no autorizado")
        if st.button("Volver al inicio"):
            st.session_state.page = "landing"
            st.rerun()
        return
    
    # Sidebar con menú
    with st.sidebar:
        st.image("https://img.icons8.com/fluency/96/noodles.png", width=80)
        st.write(f"Hola, **{user.get('first_name')}** 👋")
        st.caption("🎓 Estudiante")
        
        # Menú de navegación
        menu_options = ["Dashboard", "Mis Cursos", "Tareas", "Calificaciones", "Comunidad", "Perfil"]
        menu_icons = ["house-fill", "book-fill", "clipboard-check-fill", "graph-up", "chat-dots-fill", "person-fill"]
        
        # Verificar si hay una navegación forzada desde un botón
        forced_navigation = st.session_state.get('force_menu_change')
        if forced_navigation:
            st.session_state.student_menu_selection = forced_navigation
            st.session_state.force_menu_change = None  # Limpiar el flag
        
        default_index = 0
        if "student_menu_selection" in st.session_state:
            try:
                default_index = menu_options.index(st.session_state.student_menu_selection)
            except ValueError:
                default_index = 0

        selected_menu = option_menu(
            "Menú", 
            menu_options, 
            icons=menu_icons, 
            menu_icon="mortarboard-fill", 
            default_index=default_index,
            key="student_nav_menu",
            styles={
                "container": {"padding": "0!important"},
                "icon": {"color": "#2a9d8f", "font-size": "20px"}, 
                "nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px"},
                "nav-link-selected": {"background-color": "#2a9d8f"},
            }
        )

        # Si hubo navegación forzada, usar ese valor; si no, usar lo que retorna option_menu
        if forced_navigation:
            current_page = forced_navigation
        else:
            current_page = selected_menu
            st.session_state.student_menu_selection = selected_menu

        st.markdown("---")
        
        # Botón de cerrar sesión
        if st.button("🚪 Cerrar Sesión", type="primary", use_container_width=True):
            st.session_state.token = None
            st.session_state.user = None
            st.session_state.page = "landing"
            if "student_menu_selection" in st.session_state:
                del st.session_state.student_menu_selection
            st.rerun()

    # Enrutamiento de vistas
    if current_page == "Dashboard": 
        dashboard.show()
    elif current_page == "Mis Cursos": 
        courses.show()
    elif current_page == "Tareas": 
        assignments.show()
    elif current_page == "Calificaciones": 
        grades.show()
    elif current_page == "Comunidad":
        community.show()
    elif current_page == "Perfil": 
        profile.show()
    else:
        dashboard.show()