from flask import Flask, request, jsonify, render_template
import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet, stopwords
from fuzzywuzzy import fuzz
import json

nltk.download('wordnet', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('punkt', quiet=True)
nltk.download('averaged_perceptron_tagger', quiet=True)

data = json.load(open("data.json"))

responses = data["responses"]

product_responses = data["product_responses"]

expanded_keywords = data["expanded_keywords"]

products =  data["products"]

attributes = data["attributes"]

size_values = data["size_values"]

color_values = data["color_values"]

style_values = data["style_values"]

material_values = data["material_values"]

def fuzzy_match(token, keywords, threshold=80):
    for keyword in keywords:
        if fuzz.ratio(token, keyword) > threshold:
            return True
    return False

def identify_product_and_attributes(tokens):
    identified_product = None
    recognized_attributes = {}
    for product, keywords in products.items():
        for token in tokens:
            if token in keywords or fuzzy_match(token, keywords, 75):
                identified_product = product
                break
        if identified_product:
            break
    for attr, attr_keywords in attributes.items():
        for token in tokens:
            if token in attr_keywords or fuzzy_match(token, attr_keywords, 75):
                value = None
                if attr == "size":
                    value_dict = size_values
                elif attr == "color":
                    value_dict = color_values
                elif attr == "style":
                    value_dict = style_values
                elif attr == "material":
                    value_dict = material_values
                else:
                    value_dict = {}
                for val, val_keywords in value_dict.items():
                    for token2 in tokens:
                        if token2 in val_keywords or fuzzy_match(token2, val_keywords, 75):
                            value = val
                            break
                    if value:
                        break
                recognized_attributes[attr] = value
                break
    if identified_product:
        for token in tokens:
            for attr_name, value_dict in [("size", size_values),
                                          ("color", color_values),
                                          ("style", style_values),
                                          ("material", material_values)]:
                for val, val_keywords in value_dict.items():
                    if token in val_keywords or fuzzy_match(token, val_keywords, 80):
                        recognized_attributes[attr_name] = val
                        break
    return identified_product, recognized_attributes

def get_wordnet_pos(tag):
    tag_dict = {'J': wordnet.ADJ, 'N': wordnet.NOUN, 'V': wordnet.VERB, 'R': wordnet.ADV}
    return tag_dict.get(tag[0].upper(), wordnet.NOUN)

def chatbot_response(user_input):
    lemmatizer = WordNetLemmatizer()
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
    product, recognized_attrs = identify_product_and_attributes(lemmatized_tokens)
    if product:
        detailed_responses = []
        if not recognized_attrs:
            return product_responses[product]["default"]
        for attr, val in recognized_attrs.items():
            if attr in product_responses[product]:
                if val and val in product_responses[product][attr]:
                    detailed_responses.append(product_responses[product][attr][val])
                elif not val and "default" in product_responses[product][attr]:
                    detailed_responses.append(product_responses[product][attr]["default"])
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
    user_message = data.get('message', '')
    if user_message.strip() == '':
        return jsonify({'response': 'Please enter a message.'})
    response_text = chatbot_response(user_message)
    return jsonify({'response': response_text})

if __name__ == '__main__':
    app.run(debug=True)
