# Standard library imports
import logging
import os
from functools import wraps

# Third-party imports
from cachetools import TTLCache
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
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


def ttl_cache(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        key = str(args) + str(kwargs)
        if key in cache:
            return cache[key]
        result = await func(*args, **kwargs)
        cache[key] = result
        return result

    return wrapper


@ttl_cache
async def search_products(
    query: str = None,
    location: str = "Moscow",
    language: str = "ru",
    country: str = "ru",
    product_id: str = None,
    engine: str = "google_shopping",
):
    params = {
        "engine": engine,
        "q": query,
        "product_id": product_id,
        "gl": country,
        "hl": language,
        "location": location,
        "api_key": API_KEY,
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                SEARCH_API_URL, params=params, timeout=DEFAULT_TIMEOUT
            )
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as e:
            logger.error(f"API request failed: {e} | Params: {params}")
            return {"error": str(e)}


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def index(
    request: Request,
    q: str = "",
    location: str = "Moscow",
    hl: str = "ru",
    gl: str = "ru",
):
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
async def product_detail(request: Request, product_id: str, location: str = "Moscow"):
    result = await search_products(
        product_id=product_id, engine="google_product_offers", location=location
    )
    return templates.TemplateResponse(
        "products.html", {"request": request, "content": result, "searches": searches}
    )


@app.get("/api/search")
async def api_search(
    q: str = "", location: str = "Moscow", hl: str = "ru", gl: str = "ru"
):
    result = (
        await search_products(query=q, location=location, language=hl, country=gl)
        if q
        else {}
    )
    return JSONResponse(content=result)


@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return templates.TemplateResponse("404.html", {"request": request}, status_code=404)


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    logger.error(f"Server error: {exc}")
    return templates.TemplateResponse("500.html", {"request": request}, status_code=500)


# Запуск с Uvicorn (если запускается как скрипт)
if __name__ == "__main__":
    import uvicorn
    
    # Проверка критических переменных окружения
    required_env_vars = ["SEARCH_API_KEY"]
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    if missing_vars:
        logger.critical(f"Missing required environment variables: {', '.join(missing_vars)}")
        raise SystemExit(1)

    # Получение конфигурации
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "false").lower() in ("1", "true", "yes")

    # Логирование параметров запуска
    logger.info(f"Starting application on {host}:{port}")
    logger.info(f"Debug mode: {debug}")
    
    try:
        uvicorn.run(
            "main:app",
            host=host,
            port=port,
            reload=debug
        )
    except Exception as e:
        logger.critical(f"Failed to start application: {e}")
        raise SystemExit(1)
