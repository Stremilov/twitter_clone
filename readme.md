# Twitter Clone API
### Описание

Twitter Clone API — это бэкенд для корпоративного сервиса микроблогов. Приложение позволяет пользователям создавать, удалять твиты, ставить лайки, фоловить других пользователей и получать ленту твитов.
### Функциональные возможности

    Добавление нового твита.
    Удаление своего твита.
    Подписка на других пользователей.
    Отписка от других пользователей.
    Отметка твита как понравившегося.
    Удаление отметки «Нравится».
    Получение ленты из твитов.
    Добавление картинок к твитам.

### Нефункциональные требования

    Простое развертывание через Docker Compose.
    Сохранение данных между запусками.
    Документация всех ответов сервиса через Swagger.

### Используемые технологии

    FastAPI: для создания API.
    SQLAlchemy: для работы с базой данных.
    PostgreSQL: база данных.
    Docker и Docker Compose: для контейнеризации и оркестрации.
    Jinja2: для рендеринга HTML-шаблонов.
    aiofiles: для работы с файлами.

### Установка и запуск

    Клонируйте репозиторий:

    git clone <repository-url>
    cd twitter_clone


### Установите зависимости:

    pip install -r requirements.txt

### Настройте переменные окружения (например, добавьте файл .env):

    DATABASE_URL=postgresql://user:password@db/twitter_clone

### Запустите приложение с помощью Docker Compose:

    docker-compose up -d

    Приложение будет доступно по адресу http://localhost:8000.

## API эндпоинты
### Добавление нового твита


POST /api/tweets

Параметры:

    api-key: str
    Тело запроса (JSON):


    {
        "tweet_data": "string",
        "tweet_media_ids": [1, 2, 3]
    }

Ответ:
    
    {
        "result": true,
        "tweet_id": 1
    }

### Загрузка файлов

POST /api/medias

Параметры:

    api-key: str
    Форма: file="image.jpg"

    Ответ:
    
    json
    
    {
        "result": true,
        "media_id": 1
    }

### Удаление твита

DELETE /api/tweets/{id}

    Параметры:

    api-key: str

    Ответ:
    
    json
    
    {
        "result": true
    }

### Отметка твита как понравившегося
POST /api/tweets/{id}/likes

    Параметры:

    api-key: str

    Ответ:
    
    json
    
    {
        "result": true
    }

### Удаление отметки «Нравится»

DELETE /api/tweets/{id}/likes

    Параметры:

    api-key: str

    Ответ:
    
    json
    
    {
        "result": true
    }

### Подписка на пользователя

POST /api/users/{id}/follow

    Параметры:

    api-key: str

    Ответ:
    
    json
    
    {
        "result": true
    }

### Отписка от пользователя

DELETE /api/users/{id}/follow

    Параметры:

    api-key: str

    Ответ:
    
    json
    
    {
        "result": true
    }

### Получение ленты твитов

GET /api/tweets

    Параметры:

    api-key: str

    Ответ:
    
    json
    
    {
        "result": true,
        "tweets": [
            {
                "id": 1,
                "content": "string",
                "attachments": ["link_1", "link_2"],
                "author": {
                    "id": 1,
                    "name": "string"
                },
                "likes": [
                    {
                        "user_id": 1,
                        "name": "string"
                    }
                ]
            }
        ]
    }

### Получение информации о своем профиле

GET /api/users/me

    Параметры:

    api-key: str

    Ответ:
    
    json
    
    {
        "result": true,
        "user": {
            "id": 1,
            "name": "string",
            "followers": [
                {
                    "id": 1,
                    "name": "string"
                }
            ],
            "following": [
                {
                    "id": 1,
                    "name": "string"
                }
            ]
        }
    }

### Получение информации о произвольном профиле по id

GET /api/users/{id}

    Параметры:

    api-key: str

    Ответ:
    
    json
    
    {
        "result": true,
        "user": {
            "id": 1,
            "name": "string",
            "followers": [
                {
                    "id": 1,
                    "name": "string"
                }
            ],
            "following": [
                {
                    "id": 1,
                    "name": "string"
                }
            ]
        }
    }

### Документация

Swagger-документация доступна по адресу: http://localhost:8000/docs