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
        "location": "Moscow,Russian Federation",
        "api_key": os.environ.get("SEARCH_API_KEY"),
    }
    resp = ""
    if query:
        # response = requests.get(
        #     url,
        #     params=params,
        # )
        response = requests.get(
            "https://www.searchapi.io/api/v1/searches/search_6d97LXP4moruanBXWk03EOrl"
        )
        resp = response.json()
    return render_template("index.html", content=resp)


if __name__ == "__main__":
    app.run(debug=True)
