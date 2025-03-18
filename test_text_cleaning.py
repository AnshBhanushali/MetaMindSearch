import pytest
from dataPreprocessing import load_spacy_model, clean_text_advanced


def test_load_spacy_model():
    """Test that the spaCy model loads successfully."""
    nlp = load_spacy_model("en_core_web_sm")
    # Check that the model has a meta attribute (indicative of a proper spaCy model)
    assert hasattr(nlp, "meta"), "The loaded model should have a meta attribute."

def test_clean_text_advanced_basic():
    """
    Test basic cleaning:
    - Lowercasing
    - URL and HTML removal
    - Punctuation removal
    - Whitespace normalization
    """
    input_text = (
        "This is a SAMPLE text! Visit http://example.com for more info. "
        "<br> Amazing, isn't it?"
    )
    # Disable stopword removal and lemmatization to check basic cleaning
    cleaned = clean_text_advanced(input_text, remove_stopwords=False, lemmatize=False)
    # Since spaCy tokenization may slightly vary, check that key words are present
    for word in ["sample", "text", "visit", "more", "info", "amazing"]:
        assert word in cleaned, f"Expected word '{word}' in cleaned text."
    # Ensure punctuation is removed
    for punct in ["!", "?", "'", "<", ">", "/"]:
        assert punct not in cleaned

def test_clean_text_advanced_stopword_removal():
    """
    Test that stopwords are removed when remove_stopwords is True.
    """
    input_text = "This is a sample sentence with some stopwords."
    cleaned = clean_text_advanced(input_text, remove_stopwords=True, lemmatize=False)
    tokens = cleaned.split()  
    for stopword in ["this", "is", "a", "with", "some"]:
        assert stopword not in tokens, f"Stopword '{stopword}' should be removed."


def test_clean_text_advanced_lemmatization():
    """
    Test that lemmatization works (e.g., 'running' becomes 'run').
    """
    input_text = "He was running and eating at the same time."
    cleaned = clean_text_advanced(input_text, remove_stopwords=False, lemmatize=True)
    # Check that the lemma for "running" and "eating" appear in the cleaned text.
    assert "run" in cleaned, "Expected 'run' in cleaned text (from 'running')."
    assert "eat" in cleaned, "Expected 'eat' in cleaned text (from 'eating')."

def test_clean_text_non_string_input():
    """
    Test that passing non-string input raises a ValueError.
    """
    with pytest.raises(ValueError):
        clean_text_advanced(12345)
