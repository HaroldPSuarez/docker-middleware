FROM python:3.9-slim

WORKDIR /app

# Copiamos primero los requirements (si existen)
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt || true

# Copiamos el resto del código
COPY . .

# Evitamos el buffer en los logs de Python
ENV PYTHONUNBUFFERED=1

# Exponemos el puerto
EXPOSE 9000

# Comando para ejecutar el middleware
CMD ["python", "-u", "middleware.py"]
