import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
from models import User
from dependencies import get_password_hash

def reset_password():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == "admin").first()
        if user:
            print(f"👤 Usuario encontrado: {user.username}")
            new_hash = get_password_hash("admin123")
            user.hashed_password = new_hash
            db.commit()
            print("✅ Contraseña restablecida a: admin123")
        else:
            print("❌ Usuario admin no encontrado")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    reset_password()
