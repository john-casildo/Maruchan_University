import streamlit as st
import requests
import os
from datetime import datetime
import time

API_URL = os.getenv("API_URL", "http://localhost:8000")

# ==================== CSS PERSONALIZADO ====================

def inject_custom_css():
    """Inyecta CSS personalizado para animaciones y estilos"""
    st.markdown("""
        <style>
        /* Animaciones */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        @keyframes slideIn {
            from { transform: translateX(-100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        
        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.05); }
        }
        
        @keyframes shimmer {
            0% { background-position: -1000px 0; }
            100% { background-position: 1000px 0; }
        }
        
        /* Clases de animación */
        .fade-in {
            animation: fadeIn 0.6s ease-out;
        }
        
        .slide-in {
            animation: slideIn 0.8s ease-out;
        }
        
        .pulse {
            animation: pulse 2s infinite;
        }
        
        /* Botones personalizados */
        div.stButton > button {
            border-radius: 10px;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        
        div.stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
        }
        
        /* Tarjetas con hover */
        .hover-card {
            transition: all 0.3s ease;
        }
        
        .hover-card:hover {
            transform: translateY(-3px);
        }
        
        /* Input fields mejorados */
        .stTextInput input, .stTextArea textarea {
            border-radius: 10px !important;
            border: 2px solid #e0e0e0 !important;
            transition: all 0.3s ease !important;
        }
        
        .stTextInput input:focus, .stTextArea textarea:focus {
            border-color: #2a9d8f !important;
            box-shadow: 0 0 0 3px rgba(42, 157, 143, 0.1) !important;
        }
        
        /* Tabs personalizados */
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
            background-color: transparent;
        }
        
        .stTabs [data-baseweb="tab"] {
            border-radius: 10px 10px 0 0;
            padding: 12px 24px;
            background-color: #f8f9fa;
            transition: all 0.3s ease;
            font-weight: 600;
        }
        
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #2a9d8f, #48cae4);
            color: white !important;
        }
        
        /* Expander personalizado */
        .streamlit-expanderHeader {
            border-radius: 10px;
            font-weight: 600;
            background-color: #f8f9fa;
            transition: all 0.3s ease;
        }
        
        .streamlit-expanderHeader:hover {
            background-color: #e9ecef;
        }
        </style>
    """, unsafe_allow_html=True)

# ==================== API FUNCTIONS ====================

def get_current_user(token):
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{API_URL}/api/auth/me", headers=headers, timeout=10)
        if response.status_code == 200: 
            return response.json()
    except: 
        return None
    return None

def update_user_profile(token, user_id, user_data, profile_pic_file=None):
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.put(f"{API_URL}/api/users/{user_id}", headers=headers, json=user_data, timeout=10)
        if response.status_code != 200: 
            return False, response.json()
        updated_user = response.json()
        if profile_pic_file:
            profile_pic_file.seek(0)
            files = {"file": (profile_pic_file.name, profile_pic_file, profile_pic_file.type)}
            img_response = requests.post(f"{API_URL}/api/users/{user_id}/profile-picture", headers=headers, files=files, timeout=15)
            if img_response.status_code == 200: 
                updated_user = img_response.json()
            else: 
                return False, {"detail": "Error en imagen"}
        return True, updated_user
    except Exception as e: 
        return False, {"detail": str(e)}

def change_password_api(token: str, user_id: int, new_password: str):
    try:
        headers = {"Authorization": f"Bearer {token}"}
        data = {
            "password": new_password,
            "password_confirm": new_password
        }
        response = requests.patch(
            f"{API_URL}/api/users/{user_id}/password",
            headers=headers,
            json=data,
            timeout=10
        )
        if response.status_code == 200:
            return True, response.json()
        return False, response.json()
    except Exception as e:
        return False, {"detail": str(e)}

# ==================== HELPER FUNCTIONS ====================

def format_date(date_str):
    """Formatea una fecha ISO a formato legible"""
    if not date_str or date_str == 'N/A':
        return 'N/A'
    
    try:
        if 'T' in str(date_str):
            date_obj = datetime.fromisoformat(str(date_str).replace('Z', '+00:00'))
            return date_obj.strftime('%d/%m/%Y')
        return date_str
    except:
        return str(date_str)

# ==================== UI COMPONENTS ====================

def render_animated_header():
    """Header animado con gradiente"""
    st.markdown("""
        <div class="fade-in" style="
            background: linear-gradient(135deg, #2a9d8f 0%, #48cae4 50%, #0096c7 100%);
            padding: 50px 40px;
            border-radius: 25px;
            margin-bottom: 30px;
            box-shadow: 0 15px 35px rgba(42, 157, 143, 0.4);
            position: relative;
            overflow: hidden;
        ">
            <div style="
                position: absolute;
                top: -50%;
                right: -50%;
                width: 200%;
                height: 200%;
                background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
                animation: pulse 3s infinite;
            "></div>
            <h1 style="
                color: white;
                font-size: 3.5rem;
                font-weight: 900;
                margin: 0;
                text-align: center;
                text-shadow: 3px 3px 6px rgba(0,0,0,0.3);
                position: relative;
                z-index: 1;
            ">👤 Mi Perfil Estudiantil</h1>
            <p style="
                color: rgba(255,255,255,0.95);
                text-align: center;
                font-size: 1.2rem;
                margin-top: 10px;
                position: relative;
                z-index: 1;
            ">Gestiona tu información personal y configuración</p>
        </div>
    """, unsafe_allow_html=True)

def render_profile_card(user):
    """Tarjeta de perfil interactiva"""
    
    # Obtener URL de imagen
    image_url = None
    if user.get('profile_pic_url'):
        base_url = API_URL.rstrip("/")
        if "backend" in base_url:
            base_url = base_url.replace("backend", "localhost")
        image_url = f"{base_url}{user['profile_pic_url']}"
    
    # Formatear datos
    carnet = user.get('carnet') if user.get('carnet') else 'No asignado'
    joined_date = format_date(user.get('joined_date'))
    
    st.markdown("""
        <div class="fade-in hover-card" style="
            background: linear-gradient(135deg, rgba(255,255,255,0.9), rgba(248,249,250,0.9));
            padding: 40px;
            border-radius: 25px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.5);
            margin-bottom: 30px;
        ">
    """, unsafe_allow_html=True)
    
    col_photo, col_info = st.columns([1, 2])
    
    with col_photo:
        # Foto de perfil con efecto hover
        if image_url:
            st.markdown(f"""
                <div style="text-align: center;">
                    <div style="
                        width: 220px;
                        height: 220px;
                        margin: 0 auto;
                        border-radius: 50%;
                        overflow: hidden;
                        border: 6px solid transparent;
                        background: linear-gradient(135deg, #2a9d8f, #48cae4, #06d6a0);
                        padding: 4px;
                        box-shadow: 0 10px 30px rgba(42, 157, 143, 0.4);
                        transition: all 0.3s ease;
                        position: relative;
                    " class="hover-card">
                        <div style="
                            width: 100%;
                            height: 100%;
                            border-radius: 50%;
                            overflow: hidden;
                            background: white;
                        ">
                            <img src="{image_url}" style="
                                width: 100%;
                                height: 100%;
                                object-fit: cover;
                            ">
                        </div>
                    </div>
                    <div style="
                        margin-top: 15px;
                        font-weight: 600;
                        color: #2a9d8f;
                        font-size: 1rem;
                    ">
                        📸 Foto de Perfil
                    </div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
                <div style="text-align: center;">
                    <div style="
                        width: 220px;
                        height: 220px;
                        margin: 0 auto;
                        border-radius: 50%;
                        background: linear-gradient(135deg, #2a9d8f, #48cae4);
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        box-shadow: 0 10px 30px rgba(42, 157, 143, 0.4);
                        transition: all 0.3s ease;
                    " class="hover-card pulse">
                        <span style="font-size: 6rem; filter: drop-shadow(2px 2px 4px rgba(0,0,0,0.2));">👤</span>
                    </div>
                    <div style="
                        margin-top: 15px;
                        font-weight: 600;
                        color: #2a9d8f;
                        font-size: 1rem;
                    ">
                        📸 Sin foto de perfil
                    </div>
                </div>
            """, unsafe_allow_html=True)
    
    with col_info:
        # Información del usuario - TODO EN UNA SOLA CADENA
        st.markdown(f"""
            <div style="padding: 20px;">
                <h2 style="
                    color: #1a1a2e;
                    font-size: 2.8rem;
                    font-weight: 900;
                    margin: 0 0 20px 0;
                    background: linear-gradient(135deg, #2a9d8f, #48cae4);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    background-clip: text;
                ">
                    {user.get('full_name', 'Usuario')}
                </h2>
                
                <div style="margin-bottom: 20px;">
                    <span style="
                        background: linear-gradient(135deg, #48cae4, #0096c7);
                        color: white;
                        padding: 8px 16px;
                        border-radius: 20px;
                        font-size: 0.85rem;
                        font-weight: 600;
                        margin-right: 5px;
                        display: inline-block;
                    ">🎓 Estudiante Activo</span>
                    <span style="
                        background: linear-gradient(135deg, #06d6a0, #06ffa5);
                        color: white;
                        padding: 8px 16px;
                        border-radius: 20px;
                        font-size: 0.85rem;
                        font-weight: 600;
                        display: inline-block;
                    ">✅ Verificado</span>
                </div>
                
                <div style="
                    background: linear-gradient(135deg, rgba(42, 157, 143, 0.08), rgba(72, 202, 228, 0.08));
                    padding: 25px;
                    border-radius: 15px;
                    border-left: 4px solid #2a9d8f;
                    margin-top: 20px;
                ">
                    <div style="margin-bottom: 18px;">
                        <div style="display: flex; align-items: center;">
                            <div style="
                                width: 45px;
                                height: 45px;
                                background: linear-gradient(135deg, #2a9d8f, #48cae4);
                                border-radius: 12px;
                                display: flex;
                                align-items: center;
                                justify-content: center;
                                margin-right: 15px;
                                box-shadow: 0 4px 10px rgba(42, 157, 143, 0.3);
                            ">
                                <span style="font-size: 1.5rem;">👤</span>
                            </div>
                            <div>
                                <div style="color: #888; font-size: 0.8rem; font-weight: 600;">USUARIO</div>
                                <div style="color: #1a1a2e; font-size: 1.15rem; font-weight: 700;">{user.get('username', 'N/A')}</div>
                            </div>
                        </div>
                    </div>
                    
                    <div style="margin-bottom: 18px;">
                        <div style="display: flex; align-items: center;">
                            <div style="
                                width: 45px;
                                height: 45px;
                                background: linear-gradient(135deg, #48cae4, #0096c7);
                                border-radius: 12px;
                                display: flex;
                                align-items: center;
                                justify-content: center;
                                margin-right: 15px;
                                box-shadow: 0 4px 10px rgba(72, 202, 228, 0.3);
                            ">
                                <span style="font-size: 1.5rem;">📧</span>
                            </div>
                            <div>
                                <div style="color: #888; font-size: 0.8rem; font-weight: 600;">CORREO ELECTRÓNICO</div>
                                <div style="color: #1a1a2e; font-size: 1.15rem; font-weight: 700;">{user.get('email', 'N/A')}</div>
                            </div>
                        </div>
                    </div>
                    
                    <div style="margin-bottom: 18px;">
                        <div style="display: flex; align-items: center;">
                            <div style="
                                width: 45px;
                                height: 45px;
                                background: linear-gradient(135deg, #06d6a0, #06ffa5);
                                border-radius: 12px;
                                display: flex;
                                align-items: center;
                                justify-content: center;
                                margin-right: 15px;
                                box-shadow: 0 4px 10px rgba(6, 214, 160, 0.3);
                            ">
                                <span style="font-size: 1.5rem;">🎓</span>
                            </div>
                            <div>
                                <div style="color: #888; font-size: 0.8rem; font-weight: 600;">CARNET ESTUDIANTIL</div>
                                <div style="color: #1a1a2e; font-size: 1.15rem; font-weight: 700;">{carnet}</div>
                            </div>
                        </div>
                    </div>
                    
                    <div>
                        <div style="display: flex; align-items: center;">
                            <div style="
                                width: 45px;
                                height: 45px;
                                background: linear-gradient(135deg, #ffb703, #fb8500);
                                border-radius: 12px;
                                display: flex;
                                align-items: center;
                                justify-content: center;
                                margin-right: 15px;
                                box-shadow: 0 4px 10px rgba(255, 183, 3, 0.3);
                            ">
                                <span style="font-size: 1.5rem;">📅</span>
                            </div>
                            <div>
                                <div style="color: #888; font-size: 0.8rem; font-weight: 600;">MIEMBRO DESDE</div>
                                <div style="color: #1a1a2e; font-size: 1.15rem; font-weight: 700;">{joined_date}</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

def render_stats_cards(user):
    """Tarjetas de estadísticas animadas"""
    st.markdown("""
        <div style="margin: 30px 0;">
            <h3 style="
                color: #1a1a2e;
                font-size: 1.8rem;
                font-weight: 700;
                margin-bottom: 20px;
                text-align: center;
            ">📊 Resumen de Actividad</h3>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    stats = [
        ("🎯", "Cursos<br>Inscritos", "8", "#2a9d8f"),
        ("📚", "Tareas<br>Completadas", "42", "#48cae4"),
        ("⭐", "Promedio<br>General", "9.2", "#06d6a0"),
        ("🏆", "Logros<br>Obtenidos", "15", "#ffb703")
    ]
    
    for col, (icon, label, value, color) in zip([col1, col2, col3, col4], stats):
        with col:
            st.markdown(f"""
                <div class="hover-card" style="
                    background: linear-gradient(135deg, {color}15, {color}08);
                    padding: 25px 15px;
                    border-radius: 20px;
                    text-align: center;
                    border: 2px solid {color}30;
                    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08);
                    transition: all 0.3s ease;
                ">
                    <div style="font-size: 3rem; margin-bottom: 10px;">{icon}</div>
                    <div style="
                        color: #888;
                        font-size: 0.85rem;
                        font-weight: 600;
                        margin-bottom: 8px;
                        text-transform: uppercase;
                        letter-spacing: 0.5px;
                    ">{label}</div>
                    <div style="
                        color: {color};
                        font-size: 2.2rem;
                        font-weight: 900;
                    ">{value}</div>
                </div>
            """, unsafe_allow_html=True)

def render_edit_form(user):
    """Formulario de edición mejorado"""
    st.markdown("""
        <div class="slide-in" style="
            background: linear-gradient(135deg, rgba(72, 202, 228, 0.12), rgba(42, 157, 143, 0.08));
            padding: 30px;
            border-radius: 20px;
            border-left: 5px solid #48cae4;
            margin-bottom: 25px;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
        ">
            <h3 style="
                color: #48cae4;
                margin: 0 0 10px 0;
                font-size: 1.8rem;
                font-weight: 800;
            ">✏️ Editar Información Personal</h3>
            <p style="
                color: #666;
                margin: 0;
                font-size: 0.95rem;
            ">Actualiza tus datos personales de forma segura</p>
        </div>
    """, unsafe_allow_html=True)
    
    with st.form("edit_profile_form", clear_on_submit=False):
        st.markdown("### 📝 Datos Básicos")
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            new_first_name = st.text_input(
                "Nombre *", 
                value=user.get('first_name', ''),
                placeholder="Ingresa tu nombre",
                help="Campo obligatorio"
            )
            new_last_name = st.text_input(
                "Apellido *", 
                value=user.get('last_name', ''),
                placeholder="Ingresa tu apellido",
                help="Campo obligatorio"
            )
            new_email = st.text_input(
                "Email *", 
                value=user.get('email', ''),
                placeholder="tu@email.com",
                help="Tu correo institucional"
            )
        
        with col_b:
            new_phone = st.text_input(
                "📱 Teléfono", 
                value=user.get('phone') or '',
                placeholder="+506 8888-8888",
                help="Opcional"
            )
            new_middle_name = st.text_input(
                "Segundo Nombre", 
                value=user.get('middle_name') or '',
                placeholder="Opcional",
                help="Campo opcional"
            )
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### 📷 Foto de Perfil")
        
        col_img1, col_img2 = st.columns([2, 1])
        
        with col_img1:
            new_profile_pic = st.file_uploader(
                "Subir nueva foto",
                type=['png', 'jpg', 'jpeg'],
                help="Formatos permitidos: PNG, JPG, JPEG (máx. 5MB)"
            )
            
            if new_profile_pic:
                file_size_mb = new_profile_pic.size / (1024 * 1024)
                if file_size_mb > 5:
                    st.error(f"⚠️ Archivo muy grande: {file_size_mb:.1f}MB (máx. 5MB)")
                else:
                    st.success(f"✅ Archivo válido: {file_size_mb:.2f}MB")
        
        with col_img2:
            if new_profile_pic and new_profile_pic.size <= 5 * 1024 * 1024:
                st.image(new_profile_pic, caption="Preview", width=150)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
        with col_btn1:
            submit_update = st.form_submit_button(
                "💾 Guardar Todos los Cambios",
                type="primary",
                use_container_width=True
            )
        
        if submit_update:
            # Validaciones
            if not new_first_name or not new_last_name or not new_email:
                st.error("❌ Por favor completa todos los campos obligatorios (*)")
                return
            
            if "@" not in new_email:
                st.error("❌ Email inválido")
                return
            
            if new_profile_pic and new_profile_pic.size > 5 * 1024 * 1024:
                st.error("❌ La imagen es muy grande (máx. 5MB)")
                return
            
            update_data = {
                "first_name": new_first_name.strip(),
                "last_name": new_last_name.strip(),
                "email": new_email.strip(),
                "phone": new_phone.strip() if new_phone else None,
                "middle_name": new_middle_name.strip() if new_middle_name else None
            }
            
            # Animación de carga
            with st.spinner("🔄 Actualizando tu perfil..."):
                progress_bar = st.progress(0)
                for i in range(100):
                    time.sleep(0.01)
                    progress_bar.progress(i + 1)
                
                success, result = update_user_profile(
                    st.session_state.token, 
                    user['id'], 
                    update_data,
                    profile_pic_file=new_profile_pic
                )
                
                progress_bar.empty()
                
                if success:
                    updated_user = get_current_user(st.session_state.token)
                    if updated_user:
                        st.session_state.user = updated_user
                    else:
                        st.session_state.user = result
                    
                    st.success("✅ ¡Perfil actualizado exitosamente!")
                    st.balloons()
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(f"❌ Error: {result.get('detail', 'Error desconocido')}")

def render_password_section(user):
    """Sección de cambio de contraseña mejorada"""
    st.markdown("""
        <div class="slide-in" style="
            background: linear-gradient(135deg, rgba(239, 71, 111, 0.12), rgba(214, 40, 40, 0.08));
            padding: 30px;
            border-radius: 20px;
            border-left: 5px solid #ef476f;
            margin-bottom: 25px;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
        ">
            <h3 style="
                color: #ef476f;
                margin: 0 0 10px 0;
                font-size: 1.8rem;
                font-weight: 800;
            ">🔒 Seguridad de la Cuenta</h3>
            <p style="
                color: #666;
                margin: 0;
                font-size: 0.95rem;
            ">Protege tu cuenta con una contraseña segura</p>
        </div>
    """, unsafe_allow_html=True)
    
    with st.expander("🔐 Cambiar mi contraseña", expanded=False):
        st.markdown("""
            <div style="
                background: linear-gradient(135deg, rgba(255, 183, 3, 0.1), rgba(251, 133, 0, 0.05));
                padding: 15px;
                border-radius: 10px;
                margin-bottom: 20px;
                border-left: 3px solid #ffb703;
            ">
                <strong>⚠️ Recomendaciones de Seguridad:</strong><br>
                • Usa al menos 8 caracteres<br>
                • Combina mayúsculas y minúsculas<br>
                • Incluye números y símbolos<br>
                • No uses información personal obvia
            </div>
        """, unsafe_allow_html=True)
        
        with st.form("change_my_pass_form", clear_on_submit=True):
            col_p1, col_p2 = st.columns(2)
            
            with col_p1:
                p1 = st.text_input(
                    "🔑 Nueva Contraseña",
                    type="password",
                    placeholder="Mínimo 8 caracteres"
                )
            
            with col_p2:
                p2 = st.text_input(
                    "🔑 Confirmar Contraseña",
                    type="password",
                    placeholder="Repite la contraseña"
                )
            
            # Medidor de fortaleza
            if p1:
                strength = 0
                checks = {
                    "Longitud (8+ caracteres)": len(p1) >= 8,
                    "Mayúsculas": any(c.isupper() for c in p1),
                    "Minúsculas": any(c.islower() for c in p1),
                    "Números": any(c.isdigit() for c in p1),
                    "Símbolos": any(c in "!@#$%^&*()_+-=" for c in p1)
                }
                
                strength = sum(checks.values())
                
                st.markdown("**📊 Fortaleza de la Contraseña:**")
                
                if strength <= 2:
                    color = "#ef476f"
                    label = "Débil"
                    emoji = "❌"
                elif strength <= 3:
                    color = "#ffb703"
                    label = "Aceptable"
                    emoji = "⚠️"
                else:
                    color = "#06d6a0"
                    label = "Fuerte"
                    emoji = "✅"
                
                st.markdown(f"""
                    <div style="
                        background: #f0f0f0;
                        border-radius: 10px;
                        height: 12px;
                        margin: 10px 0;
                        overflow: hidden;
                    ">
                        <div style="
                            background: linear-gradient(90deg, {color}, {color}dd);
                            width: {strength * 20}%;
                            height: 100%;
                            transition: all 0.3s ease;
                            border-radius: 10px;
                        "></div>
                    </div>
                    <div style="color: {color}; font-weight: 700; margin-bottom: 15px;">
                        {emoji} {label} ({strength}/5)
                    </div>
                """, unsafe_allow_html=True)
                
                for check_name, passed in checks.items():
                    icon = "✅" if passed else "⭕"
                    color_check = "#06d6a0" if passed else "#cccccc"
                    st.markdown(f"""
                        <div style="color: {color_check}; font-size: 0.9rem; margin-bottom: 5px;">
                            {icon} {check_name}
                        </div>
                    """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            col_btn1, col_btn2 = st.columns([1, 2])
            with col_btn1:
                submit_pass = st.form_submit_button(
                    "🔄 Actualizar Contraseña",
                    type="primary",
                    use_container_width=True
                )
            
            if submit_pass:
                if not p1 or not p2:
                    st.error("❌ Por favor completa ambos campos")
                elif p1 != p2:
                    st.error("❌ Las contraseñas no coinciden")
                elif len(p1) < 8:
                    st.error("❌ La contraseña debe tener al menos 8 caracteres")
                else:
                    with st.spinner("🔄 Actualizando contraseña..."):
                        success, msg = change_password_api(st.session_state.token, user['id'], p1)
                        if success:
                            st.success("✅ ¡Contraseña actualizada correctamente!")
                            st.balloons()
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(f"❌ Error: {msg.get('detail')}")

# ==================== MAIN FUNCTION ====================

def show():
    """Vista interactiva del perfil del estudiante"""
    
    # Inyectar CSS
    inject_custom_css()
    
    # Verificar sesión
    if 'token' not in st.session_state or 'user' not in st.session_state:
        st.error("❌ Sesión no válida. Por favor inicia sesión nuevamente.")
        return
    
    user = st.session_state.user
    
    if user is None:
        st.error("❌ No se pudo cargar la información del usuario")
        return
    
    # Botón de navegación
    col_nav1, col_nav2, col_nav3 = st.columns([1, 2, 1])
    with col_nav1:
        if st.button("⬅️ Volver al Dashboard", key="back_btn", use_container_width=True):
            st.session_state.student_menu_selection = "Dashboard"
            st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Header
    render_animated_header()
    
    # Perfil
    render_profile_card(user)
    
    # Estadísticas
    render_stats_cards(user)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Tabs
    tab1, tab2 = st.tabs([
        "✏️ Editar Información",
        "🔒 Seguridad"
    ])
    
    with tab1:
        render_edit_form(user)
    
    with tab2:
        render_password_section(user)
    
    # Footer
    st.markdown("<br><br>", unsafe_allow_html=True)
    col_footer1, col_footer2, col_footer3 = st.columns([1, 1, 1])
    with col_footer2:
        if st.button("🏠 Regresar al Inicio", key="back_bottom", type="primary", use_container_width=True):
            st.session_state.student_menu_selection = "Dashboard"
            st.rerun()

if __name__ == "__main__":
    st.set_page_config(
        page_title="Mi Perfil - Estudiante",
        page_icon="👤",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    show()