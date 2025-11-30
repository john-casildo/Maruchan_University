#!/bin/bash
set -e

echo "🎓 Maruchan University - Inicializando base de datos..."

# El script se ejecuta automáticamente cuando se crea el contenedor
# PostgreSQL ya crea la base de datos especificada en POSTGRES_DB

echo "✅ Base de datos lista"
echo "📊 Database: $POSTGRES_DB"
echo "👤 User: $POSTGRES_USER"