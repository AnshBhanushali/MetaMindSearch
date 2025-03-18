import numpy as np
import pytest

# Import the production class and functions from your module
from dataVectorizion import FaissVectorIndex, clean_text

# --- Dummy Model for Testing ---
def dummy_encode(texts, convert_to_numpy=True):
    """
    Dummy encode function that produces embeddings of dimension 2.
    Each embedding is simply [len(text), len(text)].
    """
    return np.array([[len(text), len(text)] for text in texts], dtype=np.float32)

class DummyModel:
    def encode(self, texts, convert_to_numpy=True):
        return dummy_encode(texts, convert_to_numpy=convert_to_numpy)

# --- Pytest Fixture for FaissVectorIndex Instance ---
@pytest.fixture
def vector_indexer(monkeypatch):
    # Update the monkeypatch target to match your module name: "dataVectorizion"
    monkeypatch.setattr("dataVectorizion.SentenceTransformer", lambda model_name: DummyModel())
    # Now create the indexer; our model will be our DummyModel.
    indexer = FaissVectorIndex(model_name="dummy")
    # Ensure that the model is our dummy model.
    indexer.model = DummyModel()
    return indexer

# --- Test Cases ---

def test_build_index(vector_indexer):
    """
    Test that the FAISS index builds correctly given a list of documents.
    """
    documents = ["doc one", "doc two", "another document"]
    index = vector_indexer.build_index(documents)
    assert index.ntotal == len(documents), "Index should contain as many vectors as documents."

def test_search(vector_indexer):
    """
    Test that searching the built index returns valid indices.
    """
    documents = ["doc one", "doc two", "another document"]
    vector_indexer.build_index(documents)
    
    # Search for a query; our dummy encode returns vectors based solely on text length.
    distances, indices = vector_indexer.search("doc one", top_k=2)
    
    # Ensure that indices returned are within the valid range.
    for idx in indices[0]:
        assert 0 <= idx < len(documents), f"Returned index {idx} is out of bounds."

def test_search_without_index(vector_indexer):
    """
    Test that calling search without building an index raises an error.
    """
    with pytest.raises(ValueError):
        vector_indexer.search("doc one")

def test_search_with_cleaning(vector_indexer):
    """
    Test that providing a custom cleaning function to search works.
    """
    documents = ["Hello world", "Goodbye world"]
    vector_indexer.build_index(documents)
    
    # Define a simple cleaning function that lowercases the query.
    cleaning_func = lambda x: x.lower()
    distances, indices = vector_indexer.search("HELLO WORLD", top_k=1, clean_text_func=cleaning_func)
    
    # Check that the indices are valid.
    for idx in indices[0]:
        assert 0 <= idx < len(documents), f"Returned index {idx} is out of bounds."

def test_clean_text_function():
    """
    Test that the provided clean_text function cleans text as expected.
    """
    input_text = "Visit http://example.com! <br> It's Amazing."
    cleaned = clean_text(input_text)
    # Check that the text is lowercased and that URL, HTML tags, and punctuation are removed.
    assert "http" not in cleaned
    assert "<" not in cleaned and ">" not in cleaned
    assert "!" not in cleaned
    # Basic check for lowercasing.
    assert cleaned == cleaned.lower()
