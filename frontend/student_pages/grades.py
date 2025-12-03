import streamlit as st
import pandas as pd
import requests
import os

API_URL = os.getenv("API_URL", "http://localhost:8000")

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
    """Vista premium de calificaciones del estudiante"""
    
    # Botón de regreso
    col_back, col_spacer = st.columns([1, 5])
    with col_back:
        if st.button("⬅️ Volver al Inicio", key="back_to_dashboard", type="secondary", use_container_width=True):
            st.session_state.student_menu_selection = "Dashboard"
            st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Header con diseño mejorado
    st.markdown("""
        <div style="
            background: linear-gradient(135deg, #9d4edd 0%, #7209b7 100%);
            padding: 40px;
            border-radius: 20px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(157, 78, 221, 0.3);
        ">
            <h1 style="
                color: white;
                font-size: 3rem;
                font-weight: 800;
                margin: 0;
                text-align: center;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
            ">📊 Mis Calificaciones</h1>
        </div>
    """, unsafe_allow_html=True)
    
    submissions = get_my_submissions(st.session_state.token)
    graded = [s for s in submissions if s['grade'] is not None]
    
    if graded:
        # Calcular estadísticas generales
        total_points = sum(s['grade'] for s in graded)
        max_points = sum(s['assignment']['max_score'] for s in graded)
        overall_average = (total_points / max_points * 100) if max_points > 0 else 0
        
        # Determinar color del promedio general
        if overall_average >= 90:
            avg_color = "#06d6a0"
            avg_emoji = "🌟"
            avg_message = "¡Sobresaliente!"
        elif overall_average >= 80:
            avg_color = "#48cae4"
            avg_emoji = "🎉"
            avg_message = "¡Muy bien!"
        elif overall_average >= 70:
            avg_color = "#fca311"
            avg_emoji = "👍"
            avg_message = "¡Buen trabajo!"
        elif overall_average >= 60:
            avg_color = "#f77f00"
            avg_emoji = "📈"
            avg_message = "Sigue mejorando"
        else:
            avg_color = "#ef476f"
            avg_emoji = "💪"
            avg_message = "¡Tú puedes!"
        
        # Tarjeta de promedio general DESTACADA
        st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, {avg_color}, {avg_color}dd);
                padding: 40px;
                border-radius: 20px;
                text-align: center;
                color: white;
                box-shadow: 0 12px 30px {avg_color}40;
                margin-bottom: 30px;
                position: relative;
                overflow: hidden;
            ">
                <div style="font-size: 4rem; margin-bottom: 10px;">{avg_emoji}</div>
                <div style="font-size: 1.2rem; opacity: 0.95; margin-bottom: 15px; font-weight: 500;">
                    Tu Promedio General
                </div>
                <div style="font-size: 4.5rem; font-weight: 900; margin-bottom: 10px; text-shadow: 3px 3px 6px rgba(0,0,0,0.2);">
                    {overall_average:.1f}%
                </div>
                <div style="font-size: 1.5rem; font-weight: 600; opacity: 0.95;">
                    {avg_message}
                </div>
                <div style="font-size: 1rem; opacity: 0.85; margin-top: 15px;">
                    {total_points:.1f} / {max_points:.1f} puntos totales
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Estadísticas rápidas
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #06d6a0, #2a9d8f);
                    padding: 25px;
                    border-radius: 16px;
                    text-align: center;
                    color: white;
                    box-shadow: 0 6px 15px rgba(6, 214, 160, 0.3);
                ">
                    <div style="font-size: 2.5rem;">📚</div>
                    <div style="font-size: 0.9rem; opacity: 0.95; margin: 8px 0;">Tareas Calificadas</div>
                    <div style="font-size: 2.2rem; font-weight: 800;">{len(graded)}</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            highest = max(graded, key=lambda s: (s['grade'] / s['assignment']['max_score']) if s['assignment']['max_score'] > 0 else 0)
            highest_percent = (highest['grade'] / highest['assignment']['max_score'] * 100) if highest['assignment']['max_score'] > 0 else 0
            
            st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #ffd166, #f77f00);
                    padding: 25px;
                    border-radius: 16px;
                    text-align: center;
                    color: white;
                    box-shadow: 0 6px 15px rgba(255, 209, 102, 0.3);
                ">
                    <div style="font-size: 2.5rem;">🏆</div>
                    <div style="font-size: 0.9rem; opacity: 0.95; margin: 8px 0;">Nota Más Alta</div>
                    <div style="font-size: 2.2rem; font-weight: 800;">{highest_percent:.1f}%</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col3:
            lowest = min(graded, key=lambda s: (s['grade'] / s['assignment']['max_score']) if s['assignment']['max_score'] > 0 else 0)
            lowest_percent = (lowest['grade'] / lowest['assignment']['max_score'] * 100) if lowest['assignment']['max_score'] > 0 else 0
            
            st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #48cae4, #0096c7);
                    padding: 25px;
                    border-radius: 16px;
                    text-align: center;
                    color: white;
                    box-shadow: 0 6px 15px rgba(72, 202, 228, 0.3);
                ">
                    <div style="font-size: 2.5rem;">📉</div>
                    <div style="font-size: 0.9rem; opacity: 0.95; margin: 8px 0;">Nota Más Baja</div>
                    <div style="font-size: 2.2rem; font-weight: 800;">{lowest_percent:.1f}%</div>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        # Agrupar por curso
        courses_dict = {}
        for submission in graded:
            course_code = submission['assignment']['course_code']
            if course_code not in courses_dict:
                courses_dict[course_code] = []
            courses_dict[course_code].append(submission)
        
        # Colores para cada curso
        course_colors = [
            ("#9d4edd", "#7209b7"),
            ("#06d6a0", "#2a9d8f"),
            ("#48cae4", "#0096c7"),
            ("#f77f00", "#fca311"),
            ("#ef476f", "#d62828"),
            ("#2a9d8f", "#48cae4")
        ]
        
        # Mostrar por curso
        for idx, (course_code, course_submissions) in enumerate(courses_dict.items()):
            color1, color2 = course_colors[idx % len(course_colors)]
            
            # Calcular promedio del curso
            course_total = sum(s['grade'] for s in course_submissions)
            course_max = sum(s['assignment']['max_score'] for s in course_submissions)
            course_average = (course_total / course_max * 100) if course_max > 0 else 0
            
            # Color según promedio
            if course_average >= 90:
                status_color = "#06d6a0"
                status_icon = "🌟"
            elif course_average >= 80:
                status_color = "#48cae4"
                status_icon = "⭐"
            elif course_average >= 70:
                status_color = "#fca311"
                status_icon = "📊"
            else:
                status_color = "#ef476f"
                status_icon = "📈"
            
            # Tarjeta del curso
            st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, {color1}15, {color2}10);
                    border-left: 6px solid {color1};
                    border-radius: 16px;
                    padding: 0;
                    margin-bottom: 30px;
                    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08);
                    overflow: hidden;
                ">
                    <!-- Header del curso -->
                    <div style="
                        background: linear-gradient(135deg, {color1}, {color2});
                        padding: 25px;
                        color: white;
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                        flex-wrap: wrap;
                    ">
                        <div>
                            <div style="font-size: 2rem; font-weight: 800; margin-bottom: 5px;">
                                📚 {course_code}
                            </div>
                            <div style="font-size: 1rem; opacity: 0.95;">
                                {len(course_submissions)} tarea{'s' if len(course_submissions) != 1 else ''} calificada{'s' if len(course_submissions) != 1 else ''}
                            </div>
                        </div>
                        <div style="text-align: right; margin-top: 10px;">
                            <div style="font-size: 3rem; font-weight: 900;">
                                {course_average:.1f}%
                            </div>
                            <div style="font-size: 0.9rem; opacity: 0.9;">
                                Promedio del curso
                            </div>
                        </div>
                    </div>
            """, unsafe_allow_html=True)
            
            # Métricas del curso
            with st.container():
                col_a, col_b, col_c = st.columns(3)
                
                with col_a:
                    st.markdown(f"""
                        <div style="text-align: center; padding: 20px;">
                            <div style="font-size: 2rem; color: {color1};">{status_icon}</div>
                            <div style="font-size: 0.85rem; color: #888; margin-top: 8px;">Estado</div>
                            <div style="font-size: 1.3rem; font-weight: 700; color: {status_color}; margin-top: 5px;">
                                {'Excelente' if course_average >= 90 else 'Muy Bien' if course_average >= 80 else 'Bien' if course_average >= 70 else 'Regular'}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                
                with col_b:
                    st.markdown(f"""
                        <div style="text-align: center; padding: 20px;">
                            <div style="font-size: 2rem; color: {color1};">💯</div>
                            <div style="font-size: 0.85rem; color: #888; margin-top: 8px;">Puntos</div>
                            <div style="font-size: 1.3rem; font-weight: 700; color: {color1}; margin-top: 5px;">
                                {course_total:.1f} / {course_max:.1f}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                
                with col_c:
                    # Barra de progreso visual
                    progress_width = min(course_average, 100)
                    st.markdown(f"""
                        <div style="text-align: center; padding: 20px;">
                            <div style="font-size: 2rem; color: {color1};">📊</div>
                            <div style="font-size: 0.85rem; color: #888; margin-top: 8px;">Progreso</div>
                            <div style="
                                background: #e0e0e0;
                                border-radius: 10px;
                                height: 12px;
                                margin-top: 10px;
                                overflow: hidden;
                            ">
                                <div style="
                                    background: linear-gradient(90deg, {color1}, {color2});
                                    width: {progress_width}%;
                                    height: 100%;
                                    border-radius: 10px;
                                    transition: width 0.3s ease;
                                "></div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
            
            # Tabla de calificaciones detallada
            with st.expander(f"📋 Ver todas las calificaciones de {course_code}", expanded=False):
                for sub_idx, s in enumerate(course_submissions, 1):
                    percentage = (s['grade'] / s['assignment']['max_score'] * 100) if s['assignment']['max_score'] > 0 else 0
                    
                    # Color según la nota
                    if percentage >= 90:
                        grade_color = "#06d6a0"
                        grade_icon = "🌟"
                    elif percentage >= 80:
                        grade_color = "#48cae4"
                        grade_icon = "⭐"
                    elif percentage >= 70:
                        grade_color = "#fca311"
                        grade_icon = "⚠️"
                    else:
                        grade_color = "#ef476f"
                        grade_icon = "📉"
                    
                    st.markdown(f"""
                        <div style="
                            background: {grade_color}10;
                            border-left: 4px solid {grade_color};
                            padding: 15px;
                            border-radius: 10px;
                            margin-bottom: 12px;
                        ">
                            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                                <div style="flex: 1; min-width: 200px;">
                                    <div style="font-size: 1.1rem; font-weight: 700; color: #1a1a2e; margin-bottom: 5px;">
                                        {sub_idx}. {s['assignment']['title']}
                                    </div>
                                    <div style="font-size: 0.85rem; color: #666;">
                                        📅 {s['submitted_at_date'][:10]}
                                    </div>
                                </div>
                                <div style="text-align: right; min-width: 150px; margin-top: 10px;">
                                    <div style="
                                        background: {grade_color};
                                        color: white;
                                        padding: 8px 20px;
                                        border-radius: 20px;
                                        display: inline-block;
                                        font-weight: 700;
                                        font-size: 1.1rem;
                                    ">
                                        {grade_icon} {s['grade']:.1f} / {s['assignment']['max_score']:.1f}
                                    </div>
                                    <div style="color: {grade_color}; font-weight: 700; font-size: 1.2rem; margin-top: 5px;">
                                        {percentage:.1f}%
                                    </div>
                                </div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    if s['feedback_char']:
                        st.markdown(f"""
                            <div style="
                                background: rgba(72, 202, 228, 0.1);
                                padding: 12px;
                                border-radius: 8px;
                                border-left: 3px solid #48cae4;
                                margin: 10px 0 15px 20px;
                            ">
                                <strong style="color: #48cae4; font-size: 0.9rem;">💬 Comentarios del profesor:</strong>
                                <p style="color: #666; margin: 5px 0 0 0; font-size: 0.95rem; line-height: 1.5;">
                                    {s['feedback_char']}
                                </p>
                            </div>
                        """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
    
    else:
        # Sin calificaciones
        st.markdown("""
            <div style="
                text-align: center;
                padding: 80px 20px;
                background: linear-gradient(135deg, rgba(157, 78, 221, 0.1), rgba(114, 9, 183, 0.1));
                border-radius: 20px;
                margin-top: 30px;
            ">
                <div style="font-size: 6rem; margin-bottom: 20px;">📊</div>
                <h2 style="color: #9d4edd; font-size: 2.5rem; margin-bottom: 15px;">
                    Aún no tienes calificaciones
                </h2>
                <p style="color: #666; font-size: 1.2rem; margin-bottom: 30px;">
                    Tus notas aparecerán aquí una vez que los profesores califiquen tus entregas
                </p>
                <div style="
                    background: rgba(157, 78, 221, 0.1);
                    padding: 20px;
                    border-radius: 12px;
                    max-width: 500px;
                    margin: 0 auto;
                    border-left: 4px solid #9d4edd;
                ">
                    <p style="color: #666; margin: 0; line-height: 1.6;">
                        💡 <strong>Consejo:</strong> Asegúrate de entregar tus tareas a tiempo para recibir calificaciones
                    </p>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    # Botón de regreso
    st.markdown("<br><br>", unsafe_allow_html=True)
    col_center1, col_center2, col_center3 = st.columns([2, 2, 2])
    with col_center2:
        if st.button("🏠 Regresar al Dashboard", key="back_bottom", type="primary", use_container_width=True):
            st.session_state.student_menu_selection = "Dashboard"
            st.rerun()