"""Improved Flask application for searching products using searchapi.io."""

import os
import logging
from functools import lru_cache

import requests
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

# Настройка логирования
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Загрузка переменных окружения
load_dotenv()
app = Flask(__name__)

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

# Получение API ключа из переменных окружения с проверкой
API_KEY = os.environ.get("SEARCH_API_KEY")
if not API_KEY:
    logger.error("API key is not set in environment variables!")

# Константы
SEARCH_API_URL = "https://www.searchapi.io/api/v1/search"
DEFAULT_TIMEOUT = 10


@lru_cache(maxsize=32)
def search_products(
    query=None,
    location="Moscow",
    language="ru",
    country="ru",
    product_id=None,
    engine="google_shopping",
):
    """
    Search for products with caching for repeated queries.

    Args:
        query (str): Search query
        location (str): Location for search context
        language (str): Language code
        country (str): Country code
        product_id (str): Product ID for detailed search
        engine (str): Search engine to use

    Returns:
        dict: API response or error information
    """

    if not API_KEY:
        return {"error": "API key not configured"}

    params = {
        "engine": engine,
        "q": query,
        "product_id": product_id,
        "gl": country,
        "hl": language,
        "location": location,
        "api_key": API_KEY,
    }

    try:
        response = requests.get(SEARCH_API_URL, params=params, timeout=DEFAULT_TIMEOUT)
        response.raise_for_status()  # Вызывает исключение для HTTP-ошибок
        print(response.url)
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed: {str(e)}")
        return {"error": f"Search API request failed: {str(e)}"}


@app.route("/")
def index():
    """Main page with search form."""
    query = request.args.get("q", "")
    location = request.args.get("location", "Moscow")
    language = request.args.get("hl", "ru")
    country = request.args.get("gl", "ru")
    result = (
        search_products(
            query=query, location=location, language=language, country=country
        )
        if query
        else {}
    )
    return render_template("index.html", content=result, query=query, searches=searches)


@app.route("/product/<product_id>")
def product(product_id):
    """Product page with details."""
    location = request.args.get("location", "Moscow")
    result = (
        search_products(
            product_id=product_id, engine="google_product_offers", location=location
        )
        if product_id
        else {}
    )
    print(result)
    return render_template("products.html", content=result, searches=searches)


@app.route("/api/search")
def api_search():
    """JSON API endpoint for searches."""
    query = request.args.get("q", "")
    location = request.args.get("location", "Moscow")
    language = request.args.get("hl", "ru")
    country = request.args.get("gl", "ru")

    result = search_products(query, location, language, country) if query else {}
    return jsonify(result)


@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors."""
    return render_template("404.html"), 404


@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors."""
    logger.error(f"Server error: {str(e)}")
    return render_template("500.html"), 500


if __name__ == "__main__":
    """Run the Flask application."""
    debug_mode = os.environ.get("DEBUG", "").lower() in ("true", "1", "yes")
    app.run(
        host=os.environ.get("HOST", "0.0.0.0"),
        port=int(os.environ.get("PORT", 8000)),
        debug=debug_mode,
    )
