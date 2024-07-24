## Используем официальный образ NGINX
#FROM nginx:latest
#
## Копируем файл конфигурации NGINX
#COPY nginx.conf /etc/nginx/nginx.conf
#
## Копируем статические файлы в директорию NGINX
#COPY app/static/css /usr/share/nginx/html/static/css
#COPY app/static/js /usr/share/nginx/html/static/js
#COPY app/templates /usr/share/ngnix/html

# Используем официальный образ Python в качестве базового
FROM python:3.8

# Устанавливаем переменные окружения для неинтерактивного режима установки
ENV PYTHONUNBUFFERED 1


# Копируем файлы requirements.txt
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Копируем все файлы приложения в рабочую директорию
COPY . /app

# Создаем рабочую директорию
WORKDIR /app

# Открываем порт, который будет использоваться FastAPI
EXPOSE 8000

# Запускаем приложение
CMD ["uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000"]
