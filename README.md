# Price Monitoring App

## Overview

This application allows users to search for products on Google Shopping and view their prices from different sellers. It uses the SearchAPI.io API to retrieve product information and displays it in a user-friendly table.

## Functionality

-   **Search:** Users can enter a product name in the search bar to find relevant products on Google Shopping.
-   **Display:** The application displays a table with the following information for each product:
    -   Product image
    -   Product title (linked to the product page)
    -   Seller
    -   Price

## Technologies Used

-   **Python:** The backend is built using Python.
-   **Flask:** A micro web framework for creating the web application.
-   **SearchAPI.io:** An API for searching Google Shopping.
-   **HTML/CSS:** For creating the user interface.
-   **Pico.css:** A lightweight CSS framework for styling the application.
-   **Jinja:** A template engine for rendering HTML pages with dynamic data.

## Setup and Installation

1.  **Clone the repository:**

    ```bash
    git clone <repository_url>
    cd price-monitoring
    ```

2.  **Install dependencies:**

    ```bash
    pip install Flask requests python-dotenv
    ```

3.  **Set up environment variables:**

    -   Create a `.env` file in the project root.
    -   Add your SearchAPI.io API key to the `.env` file:

        ```
        SEARCH_API_KEY=your_api_key
        ```

4.  **Run the application:**

    ```bash
    python app.py
    ```

5.  **Access the application:**

    Open your web browser and go to `http://127.0.0.1:5000/`.

## Code Explanation

### `app.py`

-   Imports necessary libraries: `os`, `requests`, `Flask`, `render_template`, `request`, and `load_dotenv`.
-   Loads environment variables from the `.env` file using `load_dotenv()`.
-   Creates a Flask application instance.
-   Defines the `index` route:
    -   Retrieves the search query from the request parameters.
    -   Constructs the parameters for the SearchAPI.io API request.
    -   Sends a request to the SearchAPI.io API.
    -   Parses the JSON response from the API.
    -   Renders the `index.html` template with the API response data.
-   Runs the Flask application in debug mode if the script is executed directly.

### `templates/index.html`

-   Uses HTML and Pico.css to create the user interface.
-   Includes a search form that allows users to enter a product name.
-   Displays the search results in a table:
    -   Iterates through the `shopping_results` in the `content` data passed from the Flask application.
    -   Displays the product image, title (as a link), seller, and price for each product.

## API Usage

The application uses the SearchAPI.io API to search for products on Google Shopping.  You need to obtain an API key from [SearchAPI.io](https://www.searchapi.io/) and set it as an environment variable (`SEARCH_API_KEY`).

## Future Enhancements

-   Implement pagination for search results.
-   Add error handling for API requests.
-   Implement caching to reduce API usage.
-   Allow users to filter search results by price, seller, etc.
-   Improve the user interface with more advanced styling and features.
-   Deploy the application to a production environment.