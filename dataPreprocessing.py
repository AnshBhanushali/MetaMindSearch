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