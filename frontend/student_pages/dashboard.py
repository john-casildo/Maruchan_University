import streamlit as st
import requests
import os
from datetime import datetime

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

def show():
    """Dashboard principal mejorado del estudiante"""
    
    # Header con diseño mejorado
    st.markdown("""
        <div style="
            background: linear-gradient(135deg, #2a9d8f 0%, #48cae4 100%);
            padding: 40px;
            border-radius: 20px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(42, 157, 143, 0.3);
        ">
            <h1 style="
                color: white;
                font-size: 3rem;
                font-weight: 800;
                margin: 0;
                text-align: center;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
            ">📚 Mi Panel Estudiantil</h1>
        </div>
    """, unsafe_allow_html=True)
    
    user = st.session_state.user
    
    # Saludo personalizado con hora
    current_hour = datetime.now().hour
    if current_hour < 12:
        greeting = "Buenos días"
        emoji = "🌅"
    elif current_hour < 18:
        greeting = "Buenas tardes"
        emoji = "☀️"
    else:
        greeting = "Buenas noches"
        emoji = "🌙"
    
    st.markdown(f"""
        <div style="
            text-align: center;
            font-size: 1.8rem;
            font-weight: 600;
            color: #2a9d8f;
            margin-bottom: 30px;
        ">
            {emoji} {greeting}, {user.get('first_name')}!
        </div>
    """, unsafe_allow_html=True)
    
    # Obtener datos
    courses = get_my_courses(st.session_state.token)
    assignments = get_assignments(st.session_state.token)
    submissions = get_my_submissions(st.session_state.token)
    
    pending = len([a for a in assignments if a['id'] not in [s['assignment_id'] for s in submissions]])
    graded = len([s for s in submissions if s['grade'] is not None])
    
    # Métricas INTERACTIVAS con botones
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #2a9d8f, #48cae4);
                padding: 30px 20px;
                border-radius: 20px;
                text-align: center;
                color: white;
                box-shadow: 0 8px 20px rgba(0,0,0,0.15);
                margin-bottom: 10px;
            ">
                <div style="font-size: 3rem; margin-bottom: 10px;">📖</div>
                <div style="font-size: 0.9rem; opacity: 0.95; margin-bottom: 8px; font-weight: 500;">Cursos Inscritos</div>
                <div style="font-size: 2.5rem; font-weight: 800;">{len(courses)}</div>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("📚 Ver Mis Cursos", key="btn_courses", use_container_width=True, type="primary"):
            st.session_state.student_menu_selection = "Mis Cursos"
            st.rerun()
    
    with col2:
        st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #f77f00, #fca311);
                padding: 30px 20px;
                border-radius: 20px;
                text-align: center;
                color: white;
                box-shadow: 0 8px 20px rgba(0,0,0,0.15);
                margin-bottom: 10px;
            ">
                <div style="font-size: 3rem; margin-bottom: 10px;">📝</div>
                <div style="font-size: 0.9rem; opacity: 0.95; margin-bottom: 8px; font-weight: 500;">Tareas Pendientes</div>
                <div style="font-size: 2.5rem; font-weight: 800;">{pending}</div>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("📋 Ver Tareas", key="btn_tasks", use_container_width=True, type="primary"):
            st.session_state.student_menu_selection = "Tareas"
            st.rerun()
    
    with col3:
        st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #06d6a0, #2a9d8f);
                padding: 30px 20px;
                border-radius: 20px;
                text-align: center;
                color: white;
                box-shadow: 0 8px 20px rgba(0,0,0,0.15);
                margin-bottom: 10px;
            ">
                <div style="font-size: 3rem; margin-bottom: 10px;">✅</div>
                <div style="font-size: 0.9rem; opacity: 0.95; margin-bottom: 8px; font-weight: 500;">Entregas Realizadas</div>
                <div style="font-size: 2.5rem; font-weight: 800;">{len(submissions)}</div>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("📤 Ver Entregas", key="btn_submissions", use_container_width=True, type="primary"):
            st.session_state.student_menu_selection = "Tareas"
            st.rerun()
    
    with col4:
        st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #48cae4, #0096c7);
                padding: 30px 20px;
                border-radius: 20px;
                text-align: center;
                color: white;
                box-shadow: 0 8px 20px rgba(0,0,0,0.15);
                margin-bottom: 10px;
            ">
                <div style="font-size: 3rem; margin-bottom: 10px;">📊</div>
                <div style="font-size: 0.9rem; opacity: 0.95; margin-bottom: 8px; font-weight: 500;">Tareas Calificadas</div>
                <div style="font-size: 2.5rem; font-weight: 800;">{graded}</div>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("📈 Ver Calificaciones", key="btn_grades", use_container_width=True, type="primary"):
            st.session_state.student_menu_selection = "Calificaciones"
            st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Sección de progreso
    if len(submissions) > 0 and graded > 0:
        progress_percent = (graded / len(submissions)) * 100
        
        st.markdown("""
            <div style="
                background: linear-gradient(135deg, rgba(42, 157, 143, 0.1), rgba(72, 202, 228, 0.1));
                padding: 25px;
                border-radius: 16px;
                border-left: 5px solid #2a9d8f;
                margin-bottom: 25px;
            ">
                <h3 style="color: #2a9d8f; margin-bottom: 15px;">📈 Tu Progreso Académico</h3>
        """, unsafe_allow_html=True)
        
        st.progress(progress_percent / 100)
        st.markdown(f"""
                <p style="text-align: center; font-size: 1.2rem; color: #2a9d8f; font-weight: 600; margin-top: 10px;">
                    {progress_percent:.1f}% de tus tareas han sido calificadas
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    # Próximas entregas con diseño mejorado
    st.markdown("""
        <div style="
            background: linear-gradient(135deg, rgba(247, 127, 0, 0.1), rgba(252, 163, 17, 0.1));
            padding: 25px;
            border-radius: 16px;
            border-left: 5px solid #f77f00;
            margin-top: 30px;
        ">
            <h2 style="color: #f77f00; margin-bottom: 20px;">⏰ Próximas Entregas</h2>
    """, unsafe_allow_html=True)
    
    if assignments:
        pending_assignments = [a for a in assignments if a['id'] not in [s['assignment_id'] for s in submissions]]
        
        if pending_assignments:
            # Ordenar por fecha
            pending_assignments.sort(key=lambda x: x['due_date'])
            
            for idx, assignment in enumerate(pending_assignments[:5], 1):
                is_overdue = assignment.get('is_overdue', False)
                
                # Color según estado
                if is_overdue:
                    border_color = "#ef476f"
                    bg_color = "rgba(239, 71, 111, 0.05)"
                    status_badge = '<span style="background: #ef476f; color: white; padding: 4px 12px; border-radius: 12px; font-size: 0.8rem; font-weight: 600;">⏰ VENCIDA</span>'
                else:
                    border_color = "#06d6a0"
                    bg_color = "rgba(6, 214, 160, 0.05)"
                    status_badge = '<span style="background: #06d6a0; color: white; padding: 4px 12px; border-radius: 12px; font-size: 0.8rem; font-weight: 600;">✅ A TIEMPO</span>'
                
                st.markdown(f"""
                    <div style="
                        background: {bg_color};
                        border-left: 4px solid {border_color};
                        padding: 20px;
                        border-radius: 12px;
                        margin-bottom: 15px;
                        transition: all 0.3s ease;
                    ">
                        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                            <div style="flex: 1; min-width: 300px;">
                                <div style="font-size: 1.3rem; font-weight: 700; color: #1a1a2e; margin-bottom: 8px;">
                                    {idx}. 📌 {assignment['title']}
                                </div>
                                <div style="color: #666; margin-bottom: 8px;">
                                    📚 <strong>Curso:</strong> {assignment['course_code']} | 
                                    📅 <strong>Entrega:</strong> {assignment['due_date']}
                                </div>
                                <div style="color: #888; font-size: 0.9rem;">
                                    💯 <strong>Puntos:</strong> {assignment['max_score']}
                                </div>
                            </div>
                            <div style="margin-left: 20px; margin-top: 10px;">
                                {status_badge}
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            
            if len(pending_assignments) > 5:
                st.info(f"📋 Tienes {len(pending_assignments) - 5} tareas más pendientes.")
                if st.button("➡️ Ver todas las tareas", key="btn_all_tasks"):
                    st.session_state.student_menu_selection = "Tareas"
                    st.rerun()
        else:
            st.markdown("""
                <div style="
                    text-align: center;
                    padding: 40px;
                    background: linear-gradient(135deg, rgba(6, 214, 160, 0.1), rgba(42, 157, 143, 0.1));
                    border-radius: 16px;
                ">
                    <div style="font-size: 4rem; margin-bottom: 15px;">🎉</div>
                    <div style="font-size: 1.5rem; font-weight: 700; color: #06d6a0; margin-bottom: 10px;">
                        ¡Excelente trabajo!
                    </div>
                    <div style="font-size: 1.1rem; color: #666;">
                        No tienes tareas pendientes
                    </div>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div style="
                text-align: center;
                padding: 40px;
                background: rgba(72, 202, 228, 0.1);
                border-radius: 16px;
            ">
                <div style="font-size: 3rem; margin-bottom: 15px;">📭</div>
                <div style="font-size: 1.2rem; color: #48cae4;">
                    Aún no hay tareas asignadas
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Sección de resumen rápido
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown("""
            <div style="
                background: linear-gradient(135deg, rgba(72, 202, 228, 0.1), rgba(0, 150, 199, 0.1));
                padding: 25px;
                border-radius: 16px;
                border-left: 5px solid #48cae4;
            ">
                <h3 style="color: #48cae4; margin-bottom: 15px;">💡 Consejo del día</h3>
                <p style="color: #666; line-height: 1.6;">
                    Organiza tu tiempo: Dedica bloques específicos para cada materia y toma descansos regulares para mantener tu productividad.
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    with col_b:
        st.markdown("""
            <div style="
                background: linear-gradient(135deg, rgba(42, 157, 143, 0.1), rgba(6, 214, 160, 0.1));
                padding: 25px;
                border-radius: 16px;
                border-left: 5px solid #2a9d8f;
            ">
                <h3 style="color: #2a9d8f; margin-bottom: 15px;">🎯 Objetivos</h3>
                <p style="color: #666; line-height: 1.6;">
                    Mantén un promedio alto entregando tus tareas a tiempo y participando activamente en clase.
                </p>
            </div>
        """, unsafe_allow_html=True)