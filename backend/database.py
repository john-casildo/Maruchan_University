from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool
import os
import time
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Obtener URL de base de datos desde .env
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://maruchan_user:maruchan_pass@localhost:5432/maruchan_db"
)

print(f"🔗 Conectando a: {DATABASE_URL.replace(DATABASE_URL.split(':')[2].split('@')[0], '****')}")

# Configuración del engine
# Para PostgreSQL en producción
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Verifica conexiones antes de usarlas
    pool_size=10,        # Número de conexiones en el pool
    max_overflow=20,     # Conexiones adicionales permitidas
    echo=False,          # Cambia a True para ver queries SQL en desarrollo
)

# Crear SessionLocal
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base para los modelos
Base = declarative_base()


# Dependency para obtener la sesión de DB
def get_db():
    """
    Generador que proporciona una sesión de base de datos.
    Se cierra automáticamente después de cada request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Función para inicializar la base de datos
def init_db():
    """
    Crea todas las tablas en la base de datos.
    Útil para desarrollo. En producción usa Alembic.
    """
    Base.metadata.create_all(bind=engine)
    print("✅ Base de datos inicializada")


# Función para verificar conexión con reintentos
def check_db_connection(max_retries=5, delay=2):
    """
    Verifica que la conexión a la base de datos funcione.
    Reintenta varias veces si falla (útil para Docker).
    """
    for attempt in range(max_retries):
        try:
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            print(f"✅ Conexión a base de datos exitosa")
            return True
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"⏳ Intento {attempt + 1}/{max_retries} - Esperando base de datos...")
                print(f"   Error: {str(e)[:100]}")
                time.sleep(delay)
            else:
                print(f"❌ Error conectando a la base de datos después de {max_retries} intentos:")
                print(f"   {e}")
                return False
    return False


# Función para esperar a que la BD esté lista (útil en Docker)
def wait_for_db(max_wait=30):
    """
    Espera a que la base de datos esté lista.
    Útil cuando se levanta con docker-compose.
    """
    print("⏳ Esperando a que la base de datos esté lista...")
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        if check_db_connection(max_retries=1):
            return True
        time.sleep(2)
    
    print(f"❌ La base de datos no estuvo lista en {max_wait} segundos")
    return False