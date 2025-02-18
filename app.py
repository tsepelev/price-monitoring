import os

import requests
from flask import Flask, render_template, request
from flask.cli import load_dotenv

load_dotenv()
app = Flask(__name__)


@app.route("/")
def index():
    query = request.args.get("q")
    url = "https://www.searchapi.io/api/v1/search"
    params = {
        "engine": "google_shopping",
        "q": query,
        "gl": "ru",
        "hl": "ru",
        "location": "Moscow",
        "api_key": os.environ.get("SEARCH_API_KEY"),
    }
    resp = ""
    if query:
        response = requests.get(
            url,
            params=params,
            timeout=10
        )
        # response = requests.get(
        #     url="https://www.searchapi.io/api/v1/searches/search_6d97LXP4moruanBXWk03EOrl"
        # )
        if response.status_code == 200:
            resp = response.json()
    return render_template("index.html", content=resp)


if __name__ == "__main__":
    app.run(debug=bool(os.environ.get("DEBUG", False)))
