# Мониторинг цен на товары

Веб-приложение для поиска и отслеживания цен на товары с использованием API searchapi.io.

## Возможности

- Поиск товаров через Google Shopping
- Просмотр детальной информации о товаре
- Отслеживание цен у разных продавцов
- API endpoint для интеграции
- Кэширование результатов поиска

## Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/yourusername/price-monitoring.git
cd price-monitoring
```

2. Создайте виртуальное окружение и активируйте его:
```bash
python -m venv venv
source venv/bin/activate  # для Linux/Mac
venv\Scripts\activate     # для Windows
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Создайте файл `.env` и добавьте ваш API ключ:
```
SEARCH_API_KEY=ваш_ключ_api
DEBUG=True
```

## Запуск

```bash
python app.py
```

Приложение будет доступно по адресу: http://localhost:8000

## Переменные окружения

- `SEARCH_API_KEY`: Ключ API для searchapi.io
- `DEBUG`: Режим отладки (True/False)
- `HOST`: Хост для запуска приложения (по умолчанию 0.0.0.0)
- `PORT`: Порт для запуска приложения (по умолчанию 8000)

## API Endpoints

### GET /api/search
Поиск товаров через API.

Параметры:
- `q`: Поисковый запрос
- `location`: Местоположение (по умолчанию "Moscow")
- `hl`: Язык (по умолчанию "ru")
- `gl`: Страна (по умолчанию "ru")

## Технологии

- Python 3.x
- Flask
- searchapi.io
- Requests
- python-dotenv

## Лицензия

MIT
