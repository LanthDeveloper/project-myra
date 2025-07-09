# Imagen base Ubuntu con Python
FROM python:3.11-slim

# Evita prompts de apt y mantiene el sistema actualizado
ENV DEBIAN_FRONTEND=noninteractive

# Actualiza, instala dependencias necesarias para Playwright
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    unzip \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    xdg-utils \
    libu2f-udev \
    && rm -rf /var/lib/apt/lists/*

# Crea carpeta de trabajo
WORKDIR /app

# Copia los archivos del proyecto
COPY . .

# Instala Playwright
RUN pip install --upgrade pip && pip install playwright
RUN playwright install

# Instala tus dependencias (reemplaza requirements.txt si es necesario)
RUN python -m venv .venv
RUN . .venv/bin/activate && pip install -r requirements.txt

# Expone el puerto si tu app lo necesita (opcional)
EXPOSE 8000

# Comando por defecto (usa tu profile: cd src && python main.py)
CMD ["/bin/bash", "-c", ". .venv/bin/activate && cd src && python main.py"]
