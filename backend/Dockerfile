# Imagen de la API (FastAPI + uvicorn).
FROM python:3.14-slim

# Sin archivos .pyc y con logs inmediatos (sin búfer).
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Primero las dependencias: si no cambian, Docker reutiliza esta capa en cada build.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

# La API no corre como root.
RUN useradd --create-home --uid 10001 api
USER api

EXPOSE 8000

# Docker considera el contenedor "sano" cuando /api/health responde.
HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/health', timeout=2)"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
