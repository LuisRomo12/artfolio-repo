# ==========================================
# Etapa 1: Compilación del Frontend (Node.js Vue 3)
# ==========================================
FROM node:18-alpine AS frontend-builder
WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm install

COPY frontend/ ./
RUN npm run build

# ==========================================
# Etapa 2: Entorno de Ejecución (Python FastAPI + Vue 3 Assets)
# ==========================================
FROM python:3.10-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000

WORKDIR /app

# Instalar dependencias de Python
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fuente del backend
COPY backend/ ./

# Copiar activos del frontend desde la etapa de compilación
COPY --from=frontend-builder /app/frontend/dist ./static/frontend

# Exponer puerto
EXPOSE 8000

# Comando de inicio
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
