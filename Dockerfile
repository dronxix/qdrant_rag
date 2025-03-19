# Используем официальный образ Python (версия 3.10 на базе slim)
FROM python:3.10-slim

# Установка системных зависимостей (Poppler и другие необходимые пакеты)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    poppler-utils \
    build-essential \
    libpoppler-cpp-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
    
# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем PDF инструкцию (убедитесь, что файл называется КС.pdf)
COPY КС.pdf /app/КС.pdf

# Копируем код бота (например, файл bot.py)
COPY tg_bot.py /app/tg_bot.py

# Копируем файл зависимостей и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Команда для запуска бота
CMD ["python", "tg_bot.py"]
