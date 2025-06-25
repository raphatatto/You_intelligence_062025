FROM python:3.11

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código da API
COPY ./apps/api /app

# Copia a pasta packages (que está fora da API!)
COPY ./packages /app/packages

# Ajuste do path para reconhecer ambos
ENV PYTHONPATH=/app:/app/packages

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
