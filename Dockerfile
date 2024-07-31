# Используем официальный образ Python в качестве базового
FROM python:3.8

# Устанавливаем переменные окружения для неинтерактивного режима установки
ENV PYTHONUNBUFFERED 1


# Копируем файлы requirements.txt
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Создаем рабочую директорию
WORKDIR /app

# Копируем все файлы приложения в рабочую директорию
COPY . /app

# Открываем порт, который будет использоваться FastAPI
EXPOSE 8000

# Запускаем приложение
CMD ["uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000"]
