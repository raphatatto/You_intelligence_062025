FROM python:3.11

WORKDIR /app

# Garante que o Python pesquise módulos em /app
ENV PYTHONPATH=/app

# Copia requirements e instala
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o resto do seu repo
COPY . .

# Roda seu app apontando pro main da pasta certa
CMD ["uvicorn", "apps.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
