from flask import Flask, request, jsonify, render_template
import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet, stopwords
from fuzzywuzzy import fuzz

nltk.download('wordnet', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('punkt', quiet=True)
nltk.download('averaged_perceptron_tagger', quiet=True)


responses = {
    "return": "The product return policy guarantees free refund within 30 days for each item purchased.",
    "deliver": "The company delivers orders free of charge whenever customers spend more than $50. Standard shipping takes 3-5 business days.",
    "discount": "We have seasonal discounts! View our website to find the current offers!",
    "availability": "Please specify the product name so I can check its stock.",
    "price": "Our prices are competitive. I need to know which particular product you want information about.",
    "payment": "The business accepts payment through major credit cards along with PayPal and Apple Pay for customer convenience.",
    "help": "I'm here to help! Feel free to ask about our products, shipping, returns, or anything else.",
    "store": "We have physical stores in major cities and an online store available 24/7.",
    "warranty": "Our products come with a 1-year warranty against manufacturing defects.",
    "exit": "exit",
}

product_responses = {
    "tshirt": {
        "default": "We have a wide range of t-shirts available in various sizes, colors, and materials.",
        "size": {
            "small": "Small t-shirts are available in red, blue, and black.",
            "medium": "Medium t-shirts come in red, blue, black, and white.",
            "large": "Large t-shirts are available in blue and black.",
            "xlarge": "Extra large t-shirts are available in two colors: black and white."
        },
        "color": {
            "red": "Our red t-shirts are popular in both small and medium sizes.",
            "blue": "Blue t-shirts are offered in small, medium, and large sizes.",
            "black": "Black t-shirts are a bestseller and available in all sizes.",
            "white": "White t-shirts are available in medium and extra large sizes."
        },
        "material": {
            "cotton": "Our t-shirts are 100% cotton – soft, and comfortable!",
            "polyester": "We offer polyester t-shirts for a lighter option."
        },
        "price": {
            "default": "Our t-shirts range from $19.99 to $29.99 depending on style and material.",
            "cotton": "Cotton t-shirts are priced at $24.99 each, with discounts for big purchases.",
            "polyester": "Polyester t-shirts are available for $19.99, our most affordable option."
        }
    },
    "jeans": {
        "default": "We offer various jeans in different sizes, styles, and materials.",
        "size": {
            "30": "Size 30 jeans are available in slim and regular fits.",
            "32": "Size 32 jeans come in slim, regular, and relaxed fits.",
            "34": "Size 34 jeans are available in regular and relaxed fits.",
            "36": "Size 36 jeans are offered only in a relaxed fit."
        },
        "style": {
            "slim": "Slim fit jeans are available in sizes 30 and 32.",
            "regular": "Regular fit jeans are available in sizes 30, 32, and 34.",
            "relaxed": "Relaxed fit jeans are available in sizes 32, 34, and 36."
        },
        "material": {
            "denim": "Our jeans are made from high-quality denim, ensuring durability and comfort.",
            "stretch": "Our stretch jeans contain 5% elastane for extra comfort and flexibility."
        },
        "price": {
            "default": "Our jeans range from $39.99 to $59.99 depending on style and material.",
            "slim": "Slim fit jeans are priced at $49.99, offering modern style and comfort.",
            "regular": "Regular fit jeans are available for $44.99, our most popular option.",
            "relaxed": "Relaxed fit jeans are priced at $39.99, perfect for everyday comfort."
        },
        "color": {
            "blue": "Our blue jeans come in various shades from light to dark.",
            "black": "Black jeans are available in all fits.",
            "gray": "Gray jeans are available in slim and regular fits only."
        }
    },
    "jacket": {
        "default": "We offer stylish jackets for all seasons in various designs and materials.",
        "size": {
            "small": "Small jackets fit chest sizes 36-38 inches and are available in most styles.",
            "medium": "Medium jackets fit chest sizes 40-42 inches and are our most popular size.",
            "large": "Large jackets fit chest sizes 44-46 inches and come in all available colors.",
            "xlarge": "XL jackets fit chest sizes 48-50 inches and are available in selected styles."
        },
        "material": {
            "leather": "Our leather jackets are made from premium leather for durability.",
            "denim": "Denim jackets are lightweight and perfect for spring and fall.",
            "cotton": "Cotton jackets offer breathability and comfort for mild weather."
        },
        "style": {
            "bomber": "Bomber jackets feature a ribbed waistband and cuffs with a front zipper closure.",
            "trucker": "Trucker jackets have a classic button front with multiple pockets.",
            "parka": "Parkas are longer with a hood and insulation for colder weather."
        },
        "price": {
            "default": "Our jackets range from $69.99 to $199.99 depending on material and style.",
            "leather": "Leather jackets are our premium option at $199.99.",
            "denim": "Denim jackets are priced affordably at $69.99.",
            "cotton": "Cotton jackets are available for $89.99."
        },
        "color": {
            "black": "Black jackets are available in all materials and styles.",
            "brown": "Brown jackets are available in leather.",
            "blue": "Blue jackets are popular in denim and cotton materials."
        }
    },
    "sweater": {
        "default": "We offer cozy sweaters perfect for layering in colder months.",
        "size": {
            "small": "Small sweaters fit sizes 36-38 and are available in most colors.",
            "medium": "Medium sweaters fit sizes 40-42 and are our best-selling size.",
            "large": "Large sweaters fit sizes 44-46 and offer a comfortable relaxed fit.",
            "xlarge": "XL sweaters fit sizes 48-50 and are available in selected designs."
        },
        "material": {
            "wool": "Our wool sweaters are warm, naturally insulating, and perfect for winter.",
            "cotton": "Cotton sweaters are lightweight and ideal for milder temperatures.",
            "cashmere": "Cashmere sweaters are our luxurious option - incredibly soft and warm."
        },
        "style": {
            "crewneck": "Crewneck sweaters have a round neckline.",
            "v-neck": "V-neck sweaters feature a V-shaped neckline for a more formal appearance.",
            "cardigan": "Cardigans have front buttons and are perfect for versatile layering."
        },
        "price": {
            "default": "Our sweaters range from $39.99 to $129.99 depending on material.",
            "wool": "Wool sweaters are priced at $59.99, offering warmth and durability.",
            "cotton": "Cotton sweaters are our most affordable option at $39.99.",
            "cashmere": "Cashmere sweaters are premium quality at $129.99."
        },
        "color": {
            "gray": "Gray sweaters are versatile and available in all materials.",
            "navy": "Navy sweaters offer a classic color that pairs well with most outfits.",
            "cream": "Cream sweaters have a timeless look and are especially popular in wool and cashmere."
        }
    }
}

expanded_keywords = {
    "return": {"return", "refund", "exchange", "give back", "send back"},
    "deliver": {"deliver", "shipping", "transport", "shipment", "delivery", "ship"},
    "discount": {"discount", "sale", "offer", "deal", "promotion", "coupon"},
    "availability": {"stock", "available", "inventory", "in store"},
    "price": {"price", "cost", "how much", "pricing"},
    "payment": {"payment", "pay", "credit card", "debit card"},
    "help": {"help", "support", "assist", "guidance"},
    "store": {"store", "location", "shop", "physical"},
    "warranty": {"warranty", "guarantee"},
    "exit": {"exit", "quit", "leave", "goodbye", "bye"},
}

products = {
    "tshirt": {"tshirt", "t-shirt", "t shirt", "shirt", "tee"},
    "jeans": {"jeans", "denim", "pants", "trousers"},
    "jacket": {"jacket", "coat", "blazer", "outerwear"},
    "sweater": {"sweater", "jumper", "pullover", "sweatshirt"},
}

attributes = {
    "size": {"size", "fit", "dimension"},
    "color": {"color", "colour", "shade"},
    "style": {"style", "cut", "design"},
    "material": {"material", "fabric", "composition", "cloth"},
    "price": {"price", "cost"},
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
    "red": {"red", "wine", "cherry"},
    "blue": {"blue", "navy", "light blue"},
    "black": {"black", "jet black"},
    "white": {"white", "snow white", "ivory"},
    "gray": {"gray", "grey"},
    "cream": {"cream", "off-white"},
    "brown": {"brown", "chocolate"}
}

style_values = {
    "slim": {"slim", "skinny", "tight"},
    "regular": {"regular", "standard", "normal"},
    "relaxed": {"relaxed", "loose", "comfortable"},
    "bomber": {"bomber", "flight", "aviator"},
    "trucker": {"trucker", "denim jacket", "jean jacket"},
    "parka": {"parka", "hooded", "winter coat"},
    "crewneck": {"crewneck", "round neck"},
    "v-neck": {"v-neck", "v neck", "vneck"},
    "cardigan": {"cardigan", "button up", "open front"}
}

material_values = {
    "cotton": {"cotton", "100% cotton", "pure cotton"},
    "polyester": {"polyester", "poly"},
    "denim": {"denim", "jeans fabric", "jean"},
    "leather": {"leather", "genuine leather"},
    "wool": {"wool", "woolen"},
    "cashmere": {"cashmere", "kashmir"},
    "stretch": {"stretch", "elastic", "elastane", "spandex"}
}


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
