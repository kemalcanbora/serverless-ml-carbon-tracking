from nltk.stem import WordNetLemmatizer
import re
import nltk

def preprocess(text):
    # Ensure text is a string
    if not isinstance(text, str):
        text = ' '.join(map(str, text))

    text = text.lower()
    # remove all punctuation
    text = re.sub(r'[^\w\s]', '', text)
    lemmatizer = WordNetLemmatizer()
    words = nltk.word_tokenize(text)
    words = [lemmatizer.lemmatize(word) for word in words]
    return  ' '.join(words)

def diets_category_fixed(tag):
    tag = re.sub(r'\([^)]*\)', ' ', tag)
    # remove spaces
    tag = tag.replace("  ", "")
    tag = tag.replace(")", "")
    tag = tag.replace("(", "")
    tag = tag.replace(" ", "-")

    # make all lowercase
    tag = tag.lower()
    return tag