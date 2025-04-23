# Standard library imports
import logging
import os
from functools import wraps

# Third-party imports
from cachetools import TTLCache
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
import httpx
from starlette.responses import HTMLResponse

# Настройка логирования
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Загрузка переменных окружения
load_dotenv()

API_KEY = os.environ.get("SEARCH_API_KEY")
if not API_KEY:
    logger.critical("SEARCH_API_KEY is not set!")
    raise SystemExit("SEARCH_API_KEY is required")

SEARCH_API_URL = "https://www.searchapi.io/api/v1/search"
DEFAULT_TIMEOUT = 10

# Примеры поисковых запросов
searches = [
    {
        "query": 'Телевизор LG 65" 65UR81006LJ.ARUB',
        "url": "https://www.searchapi.io/api/v1/searches/search_6d97LXP4moruanBXWk03EOrl",
    },
    {
        "query": "САНОКС УЛЬТРА БЕЛЫЙ чистящее средство д/сантехники 750мл",
        "url": "https://www.searchapi.io/api/v1/searches/search_ZW75dANvqloT2aRax4blrDJ3",
    },
]

# Инициализация FastAPI
app = FastAPI()
templates = Jinja2Templates(directory="templates")
# app.mount("/static", StaticFiles(directory="static"), name="static")

# Настройка CORS (если потребуется)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

cache = TTLCache(maxsize=100, ttl=3600)  # 1 час TTL


def extract_price(extensions: list) -> float | None:
    """Извлечение цены из списка расширений."""
    if not extensions:
        return None
    for ext in extensions:
        if "₽" in ext:
            price_str = ext.replace("₽", "").replace(" ", "")
            try:
                price = float(price_str.replace(",", "."))
                # Форматируем цену по стандартам РФ (разделитель тысяч - пробел, десятичная точка)
                return round(price, 2)
            except ValueError:
                return None
    return None


def ttl_cache(func):
    """Декоратор для кэширования результатов функции с TTL."""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        key = str(args) + str(kwargs)
        cached_result = cache.get(key)

        # Проверяем, что кэшированный результат не пустой
        if (
            cached_result
            and isinstance(cached_result, dict)
            and cached_result.get("organic_results")
        ):
            return cached_result

        result = await func(*args, **kwargs)
        # Кэшируем только если результат не пустой
        if result and isinstance(result, dict) and result.get("organic_results"):
            cache[key] = result
        return result

    return wrapper


@ttl_cache
async def search_products(
    query: str | None = None,
    location: str = "Moscow",
    language: str = "ru",
    country: str = "ru",
    product_id: str | None = None,
    time_period: str | None = None,
    engine: str = "google_shopping",
    num: int = 50,
) -> dict:
    """Поиск товаров через API.

    Args:
        query: Поисковый запрос
        location: Локация для поиска
        language: Язык результатов
        country: Страна для поиска
        product_id: ID продукта
        time_period: Этот параметр ограничивает результаты URL-адресами на основе даты. 
        engine: Поисковый движок
        num: Количество результатов

    Returns:
        dict: Результаты поиска
    """
    params = {
        "engine": engine,
        "q": query,
        "product_id": product_id,
        "time_period": time_period,
        "gl": country,
        "hl": language,
        "location": location,
        "api_key": API_KEY,
        "num": num,
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                SEARCH_API_URL, params=params, timeout=DEFAULT_TIMEOUT
            )
            response.raise_for_status()
            data = response.json()

            # Добавляем проверку на наличие данных
            if not data:
                return {"error": "Empty response from API"}

            # Обработка цен
            if "organic_results" in data:
                for item in data["organic_results"]:
                    if "rich_snippet" in item and "extensions" in item["rich_snippet"]:
                        item["price"] = extract_price(
                            item["rich_snippet"]["extensions"]
                        )
                        # Добавляем форматированную цену для отображения
                        if item["price"]:
                            item["formatted_price"] = f"{item['price']:,.2f} ₽".replace(
                                ",", " "
                            )

            return data

        except httpx.RequestError as e:
            logger.error("API request failed: %s | Params: %s", e, params)
            return {"error": str(e)}


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def index(
    request: Request,
    q: str = "",
    location: str = "Moscow",
    hl: str = "ru",
    gl: str = "ru",
) -> HTMLResponse:
    """Главная страница с формой поиска."""
    result = (
        await search_products(query=q, location=location, language=hl, country=gl)
        if q
        else {}
    )
    if "error" in result:
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": result["error"]},
            status_code=500,
        )
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "content": result, "query": q, "searches": searches},
    )


@app.get("/product/{product_id}", response_class=HTMLResponse, include_in_schema=False)
async def product_detail(
    request: Request, product_id: str, location: str = "Moscow"
) -> HTMLResponse:
    """Страница детальной информации о продукте."""
    result = await search_products(
        product_id=product_id, engine="google_product_offers", location=location
    )
    return templates.TemplateResponse(
        "products.html", {"request": request, "content": result, "searches": searches}
    )


@app.get("/search", response_class=HTMLResponse, include_in_schema=False)
async def search_detail(request: Request, q: str) -> HTMLResponse:
    """Страница результатов поиска."""
    if not q:
        return templates.TemplateResponse(
            "search.html",
            {"request": request, "content": {}, "query": "", "searches": searches},
        )

    result = await search_products(
        query=q + " купить",
        engine="google",
    )
    # Фильтруем результаты, оставляя только те, где есть цена
    if "organic_results" in result:
        result["organic_results"] = [
            item for item in result["organic_results"] if item.get("price") is not None
        ]

    return templates.TemplateResponse(
        "search.html",
        {"request": request, "content": result, "query": q, "searches": searches},
    )


@app.exception_handler(404)
async def not_found_handler(request: Request, exc: Exception) -> HTMLResponse:
    """Обработчик 404 ошибки."""
    return templates.TemplateResponse("404.html", {"request": request}, status_code=404)


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: Exception) -> HTMLResponse:
    """Обработчик 500 ошибки."""
    logger.error("Server error: %s", exc)
    return templates.TemplateResponse("500.html", {"request": request}, status_code=500)


# Запуск с Uvicorn (если запускается как скрипт)
if __name__ == "__main__":
    import uvicorn

    # Проверка критических переменных окружения
    required_env_vars = ["SEARCH_API_KEY"]
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    if missing_vars:
        logger.critical(
            f"Missing required environment variables: {', '.join(missing_vars)}"
        )
        raise SystemExit(1)

    # Получение конфигурации
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "false").lower() in ("1", "true", "yes")

    # Логирование параметров запуска
    logger.info(f"Starting application on {host}:{port}")
    logger.info(f"Debug mode: {debug}")

    try:
        uvicorn.run("main:app", host=host, port=port, reload=debug)
    except Exception as e:
        logger.critical(f"Failed to start application: {e}")
        raise SystemExit(1)
