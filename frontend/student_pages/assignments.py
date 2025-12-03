import streamlit as st
import requests
import os

API_URL = os.getenv("API_URL", "http://localhost:8000")

def get_my_courses(token):
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{API_URL}/api/courses/my-courses", headers=headers)
        if response.status_code == 200: 
            return response.json()
        return []
    except: 
        return []

def get_assignments(token, course_id=None):
    try:
        headers = {"Authorization": f"Bearer {token}"}
        params = {"course_id": course_id} if course_id else {}
        response = requests.get(f"{API_URL}/api/assignments/", headers=headers, params=params)
        if response.status_code == 200: 
            return response.json()
        return []
    except: 
        return []

def get_my_submissions(token):
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{API_URL}/api/submissions/my-submissions", headers=headers)
        if response.status_code == 200: 
            return response.json()
        return []
    except: 
        return []

def upload_submission(token, assignment_id, file):
    try:
        headers = {"Authorization": f"Bearer {token}"}
        files = {"file": (file.name, file, file.type)}
        data = {"assignment_id": assignment_id}
        response = requests.post(f"{API_URL}/api/submissions/upload", headers=headers, files=files, data=data)
        return response.status_code == 201, response.json()
    except Exception as e: 
        return False, {"detail": str(e)}

def show():
    """Vista mejorada de tareas del estudiante"""
    
    # Inicializar vista activa
    if "active_task_view" not in st.session_state:
        st.session_state.active_task_view = "pendientes"  # pendientes, vencidas, entregadas
    
    # Botón de regreso
    col_back, col_spacer = st.columns([1, 5])
    with col_back:
        if st.button("⬅️ Volver al Inicio", key="back_to_dashboard", type="secondary", use_container_width=True):
            st.session_state.student_menu_selection = "Dashboard"
            st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Header
    st.markdown("""
        <div style="
            background: linear-gradient(135deg, #f77f00 0%, #fca311 100%);
            padding: 40px;
            border-radius: 20px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(247, 127, 0, 0.3);
        ">
            <h1 style="
                color: white;
                font-size: 3rem;
                font-weight: 800;
                margin: 0;
                text-align: center;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
            ">📝 Mis Tareas</h1>
        </div>
    """, unsafe_allow_html=True)
    
    # Filtro por curso
    courses = get_my_courses(st.session_state.token)
    
    if courses:
        course_options = {c['id']: f"{c['code']} - {c['title']}" for c in courses}
        
        st.markdown("""
            <div style="margin-bottom: 20px;">
                <h3 style="color: #f77f00; font-size: 1.2rem;">🔍 Filtrar por Curso</h3>
            </div>
        """, unsafe_allow_html=True)
        
        selected_course = st.selectbox(
            "Selecciona un curso",
            options=[None] + list(course_options.keys()),
            format_func=lambda x: "📚 Todos los cursos" if x is None else f"📖 {course_options[x]}",
            label_visibility="collapsed"
        )
    else:
        selected_course = None
    
    # Obtener tareas y entregas
    assignments = get_assignments(st.session_state.token, selected_course)
    submissions = get_my_submissions(st.session_state.token)
    submitted_ids = [s['assignment_id'] for s in submissions]
    
    # Clasificar tareas
    pending_on_time = []
    pending_overdue = []
    submitted_list = []
    
    for assignment in assignments:
        if assignment['id'] in submitted_ids:
            submitted_list.append(assignment)
        else:
            if assignment.get('is_overdue', False):
                pending_overdue.append(assignment)
            else:
                pending_on_time.append(assignment)
    
    # TARJETAS CLICKEABLES COMO BOTONES
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button(f"📖\n\nPendientes OK\n\n{len(pending_on_time)}", key="btn_pending", use_container_width=True):
            st.session_state.active_task_view = "pendientes"
            st.rerun()
    
    with col2:
        if st.button(f"⏰\n\nVencidas\n\n{len(pending_overdue)}", key="btn_overdue", use_container_width=True):
            st.session_state.active_task_view = "vencidas"
            st.rerun()
    
    with col3:
        if st.button(f"📤\n\nEntregadas\n\n{len(submitted_list)}", key="btn_submitted", use_container_width=True):
            st.session_state.active_task_view = "entregadas"
            st.rerun()
    
    with col4:
        st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #f77f00, #fca311);
                padding: 20px;
                border-radius: 12px;
                text-align: center;
                color: white;
                box-shadow: 0 4px 12px rgba(247, 127, 0, 0.3);
                margin-top: 8px;
            ">
                <div style="font-size: 2rem;">📊</div>
                <div style="font-size: 0.8rem; opacity: 0.9; margin: 5px 0;">Total</div>
                <div style="font-size: 1.8rem; font-weight: 700;">{len(assignments)}</div>
            </div>
        """, unsafe_allow_html=True)
    
    # Estilos CSS personalizados para los botones
    st.markdown("""
        <style>
        /* Botón de Pendientes OK - Verde */
        button[kind="secondary"]:has-text("Pendientes OK") {
            background: linear-gradient(135deg, #06d6a0, #2a9d8f) !important;
            color: white !important;
            height: 120px !important;
            font-size: 1.1rem !important;
            font-weight: 700 !important;
        }
        
        /* Botón de Vencidas - Rojo */
        button[kind="secondary"]:has-text("Vencidas") {
            background: linear-gradient(135deg, #ef476f, #d62828) !important;
            color: white !important;
            height: 120px !important;
            font-size: 1.1rem !important;
            font-weight: 700 !important;
        }
        
        /* Botón de Entregadas - Azul */
        button[kind="secondary"]:has-text("Entregadas") {
            background: linear-gradient(135deg, #48cae4, #0096c7) !important;
            color: white !important;
            height: 120px !important;
            font-size: 1.1rem !important;
            font-weight: 700 !important;
        }
        
        /* Todos los botones de tarjetas */
        div[data-testid="column"] button[key^="btn_"] {
            height: 120px !important;
            font-size: 1.8rem !important;
            font-weight: 800 !important;
            white-space: pre-line !important;
            line-height: 1.4 !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Mostrar contenido según la vista activa
    active_view = st.session_state.active_task_view
    
    # ==================== VISTA: PENDIENTES A TIEMPO ====================
    if active_view == "pendientes":
        st.markdown("""
            <h2 style="color: #06d6a0; margin-bottom: 20px;">✅ Tareas Pendientes A Tiempo</h2>
        """, unsafe_allow_html=True)
        
        if pending_on_time:
            st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, rgba(6, 214, 160, 0.1), rgba(42, 157, 143, 0.1));
                    padding: 15px;
                    border-radius: 12px;
                    margin-bottom: 20px;
                    border-left: 4px solid #06d6a0;
                ">
                    <p style="margin: 0; color: #06d6a0; font-weight: 600; font-size: 1.1rem;">
                        ✅ Tienes {len(pending_on_time)} tarea{'s' if len(pending_on_time) != 1 else ''} pendiente{'s' if len(pending_on_time) != 1 else ''} a tiempo
                    </p>
                </div>
            """, unsafe_allow_html=True)
            
            for idx, assignment in enumerate(pending_on_time, 1):
                with st.container():
                    st.markdown(f"""
                        <div style="
                            background: linear-gradient(145deg, rgba(6, 214, 160, 0.05), rgba(42, 157, 143, 0.05));
                            border-left: 5px solid #06d6a0;
                            border-radius: 12px;
                            padding: 20px;
                            margin-bottom: 20px;
                            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
                        ">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; flex-wrap: wrap;">
                                <h3 style="color: #06d6a0; font-size: 1.5rem; margin: 0;">
                                    {idx}. 📌 {assignment['title']}
                                </h3>
                                <span style="
                                    background: #06d6a0;
                                    color: white;
                                    padding: 6px 16px;
                                    border-radius: 20px;
                                    font-size: 0.85rem;
                                    font-weight: 600;
                                ">✅ A TIEMPO</span>
                            </div>
                            <div style="color: #666; margin-bottom: 10px;">
                                📚 <strong>Curso:</strong> {assignment['course_code']}
                            </div>
                            <div style="color: #666; margin-bottom: 10px;">
                                📅 <strong>Fecha límite:</strong> {assignment['due_date']}
                            </div>
                            <div style="color: #666; margin-bottom: 10px;">
                                💯 <strong>Puntos:</strong> {assignment['max_score']}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    with st.expander("📤 Subir mi entrega", expanded=False):
                        if assignment.get('description'):
                            st.markdown(f"""
                                <div style="
                                    background: rgba(6, 214, 160, 0.1);
                                    padding: 15px;
                                    border-radius: 8px;
                                    border-left: 3px solid #06d6a0;
                                    margin-bottom: 15px;
                                ">
                                    <strong style="color: #06d6a0;">📝 Descripción:</strong>
                                    <p style="color: #666; margin-top: 8px;">{assignment['description']}</p>
                                </div>
                            """, unsafe_allow_html=True)
                        
                        uploaded_file = st.file_uploader(
                            "Selecciona tu archivo",
                            key=f"upload_ok_{assignment['id']}",
                            help="Formatos: PDF, DOCX, ZIP, etc."
                        )
                        
                        if uploaded_file:
                            col_info1, col_info2 = st.columns(2)
                            with col_info1:
                                st.success(f"📄 {uploaded_file.name}")
                            with col_info2:
                                size_mb = uploaded_file.size / (1024 * 1024)
                                st.info(f"💾 {size_mb:.2f} MB")
                            
                            if st.button(f"📤 Enviar Tarea", key=f"submit_ok_{assignment['id']}", type="primary", use_container_width=True):
                                with st.spinner("Subiendo..."):
                                    success, response = upload_submission(
                                        st.session_state.token,
                                        assignment['id'],
                                        uploaded_file
                                    )
                                    if success:
                                        st.session_state.flash_message = ("success", "✅ ¡Tarea enviada!")
                                        st.rerun()
                                    else:
                                        st.error(f"❌ {response.get('detail')}")
        else:
            st.markdown("""
                <div style="
                    text-align: center;
                    padding: 60px 20px;
                    background: linear-gradient(135deg, rgba(6, 214, 160, 0.1), rgba(42, 157, 143, 0.1));
                    border-radius: 16px;
                ">
                    <div style="font-size: 4rem; margin-bottom: 15px;">🎉</div>
                    <h3 style="color: #06d6a0; margin-bottom: 10px;">¡Excelente!</h3>
                    <p style="color: #666;">No tienes tareas pendientes a tiempo</p>
                </div>
            """, unsafe_allow_html=True)
    
    # ==================== VISTA: VENCIDAS ====================
    elif active_view == "vencidas":
        st.markdown("""
            <h2 style="color: #ef476f; margin-bottom: 20px;">⏰ Tareas Vencidas</h2>
        """, unsafe_allow_html=True)
        
        if pending_overdue:
            st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, rgba(239, 71, 111, 0.1), rgba(214, 40, 40, 0.1));
                    padding: 15px;
                    border-radius: 12px;
                    margin-bottom: 20px;
                    border-left: 4px solid #ef476f;
                ">
                    <p style="margin: 0; color: #ef476f; font-weight: 600; font-size: 1.1rem;">
                        ⚠️ Tienes {len(pending_overdue)} tarea{'s' if len(pending_overdue) != 1 else ''} vencida{'s' if len(pending_overdue) != 1 else ''}
                    </p>
                </div>
            """, unsafe_allow_html=True)
            
            for idx, assignment in enumerate(pending_overdue, 1):
                with st.container():
                    st.markdown(f"""
                        <div style="
                            background: linear-gradient(145deg, rgba(239, 71, 111, 0.05), rgba(214, 40, 40, 0.05));
                            border-left: 5px solid #ef476f;
                            border-radius: 12px;
                            padding: 20px;
                            margin-bottom: 20px;
                            box-shadow: 0 4px 12px rgba(239, 71, 111, 0.1);
                        ">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; flex-wrap: wrap;">
                                <h3 style="color: #ef476f; font-size: 1.5rem; margin: 0;">
                                    {idx}. ⏰ {assignment['title']}
                                </h3>
                                <span style="
                                    background: #ef476f;
                                    color: white;
                                    padding: 6px 16px;
                                    border-radius: 20px;
                                    font-size: 0.85rem;
                                    font-weight: 600;
                                ">⏰ VENCIDA</span>
                            </div>
                            <div style="color: #666; margin-bottom: 10px;">
                                📚 <strong>Curso:</strong> {assignment['course_code']}
                            </div>
                            <div style="color: #ef476f; margin-bottom: 10px; font-weight: 600;">
                                📅 <strong>Venció:</strong> {assignment['due_date']}
                            </div>
                            <div style="color: #666; margin-bottom: 10px;">
                                💯 <strong>Puntos:</strong> {assignment['max_score']}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    with st.expander("📤 Subir entrega tardía", expanded=False):
                        st.warning("⚠️ Esta tarea está vencida. Se marcará como entrega tardía.")
                        
                        if assignment.get('description'):
                            st.markdown(f"""
                                <div style="
                                    background: rgba(239, 71, 111, 0.1);
                                    padding: 15px;
                                    border-radius: 8px;
                                    border-left: 3px solid #ef476f;
                                    margin-bottom: 15px;
                                ">
                                    <strong style="color: #ef476f;">📝 Descripción:</strong>
                                    <p style="color: #666; margin-top: 8px;">{assignment['description']}</p>
                                </div>
                            """, unsafe_allow_html=True)
                        
                        uploaded_file = st.file_uploader(
                            "Selecciona tu archivo",
                            key=f"upload_late_{assignment['id']}",
                            help="Aún puedes enviar la tarea"
                        )
                        
                        if uploaded_file:
                            if st.button(f"📤 Enviar (Tardía)", key=f"submit_late_{assignment['id']}", type="primary", use_container_width=True):
                                with st.spinner("Subiendo..."):
                                    success, response = upload_submission(
                                        st.session_state.token,
                                        assignment['id'],
                                        uploaded_file
                                    )
                                    if success:
                                        st.session_state.flash_message = ("success", "✅ Tarea enviada")
                                        st.rerun()
                                    else:
                                        st.error(f"❌ {response.get('detail')}")
        else:
            st.markdown("""
                <div style="
                    text-align: center;
                    padding: 60px 20px;
                    background: linear-gradient(135deg, rgba(6, 214, 160, 0.1), rgba(42, 157, 143, 0.1));
                    border-radius: 16px;
                ">
                    <div style="font-size: 4rem; margin-bottom: 15px;">👍</div>
                    <h3 style="color: #06d6a0; margin-bottom: 10px;">¡Bien hecho!</h3>
                    <p style="color: #666;">No tienes tareas vencidas</p>
                </div>
            """, unsafe_allow_html=True)
    
    # ==================== VISTA: ENTREGADAS ====================
    elif active_view == "entregadas":
        st.markdown("""
            <h2 style="color: #48cae4; margin-bottom: 20px;">📤 Tareas Entregadas</h2>
        """, unsafe_allow_html=True)
        
        if submitted_list:
            st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, rgba(72, 202, 228, 0.1), rgba(0, 150, 199, 0.1));
                    padding: 15px;
                    border-radius: 12px;
                    margin-bottom: 20px;
                    border-left: 4px solid #48cae4;
                ">
                    <p style="margin: 0; color: #48cae4; font-weight: 600; font-size: 1.1rem;">
                        📤 Has entregado {len(submitted_list)} tarea{'s' if len(submitted_list) != 1 else ''}
                    </p>
                </div>
            """, unsafe_allow_html=True)
            
            for idx, assignment in enumerate(submitted_list, 1):
                submission = next((s for s in submissions if s['assignment_id'] == assignment['id']), None)
                
                if submission:
                    status_color = "#ef476f" if submission['late'] else "#06d6a0"
                    status_text = "⏰ TARDÍA" if submission['late'] else "✅ A TIEMPO"
                    
                    st.markdown(f"""
                        <div style="
                            background: linear-gradient(145deg, rgba(72, 202, 228, 0.05), rgba(0, 150, 199, 0.05));
                            border-left: 5px solid #48cae4;
                            border-radius: 12px;
                            padding: 20px;
                            margin-bottom: 20px;
                        ">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; flex-wrap: wrap;">
                                <h3 style="color: #48cae4; font-size: 1.4rem; margin: 0;">
                                    {idx}. ✅ {assignment['title']}
                                </h3>
                                <span style="
                                    background: {status_color};
                                    color: white;
                                    padding: 6px 16px;
                                    border-radius: 20px;
                                    font-size: 0.85rem;
                                    font-weight: 600;
                                    margin-top: 10px;
                                ">{status_text}</span>
                            </div>
                            <div style="color: #666; margin-bottom: 8px;">
                                📚 <strong>Curso:</strong> {assignment['course_code']}
                            </div>
                            <div style="color: #666; margin-bottom: 8px;">
                                📅 <strong>Entregada:</strong> {submission['submitted_at_date'][:16].replace('T', ' ')}
                            </div>
                    """, unsafe_allow_html=True)
                    
                    col_grade, col_feedback = st.columns([1, 2])
                    
                    with col_grade:
                        if submission['grade'] is not None:
                            percentage = (submission['grade'] / assignment['max_score'] * 100) if assignment['max_score'] > 0 else 0
                            
                            if percentage >= 90:
                                grade_color = "#06d6a0"
                            elif percentage >= 70:
                                grade_color = "#48cae4"
                            elif percentage >= 60:
                                grade_color = "#fca311"
                            else:
                                grade_color = "#ef476f"
                            
                            st.markdown(f"""
                                <div style="
                                    background: {grade_color}20;
                                    padding: 15px;
                                    border-radius: 12px;
                                    text-align: center;
                                    border: 2px solid {grade_color};
                                ">
                                    <div style="color: {grade_color}; font-size: 0.9rem; font-weight: 600;">CALIFICACIÓN</div>
                                    <div style="color: {grade_color}; font-size: 2rem; font-weight: 800; margin: 5px 0;">
                                        {submission['grade']}/{assignment['max_score']}
                                    </div>
                                    <div style="color: {grade_color}; font-size: 1rem; font-weight: 600;">
                                        {percentage:.1f}%
                                    </div>
                                </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.info("⏳ Pendiente de calificación")
                    
                    with col_feedback:
                        if submission['feedback_char']:
                            st.markdown(f"""
                                <div style="
                                    background: rgba(72, 202, 228, 0.1);
                                    padding: 15px;
                                    border-radius: 12px;
                                    border-left: 3px solid #48cae4;
                                ">
                                    <strong style="color: #48cae4;">💬 Comentarios:</strong>
                                    <p style="color: #666; margin-top: 8px; line-height: 1.5;">{submission['feedback_char']}</p>
                                </div>
                            """, unsafe_allow_html=True)
                    
                    st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.markdown("""
                <div style="
                    text-align: center;
                    padding: 60px 20px;
                    background: rgba(72, 202, 228, 0.1);
                    border-radius: 16px;
                ">
                    <div style="font-size: 4rem; margin-bottom: 15px;">📭</div>
                    <h3 style="color: #48cae4; margin-bottom: 10px;">Sin entregas</h3>
                    <p style="color: #666;">Aún no has entregado ninguna tarea</p>
                </div>
            """, unsafe_allow_html=True)
    
    # Botón de regreso
    st.markdown("<br><br>", unsafe_allow_html=True)
    col_center1, col_center2, col_center3 = st.columns([2, 2, 2])
    with col_center2:
        if st.button("🏠 Regresar al Dashboard", key="back_bottom", type="primary", use_container_width=True):
            st.session_state.student_menu_selection = "Dashboard"
            st.rerun()