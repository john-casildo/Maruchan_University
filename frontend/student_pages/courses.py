import streamlit as st
import requests
import os

API_URL = os.getenv("API_URL", "http://localhost:8000")

def get_my_courses(token):
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{API_URL}/api/courses/my-courses", headers=headers)
        return response.json() if response.status_code == 200 else []
    except: 
        return []

def show():
    """Vista mejorada de cursos del estudiante"""
    
    # Botón de regreso al inicio
    col_back, col_spacer = st.columns([1, 5])
    with col_back:
        if st.button("⬅️ Volver al Inicio", key="back_to_dashboard", type="secondary", use_container_width=True):
            st.session_state.student_menu_selection = "Dashboard"
            st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Header con diseño mejorado
    st.markdown("""
        <div style="
            background: linear-gradient(135deg, #48cae4 0%, #0096c7 100%);
            padding: 40px;
            border-radius: 20px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(72, 202, 228, 0.3);
        ">
            <h1 style="
                color: white;
                font-size: 3rem;
                font-weight: 800;
                margin: 0;
                text-align: center;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
            ">📚 Mis Cursos</h1>
        </div>
    """, unsafe_allow_html=True)
    
    courses = get_my_courses(st.session_state.token)
    
    if courses:
        # Resumen de cursos
        st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, rgba(72, 202, 228, 0.1), rgba(0, 150, 199, 0.1));
                padding: 20px;
                border-radius: 16px;
                text-align: center;
                margin-bottom: 30px;
                border: 2px solid rgba(72, 202, 228, 0.3);
            ">
                <h2 style="color: #48cae4; font-size: 1.5rem; margin: 0;">
                    📖 Estás inscrito en <strong>{len(courses)}</strong> curso{'s' if len(courses) != 1 else ''}
                </h2>
            </div>
        """, unsafe_allow_html=True)
        
        # Colores para cada curso
        colors = [
            ("#2a9d8f", "#48cae4"),
            ("#06d6a0", "#2a9d8f"),
            ("#f77f00", "#fca311"),
            ("#48cae4", "#0096c7"),
            ("#ef476f", "#d62828"),
            ("#9d4edd", "#7209b7")
        ]
        
        for idx, course in enumerate(courses):
            color1, color2 = colors[idx % len(colors)]
            
            # Tarjeta de curso con diseño premium
            st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, {color1}15, {color2}10);
                    border-left: 6px solid {color1};
                    border-radius: 16px;
                    padding: 0;
                    margin-bottom: 25px;
                    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08);
                    overflow: hidden;
                    transition: all 0.3s ease;
                ">
                    <!-- Header del curso -->
                    <div style="
                        background: linear-gradient(135deg, {color1}, {color2});
                        padding: 25px;
                        color: white;
                    ">
                        <div style="font-size: 1.8rem; font-weight: 800; margin-bottom: 8px;">
                            🎓 {course['code']} - {course['title']}
                        </div>
                        <div style="font-size: 1.1rem; opacity: 0.95;">
                            👨‍🏫 Profesor: {course['teacher_name']}
                        </div>
                    </div>
            """, unsafe_allow_html=True)
            
            # Detalles del curso
            with st.container():
                # Info general
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown(f"""
                        <div style="text-align: center; padding: 15px;">
                            <div style="font-size: 2rem; color: {color1};">💳</div>
                            <div style="font-size: 0.9rem; color: #888; margin-top: 5px;">Créditos</div>
                            <div style="font-size: 1.8rem; font-weight: 700; color: {color1};">
                                {course['credits']}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                        <div style="text-align: center; padding: 15px;">
                            <div style="font-size: 2rem; color: {color1};">📆</div>
                            <div style="font-size: 0.9rem; color: #888; margin-top: 5px;">Semestre</div>
                            <div style="font-size: 1.8rem; font-weight: 700; color: {color1};">
                                {course['semester']}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f"""
                        <div style="text-align: center; padding: 15px;">
                            <div style="font-size: 2rem; color: {color1};">👥</div>
                            <div style="font-size: 0.9rem; color: #888; margin-top: 5px;">Estudiantes</div>
                            <div style="font-size: 1.8rem; font-weight: 700; color: {color1};">
                                {course['enrolled_count']}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("<hr style='margin: 5px 20px; border: none; height: 1px; background: #ddd;'>", unsafe_allow_html=True)
                
                # Información adicional
                with st.expander("📋 Ver más detalles", expanded=False):
                    st.markdown(f"""
                        <div style="padding: 15px;">
                            <div style="margin-bottom: 15px;">
                                <strong style="color: {color1};">🕐 Horario:</strong>
                                <span style="color: #666; margin-left: 10px;">{course.get('schedule', 'No especificado')}</span>
                            </div>
                            <div style="margin-bottom: 15px;">
                                <strong style="color: {color1};">🚪 Aula:</strong>
                                <span style="color: #666; margin-left: 10px;">{course.get('classroom', 'N/A')}</span>
                            </div>
                            <div style="margin-bottom: 15px;">
                                <strong style="color: {color1};">📅 Inicio:</strong>
                                <span style="color: #666; margin-left: 10px;">{course.get('start_date', 'N/A')[:10] if course.get('start_date') else 'N/A'}</span>
                            </div>
                            <div style="margin-bottom: 15px;">
                                <strong style="color: {color1};">🏁 Fin:</strong>
                                <span style="color: #666; margin-left: 10px;">{course.get('end_date', 'N/A')[:10] if course.get('end_date') else 'N/A'}</span>
                            </div>
                    """, unsafe_allow_html=True)
                    
                    if course.get('description'):
                        st.markdown(f"""
                            <div style="
                                background: {color1}10;
                                padding: 15px;
                                border-radius: 10px;
                                margin-top: 15px;
                                border-left: 4px solid {color1};
                            ">
                                <strong style="color: {color1};">📝 Descripción:</strong>
                                <p style="color: #666; margin-top: 10px; line-height: 1.6;">
                                    {course['description']}
                                </p>
                            </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown("</div>", unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Botón adicional al final para volver
        st.markdown("<br><br>", unsafe_allow_html=True)
        col_center1, col_center2, col_center3 = st.columns([2, 2, 2])
        with col_center2:
            if st.button("🏠 Regresar al Dashboard", key="back_to_dashboard_bottom", type="primary", use_container_width=True):
                st.session_state.student_menu_selection = "Dashboard"
                st.rerun()
    else:
        # Mensaje cuando no hay cursos
        st.markdown("""
            <div style="
                text-align: center;
                padding: 60px 20px;
                background: linear-gradient(135deg, rgba(72, 202, 228, 0.1), rgba(0, 150, 199, 0.1));
                border-radius: 20px;
                margin-top: 30px;
            ">
                <div style="font-size: 5rem; margin-bottom: 20px;">📚</div>
                <h2 style="color: #48cae4; font-size: 2rem; margin-bottom: 15px;">
                    Aún no estás inscrito en ningún curso
                </h2>
                <p style="color: #666; font-size: 1.1rem;">
                    Contacta a tu coordinador académico para inscribirte en tus materias
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        col_center1, col_center2, col_center3 = st.columns([2, 2, 2])
        with col_center2:
            if st.button("🏠 Regresar al Dashboard", key="back_no_courses", type="primary", use_container_width=True):
                st.session_state.student_menu_selection = "Dashboard"
                st.rerun()