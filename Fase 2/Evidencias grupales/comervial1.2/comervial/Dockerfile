# Imagen base
FROM python:3.12-slim

# Evita cacheos y cosas interactivas
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Instalar dependencias del sistema
RUN apt-get update \
    && apt-get install -y build-essential default-libmysqlclient-dev pkg-config \
    && apt-get clean

# Crear directorio
WORKDIR /app

# Copiar requirements
COPY requirements.txt .

# Instalar dependencias
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copiar todo el proyecto al contenedor
COPY . .

# Exponer el puerto en el que Django corre
EXPOSE 8000

# Comando para arrancar el servidor
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
