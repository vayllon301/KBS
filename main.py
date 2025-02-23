import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import wordnet, stopwords
from fuzzywuzzy import fuzz

nltk.download('wordnet')
nltk.download('stopwords')
nltk.download('punkt')

responses = {
    "return": "You can return anytime within 30 days with all the costs covered",
    "delivery": "We offer free delivery for orders above $50. Standard shipping takes 3-5 business days.",
    "discount": "We have seasonal discounts! Check our website for the latest deals.",
    "availability": "Please specify the product name, and I can check if it's in stock.",
}


def get_synonyms(word):
    synonyms = set()
    for syn in wordnet.synsets(word):
        for lemma in syn.lemmas():
            synonyms.add(lemma.name().lower())
    return synonyms


expanded_keywords = {
    "return": get_synonyms("return"),
    "delivery": get_synonyms("delivery"),
    "discount": get_synonyms("discount") | get_synonyms("sale"),
    "availability": get_synonyms("stock"),
}


def fuzzy_match(token, keywords, threshold=80):

    for keyword in keywords:
        # Use token ratio for similar words
        ratio = fuzz.ratio(token, keyword)
        # Use partial ratio for substring matches
        partial_ratio = fuzz.partial_ratio(token, keyword)
        # Use token sort ratio for words in different order
        token_sort_ratio = fuzz.token_sort_ratio(token, keyword)

        # If any of the ratios exceed the threshold, consider it a match
        if max(ratio, partial_ratio, token_sort_ratio) > threshold:
            return True
    return False


def chatbot_response(user_input):
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    tokens = word_tokenize(user_input.lower())
    tokens = [token for token in tokens if token not in stop_words]

    # Check each category
    for category, keywords in expanded_keywords.items():
        for token in tokens:
            # Check for exact matches first
            if token in keywords:
                return responses[category]
            # If no exact match, try fuzzy matching
            if fuzzy_match(token, keywords):
                return responses[category]

    return "I'm not sure about that. Could you ask in a different way?"


print("Do you have any questions?")
user_question = input()

response = chatbot_response(user_question)
print("Chatbot:", response)
