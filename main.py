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

responses = {
    "return": "You can return anytime within 30 days with all the costs covered",
    "deliver": "We offer free delivery for orders above $50. Standard shipping takes 3-5 business days.",
    "discount": "We have seasonal discounts! Check our website for the latest deals.",
    "availability": "Please specify the product name, and I can check if it's in stock.",
    "exit": "exit",
}


def get_wordnet_pos(tag):

    tag_dict = {
        'J': wordnet.ADJ,
        'N': wordnet.NOUN,
        'V': wordnet.VERB,
        'R': wordnet.ADV
    }
    return tag_dict.get(tag[0].upper(), wordnet.NOUN)


expanded_keywords = {
    "return": {"return", "refund", "exchange", "give back", "send back"},
    "deliver": {"deliver", "shipping", "transport", "shipment", "deliver"},
    "discount": {"discount", "sale", "offer", "deal", "promotion", "coupon"},
    "availability": {"stock", "available", "inventory", "in store"},
    "exit": {"exit", "quit", "leave"},
}


def fuzzy_match(token, keywords, threshold=90):
    for keyword in keywords:
        ratio = fuzz.ratio(token, keyword)
        if  ratio > threshold:
            return True
    return False


def chatbot_response(user_input):

    lemmatizer = WordNetLemmatizer()

    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    tokens = word_tokenize(user_input.lower())


    pos_tags = nltk.pos_tag(tokens)

    lemmatized_tokens = []

    for token, tag in pos_tags:
        if token not in stop_words:
            # Convert POS tag to format accepted by WordNet lemmatizer
            wordnet_pos = get_wordnet_pos(tag)
            # Lemmatize the token
            lemma = lemmatizer.lemmatize(token, wordnet_pos)
            lemmatized_tokens.append(lemma)


    for category, keywords in expanded_keywords.items():
        for token in lemmatized_tokens:

            if token in keywords:
                return responses[category]

            if fuzzy_match(token, keywords):
                return responses[category]

    return "I'm not sure about that. Could you ask in a different way?"


while(True):
    print("Do you have any questions?")
    user_question = input()

    response = chatbot_response(user_question)
    if response == "exit":
        break
    print("Chatbot:", response)

