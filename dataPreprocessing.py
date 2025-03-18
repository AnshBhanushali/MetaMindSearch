import re
import string
import logging
import spacy
from spacy.lang.en.stop_words import STOP_WORDS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def load_spacy_model(model_name="en_core_web_sm"):
    """
    Loads a spaCy language model.
    Raises an informative error if the model is not installed.
    """
    try:
        nlp = spacy.load(model_name)
        logger.info(f"Loaded spaCy model: {model_name}")
        return nlp
    except Exception as e:
        error_msg = (f"Error loading spaCy model '{model_name}': {e}. "
                     "Please install it by running: python -m spacy download en_core_web_sm")
        logger.error(error_msg)
        raise RuntimeError(error_msg)

# Load the spaCy model (this can be done once at the start)
nlp = load_spacy_model()

def clean_text_advanced(text, remove_stopwords=True, lemmatize=True):
    """
    Performs advanced text cleaning using regular expressions and spaCy.
    
    Parameters:
        text (str): The text to clean.
        remove_stopwords (bool): Whether to remove stopwords.
        lemmatize (bool): Whether to lemmatize tokens.
        
    Returns:
        str: The cleaned text.
    """
    if not isinstance(text, str):
        logger.error("Input text must be a string.")
        raise ValueError("Input text must be a string.")

    text = text.lower()
    # Remove URLs
    text = re.sub(r'http\S+|www\S+', '', text)
    # Remove HTML tags
    text = re.sub(r'<.*?>', '', text)
    # Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Use spaCy to process text (tokenization, lemmatization, etc.)
    doc = nlp(text)
    tokens = []
    for token in doc:
        # Optionally skip stopwords and non-alphanumeric tokens
        if remove_stopwords and token.text in STOP_WORDS:
            continue
        if token.is_space or token.is_punct:
            continue
        # Choose lemma or original form
        token_text = token.lemma_ if lemmatize else token.text
        tokens.append(token_text)
    
    cleaned_text = " ".join(tokens)
    return cleaned_text