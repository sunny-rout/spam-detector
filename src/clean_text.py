import re
import string
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Download necessary NLTK corpora if not already present.
try:
    nltk.data.find('corpora/wordnet')
except Exception:
    nltk.download('wordnet')
try:
    nltk.data.find('corpora/stopwords')
except Exception:
    nltk.download('stopwords')

def clean_text(text):
    # 1. Convert to lowercase
    text = text.lower()
    # 2. Remove punctuation and numbers
    text = re.sub(r'[%s]' % re.escape(string.punctuation), ' ', text)
    text = re.sub(r'\d+', ' ', text)
    # 3. Tokenize and remove stopwords
    stop_words = set(stopwords.words('english'))
    words = text.split()
    filtered_words = [word for word in words if word not in stop_words]
    # 4. Lemmatization
    lemmatizer = WordNetLemmatizer()
    lemmas = [lemmatizer.lemmatize(word) for word in filtered_words]
    # Rejoin the words into a single string
    return " ".join(lemmas)
