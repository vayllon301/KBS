# Product Q&A Chatbot

This project implements a simple Flask-based chatbot capable of answering questions about products, their attributes, and other general queries based on a dataset defined in a JSON file.

## Overview

The chatbot uses Natural Language Processing (NLP) techniques to understand user input and generate relevant responses. Key functionalities include:

*   **Tokenization and Lemmatization**: User input text is processed to split it into tokens (words), remove stopwords, and reduce words to their base form (lemmas).
*   **Fuzzy Matching**: Used to find approximate matches between user tokens and defined keywords, allowing for flexibility in user input.
*   **Product and Attribute Identification**: The system can identify products and their attributes (such as size, color, style, material) mentioned in the user's query.
*   **Rule-Based System**: Responses are generated based on predefined rules and keywords found in the user input.

## Project Structure

*   `app.py`: Contains the main logic of the Flask application, natural language processing, and chatbot response generation.
*   `data.json`: JSON file удовольствия storing the data used by the chatbot, including responses, keywords, product information, and attributes.
*   `templates/index.html`: A simple HTML file to interact with the chatbot through a web interface. This file is already included in the `templates` directory.

## File Details

### `app.py`

This file is the core of the application and performs the following tasks:

1.  **Imports**: Imports necessary libraries such as Flask (for the web server), NLTK (for NLP tasks), and FuzzyWuzzy (for fuzzy matching).
2.  **`ensure_nltk_resources()`**: This function ensures that the required NLTK resources (like WordNet, stopwords, Punkt tokenizer, and the Perceptron tagger) are downloaded on the system. If not, it downloads them automatically the first time it runs.
3.  **`load_data()`**: Loads data from the `data.json` file.
4.  **Global Data Loading**: Different sections of the `data.json` file (responses, product\_responses, expanded\_keywords, products, attributes, attribute\_value\_maps) are loaded into global variables for easy access.
5.  **`fuzzy_match(token, keywords, threshold=80)`**: Compares a `token` with a list of `keywords` using the FuzzyWuzzy library. Returns `True` if the similarity ratio exceeds the `threshold` (default 80).
6.  **`extract_attribute_value(tokens, attr_name)`**: Extracts the value of a specific attribute (e.g., "red" for the "color" attribute) from the user's `tokens`. It looks for direct or fuzzy matches with attribute values defined in `attribute_value_maps`.
7.  **`identify_product_and_attributes(tokens)`**: Attempts to identify a product and its attributes from the `tokens`. It first looks for the product and then associated attributes.
8.  **`preprocess_text(user_input)`**:
    *   Converts user input to lowercase.
    *   Tokenizes the input (splits it into words).
    *   Performs Part-of-Speech (POS) tagging.
    *   Removes stopwords (common words like "the", "a", "is").
    *   Lemmatizes tokens (reduces words to their root form, e.g., "running" -> "run").
9.  **`get_wordnet_pos(tag)`**: Converts NLTK POS tags to a format compatible with the WordNet lemmatizer.
10. **`chatbot_response(user_input)`**:
    *   Preprocesses user input using `preprocess_text`.
    *   First, it checks for matches with `expanded_keywords` for general responses (greetings, goodbyes, etc.).
    *   If no match, it calls `identify_product_and_attributes` to look for products and attributes.
    *   If a product is identified:
        *   If no attributes are recognized, it returns the default response for that product.
        *   If attributes are recognized, it looks for specific responses for those product-attribute-value combinations. If no specific response is found, it might use a default response for the attribute.
    *   If no relevant match is found, it returns a generic message indicating it didn't understand the query.
11. **Flask Routes**:
    *   `@app.route('/')`: Serves the main page (`index.html`).
    *   `@app.route('/chat', methods=['POST'])`: Receives user messages in JSON format, calls `chatbot_response` to get a response, and returns it in JSON format.
12. **App Execution**: If the script is run directly (`if __name__ == '__main__':`), it starts the Flask development server.

### `data.json`

This file is crucial as it contains all the chatbot's knowledge. Its structure is as follows:



*   **`responses`**: A dictionary where keys are intent categories (e.g., "greeting") and values are the chatbot's responses.
*   **`product_responses`**: A nested dictionary. The first key is the product name. The value is another dictionary containing:
    *   `"default"`: The generic response for that product if no attributes are specified.
    *   Attribute keys (e.g., `"color"`, `"size"`): Each contains a dictionary with specific attribute values (e.g., `"silver"`, `"13-inch"`) and their corresponding responses, plus a `"default"` response for the attribute if the value is not recognized.
*   **`expanded_keywords`**: A dictionary where keys are the same intent categories as in `responses`, and values are lists of keywords associated with that intent.
*   **`products`**: A dictionary where keys are normalized product names and values are lists of keywords users might use to refer to them.
*   **`attributes`**: A dictionary where keys are normalized attribute names and values are lists of keywords for those attributes.
*   **`size_values`, `color_values`, `style_values`, `material_values`**: Dictionaries specific to each attribute type. Keys are normalized attribute values (e.g., "13-inch", "red"), and values are lists of keywords users might use for those values.

## How to Run the Application

Follow these steps to get the chatbot running:

1.  **Prerequisites**:
    *   Ensure you have Python 3.x installed.
    *   You will need `pip` (Python's package manager) to install dependencies.

2.  **Download the Project**:
    Download the project files, typically as a ZIP archive, and extract them to a directory on your computer.

3.  **Create a Virtual Environment (Recommended)**:
    It's good practice to use virtual environments to isolate project dependencies.
    Navigate to your project directory in the terminal and run:
    ```bash
    python -m venv venv
    ```
    Activate the virtual environment:
    *   On macOS and Linux:
        ```bash
        source venv/bin/activate
        ```
    *   On Windows:
        ```bash
        .\venv\Scripts\activate
        ```

4.  **Install Dependencies**:
    Install the required libraries:
    ```bash
    pip install Flask nltk fuzzywuzzy python-Levenshtein
    ```
    

5.  **Verify `templates/index.html`**:
    The `index.html` file for the chat interface is already included in the `templates` directory. Ensure it is present.

6.  **Run the Flask Application**:
    Open your terminal in the project's root directory (where `app.py` is located) and run the following commands:

    Set the `FLASK_APP` environment variable and then use `flask run`.
    ```bash
    flask run
    ```
    This will start the development server, usually at `http://127.0.0.1:5000/`. The first time it runs, it might take a moment if it needs to download NLTK resources.

    Alternatively, you can run the `app.py` script directly:
    ```bash
    python app.py
    ```
    This will also start the development server.

7.  **Interact with the Chatbot**:
    Open your web browser and go to `http://127.0.0.1:5000/`. You should see the interface from `index.html` and can start chatting.
