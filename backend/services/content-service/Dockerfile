# backend\services\content-service\Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copiar archivos de dependencias
COPY requirements.txt /app/

# Instalar dependencias de Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente
COPY . /app/

# Hacer ejecutable el script de inicio
COPY start.sh /app/
RUN chmod +x /app/start.sh

# Puerto en el que escucha el microservicio
EXPOSE 8002

# Script de inicio como punto de entrada
ENTRYPOINT ["/app/start.sh"]

# Comando para ejecutar la aplicación
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002", "--reload"]