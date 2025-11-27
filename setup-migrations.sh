#!/bin/bash

# Script para configurar Alembic en el proyecto Maruchan University

echo "🎓 Configurando migraciones para Maruchan University..."

# 1. Entrar al contenedor del backend
echo "📦 Accediendo al contenedor backend..."

# 2. Inicializar Alembic (solo la primera vez)
docker-compose exec backend alembic init alembic

echo "✅ Alembic inicializado"

# 3. Crear la primera migración
echo "📝 Creando migración inicial..."
docker-compose exec backend alembic revision --autogenerate -m "Initial migration: students, professors, courses, enrollments"

# 4. Aplicar la migración
echo "🚀 Aplicando migración a la base de datos..."
docker-compose exec backend alembic upgrade head

echo "✨ ¡Migraciones configuradas exitosamente!"
echo ""
echo "Comandos útiles:"
echo "  - Crear nueva migración: docker-compose exec backend alembic revision --autogenerate -m 'descripcion'"
echo "  - Aplicar migraciones: docker-compose exec backend alembic upgrade head"
echo "  - Ver historial: docker-compose exec backend alembic history"
echo "  - Revertir última: docker-compose exec backend alembic downgrade -1"