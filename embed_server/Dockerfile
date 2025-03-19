# Используем официальный python-образ | Use official Python image
FROM python:3.9-slim

# Устанавливаем рабочую директорию | Set working directory
WORKDIR /app

# Копируем файл зависимостей | Copy dependencies file
COPY requirements.txt .

# Устанавливаем зависимости | Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Копируем ваш код | Copy your code
COPY server.py .

# Открываем порт 8080 | Expose port 8080
EXPOSE 8080

# Запускаем приложение | Run the application
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8080"]