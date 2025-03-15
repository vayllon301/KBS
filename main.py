import nltk
import pandas as pd
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet, stopwords
from fuzzywuzzy import fuzz

nltk.download('wordnet')
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')

# Basic responses
responses = {
    "return": "You can return anytime within 30 days with all the costs covered",
    "deliver": "We offer free delivery for orders above $50. Standard shipping takes 3-5 business days.",
    "discount": "We have seasonal discounts! Check our website for the latest deals.",
    "availability": "Please specify the product name, and I can check if it's in stock.",
    "exit": "exit",
}

# Product-specific responses
product_responses = {
    "tshirt": {
        "default": "We have various t-shirts available in different sizes and colors.",
        "size": {
            "small": "We have small t-shirts available in red, blue, and black colors.",
            "medium": "We have medium t-shirts available in all colors: red, blue, black, and white.",
            "large": "We have large t-shirts available in blue and black colors.",
            "xlarge": "We have extra large t-shirts available in limited colors: black and white."
        },
        "color": {
            "red": "Red t-shirts are available in small and medium sizes.",
            "blue": "Blue t-shirts are available in small, medium, and large sizes.",
            "black": "Black t-shirts are available in all sizes: small, medium, large, and extra large.",
            "white": "White t-shirts are available in medium and extra large sizes."
        }
    },
    "jeans": {
        "default": "We have various jeans available in different sizes and styles.",
        "size": {
            "30": "Size 30 jeans are available in slim and regular fit.",
            "32": "Size 32 jeans are available in all fits: slim, regular, and relaxed.",
            "34": "Size 34 jeans are available in regular and relaxed fit.",
            "36": "Size 36 jeans are available in relaxed fit only."
        },
        "style": {
            "slim": "Slim fit jeans are available in sizes 30 and 32.",
            "regular": "Regular fit jeans are available in sizes 30, 32, and 34.",
            "relaxed": "Relaxed fit jeans are available in sizes 32, 34, and 36."
        }
    }
}


def get_wordnet_pos(tag):
    tag_dict = {
        'J': wordnet.ADJ,
        'N': wordnet.NOUN,
        'V': wordnet.VERB,
        'R': wordnet.ADV
    }
    return tag_dict.get(tag[0].upper(), wordnet.NOUN)


# Enhanced keyword categories
expanded_keywords = {
    "return": {"return", "refund", "exchange", "give back", "send back"},
    "deliver": {"deliver", "shipping", "transport", "shipment", "deliver"},
    "discount": {"discount", "sale", "offer", "deal", "promotion", "coupon"},
    "availability": {"stock", "available", "inventory", "in store"},
    "exit": {"exit", "quit", "leave"},
}

# Entity recognition dictionaries
products = {
    "tshirt": {"tshirt", "t-shirt", "t shirt", "shirt", "tee"},
    "jeans": {"jeans", "denim", "pants", "trousers"}
}

attributes = {
    "size": {"size", "fit", "dimension"},
    "color": {"color", "colour", "shade"},
    "style": {"style", "fit", "cut", "design"}
}

size_values = {
    "small": {"small", "s", "sm"},
    "medium": {"medium", "m", "med"},
    "large": {"large", "l", "lg"},
    "xlarge": {"xlarge", "xl", "extra large"},
    "30": {"30", "30 inch", "30\""},
    "32": {"32", "32 inch", "32\""},
    "34": {"34", "34 inch", "34\""},
    "36": {"36", "36 inch", "36\""}
}

color_values = {
    "red": {"red", "crimson", "scarlet"},
    "blue": {"blue", "navy", "azure"},
    "black": {"black", "jet black"},
    "white": {"white", "snow white", "ivory"}
}

style_values = {
    "slim": {"slim", "skinny", "tight"},
    "regular": {"regular", "standard", "normal"},
    "relaxed": {"relaxed", "loose", "comfortable"}
}


def fuzzy_match(token, keywords, threshold=90):
    for keyword in keywords:
        ratio = fuzz.ratio(token, keyword)
        if ratio > threshold:
            return True
    return False


def identify_entities(tokens):
    identified_product = None
    identified_attribute = None
    identified_value = None

    for product, keywords in products.items():
        for token in tokens:
            if token in keywords or fuzzy_match(token, keywords, 80):
                identified_product = product
                break
        if identified_product:
            break

    for attribute, keywords in attributes.items():
        for token in tokens:
            if token in keywords or fuzzy_match(token, keywords, 80):
                identified_attribute = attribute
                break
        if identified_attribute:
            break

    # Check for values based on attributes
    if identified_attribute == "size":
        value_dict = size_values
    elif identified_attribute == "color":
        value_dict = color_values
    elif identified_attribute == "style":
        value_dict = style_values
    else:
        value_dict = {}

    for value, keywords in value_dict.items():
        for token in tokens:
            if token in keywords or fuzzy_match(token, keywords, 80):
                identified_value = value
                break
        if identified_value:
            break

    return identified_product, identified_attribute, identified_value


def chatbot_response(user_input):
    lemmatizer = WordNetLemmatizer()

    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    tokens = word_tokenize(user_input.lower())

    pos_tags = nltk.pos_tag(tokens)

    lemmatized_tokens = []

    for token, tag in pos_tags:
        if token not in stop_words:
            wordnet_pos = get_wordnet_pos(tag)
            lemma = lemmatizer.lemmatize(token, wordnet_pos)
            lemmatized_tokens.append(lemma)

    for category, keywords in expanded_keywords.items():
        for token in lemmatized_tokens:
            if token in keywords or fuzzy_match(token, keywords):
                return responses[category]

    product, attribute, value = identify_entities(lemmatized_tokens)

    if product:
        if product in product_responses:
            if attribute and value and attribute in product_responses[product] and value in product_responses[product][
                attribute]:
                return product_responses[product][attribute][value]
            elif attribute and attribute in product_responses[product]:
                return product_responses[product][attribute].get("default", product_responses[product]["default"])
            else:
                return product_responses[product]["default"]

    return "I'm not sure about that. Could you ask in a different way?"


while (True):
    print("Do you have any questions?")
    user_question = input()

    response = chatbot_response(user_question)
    if response == "exit":
        break
    print("Chatbot:", response)