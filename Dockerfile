FROM python:3.11-slim

# Instalar pdftk y dependencias del sistema
RUN apt-get update && apt-get install -y \
    pdftk \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar requirements e instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar archivos del proyecto
COPY api_ss4_filler.py .
COPY ss4_form_filler_pdftk.py .
COPY ss4_field_mapping.json .
COPY test_api.py .

# Crear directorio para templates (outputs ya no se necesita - se usa /tmp)
RUN mkdir -p /app/templates

# Exponer puerto
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Comando para iniciar la aplicación
CMD ["uvicorn", "api_ss4_filler:app", "--host", "0.0.0.0", "--port", "8000"]
