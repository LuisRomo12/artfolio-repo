# ==========================================
# Entorno de Ejecución (Python FastAPI + Vue 3 Frontend)
# ==========================================
FROM python:3.10-slim AS runtime

# Variables de entorno para Python y puerto por defecto
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000

WORKDIR /app

# Instalar dependencias de Python
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fuente del backend
COPY backend/ ./

# Copiar el frontend compilado hacia static/frontend
COPY frontend/dist ./static/frontend

# Exponer puerto (Cloud Run inyectará la variable $PORT)
EXPOSE 8000

# Comando de inicio usando sh para evaluar dinámicamente $PORT
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
