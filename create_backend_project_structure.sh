#!/bin/bash

# Crear directorio principal del proyecto
mkdir -p backend
cd backend

# Crear archivo README.md
cat > README.md << EOF
# El Chaltén Connect - Backend

Plataforma integral para turismo en El Chaltén que conecta visitantes con servicios locales mientras 
ofrece funcionalidades especializadas para áreas remotas de montaña.
EOF

# Crear estructura para el API Gateway
mkdir -p api-gateway/app/routers
mkdir -p api-gateway/app/core
mkdir -p api-gateway/app/middlewares
mkdir -p api-gateway/app/tests
touch api-gateway/Dockerfile
touch api-gateway/requirements.txt
touch api-gateway/app/__init__.py
touch api-gateway/app/main.py
touch api-gateway/app/core/__init__.py
touch api-gateway/app/core/config.py
touch api-gateway/app/core/security.py
touch api-gateway/app/middlewares/__init__.py
touch api-gateway/app/middlewares/cors.py
touch api-gateway/app/middlewares/logging.py
touch api-gateway/app/routers/__init__.py

# Crear estructura para los microservicios
declare -a microservices=("users" "reservations" "content" "notifications" "weather" "analytics")

for service in "${microservices[@]}"; do
    # Crear directorios de servicio primero
    mkdir -p "services/${service}-service/app/api"
    mkdir -p "services/${service}-service/app/core"
    mkdir -p "services/${service}-service/app/db"
    mkdir -p "services/${service}-service/app/models"
    mkdir -p "services/${service}-service/app/schemas"
    mkdir -p "services/${service}-service/app/services"
    mkdir -p "services/${service}-service/app/tests"
    mkdir -p "services/${service}-service/alembic/versions"
    
    # Ahora crear archivos
    touch "services/${service}-service/Dockerfile"
    touch "services/${service}-service/requirements.txt"
    touch "services/${service}-service/app/__init__.py"
    touch "services/${service}-service/app/main.py"
    
    # Core files
    touch "services/${service}-service/app/core/__init__.py"
    touch "services/${service}-service/app/core/config.py"
    touch "services/${service}-service/app/core/security.py"
    
    # DB files
    touch "services/${service}-service/app/db/__init__.py"
    touch "services/${service}-service/app/db/base.py"
    touch "services/${service}-service/app/db/session.py"
    
    # API files
    touch "services/${service}-service/app/api/__init__.py"
    touch "services/${service}-service/app/api/deps.py"
    touch "services/${service}-service/app/api/routes.py"
    
    # Models and Schemas
    touch "services/${service}-service/app/models/__init__.py"
    touch "services/${service}-service/app/schemas/__init__.py"
    
    # Services
    touch "services/${service}-service/app/services/__init__.py"
    
    # Alembic files
    touch "services/${service}-service/alembic/env.py"
    touch "services/${service}-service/alembic/README"
    touch "services/${service}-service/alembic/script.py.mako"
    touch "services/${service}-service/alembic.ini"
done

# Crear estructura para docker-compose y configuraciones compartidas
mkdir -p docker
touch docker/docker-compose.yml
touch docker/docker-compose.override.yml
touch docker/.env

# Crear estructura para CI/CD
mkdir -p .github/workflows
touch .github/workflows/ci.yml
touch .github/workflows/cd.yml

# Crear directorios para scripts y herramientas
mkdir -p scripts
touch scripts/setup-dev.sh
touch scripts/run-tests.sh
chmod +x scripts/setup-dev.sh
chmod +x scripts/run-tests.sh

# Crear archivos de configuración global
touch .gitignore
touch .env.example

# Añadir contenido básico a .gitignore
cat > .gitignore << EOF
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
*.egg-info/
.installed.cfg
*.egg

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Docker
.dockerignore

# IDE
.idea/
.vscode/
*.swp
*.swo

# Logs
logs/
*.log

# Database
*.db
*.sqlite3

# OS
.DS_Store
Thumbs.db
EOF

echo "Estructura de directorios del proyecto creada exitosamente."
echo "Ubicación: $(pwd)"