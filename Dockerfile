# Используем официальный образ Python в качестве базового
FROM python:3.8

# Устанавливаем переменные окружения для неинтерактивного режима установки
ENV PYTHONUNBUFFERED 1

# Создаем рабочую директорию
WORKDIR /app

# Копируем файлы requirements.txt и устанавливаем зависимости
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Копируем все файлы приложения в рабочую директорию
COPY . .

# Создаем директории для загрузок и статики
RUN mkdir -p /app/uploads /app/static

# Открываем порт, который будет использоваться FastAPI
EXPOSE 8000

# Запускаем приложение
CMD ["uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000"]
