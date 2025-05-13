from flask import Flask, request, jsonify, render_template
import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet, stopwords
from fuzzywuzzy import fuzz
import json
import os

def ensure_nltk_resources():
    resources = ['wordnet', 'stopwords', 'punkt', 'averaged_perceptron_tagger']
    for resource in resources:
        try:
            nltk.data.find(f'tokenizers/{resource}')
        except LookupError:
            nltk.download(resource, quiet=True)

ensure_nltk_resources()

def load_data():
    
    with open("data.json", 'r') as f:
        return json.load(f)

data = load_data()
responses = data["responses"]
product_responses = data["product_responses"]
expanded_keywords = data["expanded_keywords"]
products = data["products"]
attributes = data["attributes"]
attribute_value_maps = {
    "size": data["size_values"],
    "color": data["color_values"],
    "style": data["style_values"],
    "material": data["material_values"]
}

def fuzzy_match(token, keywords, threshold=80):
    return any(fuzz.ratio(token, keyword) > threshold for keyword in keywords)

def extract_attribute_value(tokens, attr_name):
    if attr_name not in attribute_value_maps:
        return None

    value_dict = attribute_value_maps[attr_name]
    for val, val_keywords in value_dict.items():
        if any(token in val_keywords or fuzzy_match(token, val_keywords, 75) for token in tokens):
            return val
    return None

def identify_product_and_attributes(tokens):
 
    identified_product = None
    for product, keywords in products.items():
        if any(token in keywords or fuzzy_match(token, keywords, 75) for token in tokens):
            identified_product = product
            break

    recognized_attributes = {}
    for attr_name in attributes:
        if any(token in attributes[attr_name] or fuzzy_match(token, attributes[attr_name], 75)
               for token in tokens):
            recognized_attributes[attr_name] = extract_attribute_value(tokens, attr_name)

    if identified_product:
        for attr_name in attribute_value_maps:
            if attr_name not in recognized_attributes:
                value = extract_attribute_value(tokens, attr_name)
                if value:
                    recognized_attributes[attr_name] = value

    return identified_product, recognized_attributes

def preprocess_text(user_input):
    lemmatizer = WordNetLemmatizer()
    stop_words = set(stopwords.words('english'))
    tokens = word_tokenize(user_input.lower())
    pos_tags = nltk.pos_tag(tokens)

    processed_tokens = []
    for token, tag in pos_tags:
        if token not in stop_words:
            wordnet_pos = get_wordnet_pos(tag)
            lemma = lemmatizer.lemmatize(token, wordnet_pos)
            processed_tokens.append(lemma)

    return processed_tokens

def get_wordnet_pos(tag):
    tag_dict = {'J': wordnet.ADJ, 'N': wordnet.NOUN, 'V': wordnet.VERB, 'R': wordnet.ADV}
    return tag_dict.get(tag[0].upper(), wordnet.NOUN)

def chatbot_response(user_input):
    tokens = preprocess_text(user_input)

    for category, keywords in expanded_keywords.items():
        if any(token in keywords or fuzzy_match(token, keywords) for token in tokens):
            return responses[category]

    product, recognized_attrs = identify_product_and_attributes(tokens)
    if product:
        if not recognized_attrs:
            return product_responses[product]["default"]

        detailed_responses = []
        for attr, val in recognized_attrs.items():
            if attr in product_responses[product]:
                attr_dict = product_responses[product][attr]
                if val and val in attr_dict:
                    detailed_responses.append(attr_dict[val])
                elif "default" in attr_dict:
                    detailed_responses.append(attr_dict["default"])

        if detailed_responses:
            return "\n".join(detailed_responses)
        return product_responses[product]["default"]

    return "I'm not sure about that. Could you ask in a different way?"

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message', '').strip()
    if not user_message:
        return jsonify({'response': 'Please enter a message.'})
    response_text = chatbot_response(user_message)
    return jsonify({'response': response_text})

if __name__ == '__main__':
    app.run(debug=True)
