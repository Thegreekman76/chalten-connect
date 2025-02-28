#!/bin/bash
set -e

# Esperar a que PostgreSQL esté listo
echo "Esperando a que PostgreSQL esté listo..."
until PGPASSWORD=$POSTGRES_PASSWORD psql -h "$POSTGRES_SERVER" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\q'; do
  echo "PostgreSQL no está disponible todavía - esperando..."
  sleep 3
done

echo "PostgreSQL listo, configurando el entorno Python..."

# Asegurarse de que Python puede encontrar los módulos
export PYTHONPATH=$PYTHONPATH:/app

echo "Creando tablas directamente con SQLAlchemy..."
# Usar Python para crear tablas directamente desde los modelos
python -c "
from app.db.base import Base
from app.db.session import engine
Base.metadata.create_all(bind=engine)
print('Tablas creadas correctamente con SQLAlchemy')
"

echo "Configuración completada, iniciando aplicación..."

# Iniciar la aplicación
exec "$@"