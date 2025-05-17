# TMDB Proxy Service

Прокси-сервис для API TMDB (The Movie Database), написанный с использованием FastAPI.

## Описание

Этот сервис выступает в качестве прокси между клиентами и API TMDB. Он перенаправляет все запросы на TMDB API и возвращает полученные ответы клиентам. Это может быть полезно для:

- Кэширования запросов
- Логирования и мониторинга
- Добавления дополнительной логики обработки запросов

## Требования

- Python 3.8+
- FastAPI
- Uvicorn
- HTTPX
- python-dotenv

## Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/yourusername/ProxyServiceTMDB.git
cd ProxyServiceTMDB
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Настройте переменные окружения, создав файл `.env` в корне проекта:
```
TARGET_API_BASE_URL=https://api.themoviedb.org/3
ENABLE_CACHE=true
CACHE_TTL=300
CACHE_CLEANUP_INTERVAL=60
```

## Запуск

Запустите сервис с помощью Uvicorn:

```bash
uvicorn main:app --reload
```

Сервис будет доступен по адресу http://localhost:8000.

## Использование

Просто отправляйте запросы к этому сервису так же, как вы бы отправляли их к TMDB API, с префиксом `/TMDBProxy`:

```
GET http://localhost:8000/TMDBProxy/movie/popular?api_key=your_tmdb_api_key_here
```

Этот запрос будет перенаправлен на `https://api.themoviedb.org/3/movie/popular?api_key=your_tmdb_api_key_here`.

### Кэширование

Сервис автоматически кэширует GET-запросы для повышения производительности. Кэш имеет следующие настройки:

- `CACHE_TTL` - время жизни записей в кэше (по умолчанию 300 секунд)
- `CACHE_CLEANUP_INTERVAL` - интервал автоматической очистки устаревших записей (по умолчанию 60 секунд)

Статистику кэша можно посмотреть по адресу:
- `GET /TMDBProxy/cache/stats` - получение статистики кэша

## API документация

Документация FastAPI доступна по адресу:
- http://localhost:8000/docs - Swagger UI
- http://localhost:8000/redoc - ReDoc

## Лицензия

MIT 