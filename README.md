# Система мониторинга цен

Веб-приложение для отслеживания цен на товары через Google Shopping. Построено с использованием FastAPI и SearchAPI.io.

![Google Shopping](https://github.com/tsepelev/price-monitoring/blob/master/img/shopping.png?raw=true)
![Google Search](https://github.com/tsepelev/price-monitoring/blob/master/img/search.png?raw=true)

## Функциональности

- Поиск товаров через Google Shopping
- Просмотр детальной информации о товаре и предложениях
- Кэширование результатов поиска
- API endpoint для интеграции
- Поддержка различных локаций и языков

## Требования

- Python 3.7+
- FastAPI
- httpx
- cachetools
- python-dotenv
- Jinja2

## Установка

1. Клонируйте репозиторий:

```bash
git clone [url-репозитория]
cd price-monitoring
```

2. Установите зависимости:

```bash
pip install -r requirements.txt
```

3. Создайте файл `.env` в корневой директории:

```env
SEARCH_API_KEY=ваш_ключ_api
HOST=0.0.0.0
PORT=8000
DEBUG=false
```

## Запуск

```bash
python main.py
```

Приложение будет доступно по адресу: `http://localhost:8000`

## API Endpoints

- `GET /` - Главная страница с формой поиска
- `GET /product/{product_id}` - Страница с детальной информацией о товаре
- `GET /api/search` - API endpoint для поиска товаров

### Параметры API

- `q` - поисковый запрос
- `location` - местоположение (по умолчанию: "Moscow")
- `hl` - язык результатов (по умолчанию: "ru")
- `gl` - страна поиска (по умолчанию: "ru")

## Примечания

- Для работы приложения требуется действительный API ключ от SearchAPI.io
- Результаты поиска кэшируются на 1 час
- Поддерживается обработка ошибок и пользовательские страницы ошибок
