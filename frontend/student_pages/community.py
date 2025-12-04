"""
Módulo de Comunidad/Chat para Estudiantes
==========================================
Permite a los estudiantes comunicarse con otros usuarios del sistema.
"""

import streamlit as st
import requests

API_URL = "http://backend:8000"

# ==================== FUNCIONES DE API ====================

def get_online_users_api(token):
    """Obtiene usuarios online"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{API_URL}/api/chat/users/online", headers=headers)
        return response.json() if response.status_code == 200 else []
    except:
        return []

def get_students(token):
    """Obtiene todos los estudiantes"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{API_URL}/api/users/by-role/student", headers=headers)
        return response.json() if response.status_code == 200 else []
    except:
        return []

def get_teachers(token):
    """Obtiene todos los profesores"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{API_URL}/api/users/by-role/teacher", headers=headers)
        return response.json() if response.status_code == 200 else []
    except:
        return []

def get_admins(token):
    """Obtiene todos los administradores"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{API_URL}/api/users/by-role/admin", headers=headers)
        return response.json() if response.status_code == 200 else []
    except:
        return []

def send_message_api(token, receiver_id, content):
    """Envía un mensaje a otro usuario"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        data = {"receiver_id": receiver_id, "content": content}
        response = requests.post(f"{API_URL}/api/chat/send", headers=headers, json=data)
        return response.status_code == 200
    except:
        return False

def get_chat_history_api(token, other_user_id):
    """Obtiene el historial de chat con otro usuario"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{API_URL}/api/chat/history/{other_user_id}", headers=headers)
        return response.json() if response.status_code == 200 else []
    except:
        return []

# ==================== COMPONENTES DE UI ====================

def show_active_chat(selected_user_id, user_map, my_id, online_ids):
    """
    Muestra el historial y el input con un botón manual de recarga.
    """
    target_user = user_map[selected_user_id]
    is_online = selected_user_id in online_ids
    status_badge = "🟢 En línea" if is_online else "⚪ Desconectado"
    role_map = {"admin": "Administrador", "teacher": "Profesor", "student": "Estudiante"}
    
    # Header del chat estilizado
    st.markdown(f"""
        <div style="background: linear-gradient(145deg, rgba(42, 157, 143, 0.08), rgba(72, 202, 228, 0.04));
                    padding: 15px 20px; border-radius: 12px; margin-bottom: 15px;
                    border: 2px solid rgba(42, 157, 143, 0.15);">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h3 style="margin: 0; color: #2a9d8f;">💬 {target_user['full_name']}</h3>
                    <span style="color: #666; font-size: 0.9rem;">{role_map.get(target_user.get('role', ''), target_user.get('role', ''))}</span>
                </div>
                <span style="background: {'#06d6a0' if is_online else '#888'}22; 
                            color: {'#06d6a0' if is_online else '#888'}; 
                            padding: 5px 12px; border-radius: 15px; font-size: 0.85rem;">
                    {status_badge}
                </span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    col_spacer, col_btn = st.columns([4, 1])
    with col_btn:
        if st.button("🔄 Actualizar", key="manual_refresh_chat", type="secondary", use_container_width=True):
            st.rerun()
    
    # --- CONTENEDOR DE MENSAJES ---
    chat_container = st.container(height=380)
    
    # Obtener historial desde la API
    history = get_chat_history_api(st.session_state.token, selected_user_id)
    
    with chat_container:
        if not history:
            st.markdown("""
                <div style="text-align: center; padding: 60px 20px; color: #888;">
                    <div style="font-size: 3rem; margin-bottom: 15px;">👋</div>
                    <p style="color: #2a9d8f; font-weight: 500;">¡Aún no hay mensajes!</p>
                    <p style="font-size: 0.9rem;">Sé el primero en saludar</p>
                </div>
            """, unsafe_allow_html=True)
        else:
            for msg in history:
                is_me = msg['sender_id'] == my_id
                with st.chat_message("user" if is_me else "assistant", avatar="👤" if is_me else "🎓"):
                    st.write(msg['content'])
                    ts = msg['timestamp']
                    try:
                        time_str = ts.split("T")[1][:5]
                    except:
                        time_str = ts
                    st.caption(f"🕐 {time_str}")

    # --- INPUT DE MENSAJE ---
    if prompt := st.chat_input(f"Escribe a {target_user['full_name']}..."):
        if send_message_api(st.session_state.token, selected_user_id, prompt):
            st.rerun()
        else:
            st.error("❌ Error al enviar mensaje")

# ==================== FUNCIÓN PRINCIPAL ====================

def show():
    """Vista principal de Comunidad para estudiantes"""
    
    # Header con gradiente igual que dashboard
    st.markdown("""
        <div style="background: linear-gradient(135deg, #2a9d8f 0%, #48cae4 100%); 
                    padding: 40px; border-radius: 20px; margin-bottom: 30px;
                    box-shadow: 0 10px 30px rgba(42, 157, 143, 0.3);">
            <h1 style="color: white; margin: 0; font-size: 2.8rem; text-align: center; 
                       text-shadow: 2px 2px 4px rgba(0,0,0,0.2);">
                💬 Comunidad Universitaria
            </h1>
            <p style="color: rgba(255,255,255,0.9); margin: 15px 0 0 0; font-size: 1.2rem; text-align: center;">
                Conecta con profesores, compañeros y administradores
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Obtener datos de usuarios
    online_users = get_online_users_api(st.session_state.token)
    online_ids = [u['id'] for u in online_users]
    
    all_students = get_students(st.session_state.token)
    all_teachers = get_teachers(st.session_state.token)
    all_admins = get_admins(st.session_state.token)
    
    # Crear mapa de usuarios
    full_list = all_students + all_teachers + all_admins
    user_map = {u['id']: u for u in full_list}
    
    my_id = st.session_state.user['id']
    
    # Remover al usuario actual de la lista
    if my_id in user_map:
        del user_map[my_id]
    
    # Calcular estadísticas
    online_count = len([uid for uid in user_map.keys() if uid in online_ids])
    teachers_count = len([u for u in user_map.values() if u.get('role') == 'teacher'])
    students_count = len([u for u in user_map.values() if u.get('role') == 'student'])
    
    # Tarjetas de estadísticas con gradientes
    st.markdown("""
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-bottom: 25px;">
            <div style="background: linear-gradient(135deg, #06d6a0, #1b9e77); padding: 20px; 
                        border-radius: 15px; text-align: center; box-shadow: 0 4px 15px rgba(6, 214, 160, 0.3);">
                <div style="font-size: 2rem; color: white;">🟢</div>
                <div style="font-size: 1.8rem; font-weight: bold; color: white;">""" + str(online_count) + """</div>
                <div style="color: rgba(255,255,255,0.9); font-size: 0.9rem;">En línea</div>
            </div>
            <div style="background: linear-gradient(135deg, #0077b6, #48cae4); padding: 20px; 
                        border-radius: 15px; text-align: center; box-shadow: 0 4px 15px rgba(0, 119, 182, 0.3);">
                <div style="font-size: 2rem; color: white;">👨‍🏫</div>
                <div style="font-size: 1.8rem; font-weight: bold; color: white;">""" + str(teachers_count) + """</div>
                <div style="color: rgba(255,255,255,0.9); font-size: 0.9rem;">Profesores</div>
            </div>
            <div style="background: linear-gradient(135deg, #e9c46a, #f4a261); padding: 20px; 
                        border-radius: 15px; text-align: center; box-shadow: 0 4px 15px rgba(233, 196, 106, 0.3);">
                <div style="font-size: 2rem; color: white;">🎓</div>
                <div style="font-size: 1.8rem; font-weight: bold; color: white;">""" + str(students_count) + """</div>
                <div style="color: rgba(255,255,255,0.9); font-size: 0.9rem;">Compañeros</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    col_users, col_chat = st.columns([1, 2])
    
    with col_users:
        # Panel de contactos estilizado
        st.markdown("""
            <div style="background: linear-gradient(145deg, rgba(42, 157, 143, 0.08), rgba(72, 202, 228, 0.04));
                        padding: 15px; border-radius: 12px; border: 2px solid rgba(42, 157, 143, 0.15);
                        margin-bottom: 15px;">
                <h3 style="color: #2a9d8f; margin: 0;">📇 Contactos</h3>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔄 Actualizar", type="secondary", use_container_width=True):
            st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Filtros estilizados
        filter_role = st.selectbox(
            "🔍 Filtrar por rol:",
            ["Todos", "Profesores", "Estudiantes", "Admins"],
            key="community_filter"
        )
        
        contact_options = []
        
        # Ordenar: Online primero
        for uid, udata in user_map.items():
            # Aplicar filtro
            if filter_role == "Profesores" and udata.get('role') != 'teacher':
                continue
            elif filter_role == "Estudiantes" and udata.get('role') != 'student':
                continue
            elif filter_role == "Admins" and udata.get('role') != 'admin':
                continue
            
            if uid in online_ids:
                contact_options.insert(0, uid)  # Online al inicio
            else:
                contact_options.append(uid)
        
        if not contact_options:
            st.markdown("""
                <div style="background: rgba(42, 157, 143, 0.1); padding: 20px; border-radius: 10px; 
                            text-align: center; margin-top: 15px;">
                    <div style="font-size: 2rem; margin-bottom: 10px;">📭</div>
                    <p style="color: #666; margin: 0;">No hay usuarios disponibles</p>
                </div>
            """, unsafe_allow_html=True)
            selected_user_id = None
        else:
            def format_user_option(uid):
                user = user_map[uid]
                status = "🟢" if uid in online_ids else "⚪"
                role_map = {"admin": "🛡️", "teacher": "👨‍🏫", "student": "🎓"}
                role_icon = role_map.get(user.get('role', ''), "👤")
                return f"{status} {role_icon} {user['full_name']}"

            selected_user_id = st.radio(
                "Seleccionar chat:",
                options=contact_options,
                format_func=format_user_option,
                label_visibility="collapsed"
            )
    
    with col_chat:
        if selected_user_id:
            show_active_chat(selected_user_id, user_map, my_id, online_ids)
        else:
            st.markdown("""
                <div style="background: linear-gradient(145deg, rgba(42, 157, 143, 0.05), rgba(72, 202, 228, 0.03));
                            padding: 60px 30px; border-radius: 20px; text-align: center;
                            border: 2px dashed rgba(42, 157, 143, 0.2);">
                    <div style="font-size: 5rem; margin-bottom: 20px;">💬</div>
                    <h2 style="color: #2a9d8f; margin-bottom: 10px;">¡Comienza a chatear!</h2>
                    <p style="color: #666; font-size: 1.1rem;">
                        Selecciona un contacto de la lista para iniciar una conversación
                    </p>
                    <div style="margin-top: 20px; display: flex; justify-content: center; gap: 15px; flex-wrap: wrap;">
                        <span style="background: #2a9d8f22; color: #2a9d8f; padding: 8px 15px; 
                                    border-radius: 20px; font-size: 0.9rem;">👨‍🏫 Profesores</span>
                        <span style="background: #48cae422; color: #0077b6; padding: 8px 15px; 
                                    border-radius: 20px; font-size: 0.9rem;">🎓 Compañeros</span>
                        <span style="background: #e9c46a22; color: #e76f51; padding: 8px 15px; 
                                    border-radius: 20px; font-size: 0.9rem;">🛡️ Admins</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
