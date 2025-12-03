import requests
import streamlit as st
import os

# URL de la API (Docker o Local)
API_URL = os.getenv("API_URL", "http://backend:8000")

def login_api(username, password):
    try:
        # ¡OJO! Usa data=... no json=...
        response = requests.post(
            f"{API_URL}/api/auth/login",
            data={"username": username, "password": password} 
        )
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"Error: {e}")
        return None

def get_data(endpoint, token):
    """Obtiene datos (GET)"""
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(f"{API_URL}{endpoint}", headers=headers)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def upload_file_api(assignment_id, file, token):
    """Sube un archivo de tarea (POST con Multipart)"""
    headers = {"Authorization": f"Bearer {token}"}
    
    # Preparamos el archivo para el envío
    files = {"file": (file.name, file, file.type)}
    
    try:
        # Enviamos al endpoint de entregas (submissions)
        # NOTA: Ajusta la URL al endpoint real de tu compañero
        response = requests.post(
            f"{API_URL}/api/submissions/upload/{assignment_id}", 
            headers=headers, 
            files=files
        )
        
        if response.status_code == 201:
            return True, response.json()
        return False, response.json().get('detail', 'Error desconocido')
    except Exception as e:
        return False, str(e)
    
# ... (código anterior) ...

def update_profile_api(token, user_id, data):
    """Actualiza datos del usuario"""
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.put(f"{API_URL}/api/users/{user_id}", headers=headers, json=data)
        if response.status_code == 200:
            return True, response.json()
        return False, response.json()
    except Exception as e:
        return False, {"detail": str(e)}

def get_materials_api(token, course_id=None):
    """Obtiene materiales de clase"""
    headers = {"Authorization": f"Bearer {token}"}
    params = {"course_id": course_id} if course_id else {}
    try:
        response = requests.get(f"{API_URL}/api/materials/", headers=headers, params=params)
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []