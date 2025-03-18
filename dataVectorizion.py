import logging
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.StreamHandler()]
    )
    return logging.getLogger(__name__)

logger = setup_logging()

class FaissVectorIndex:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        """
        Initialize the vector indexer by loading a pre-trained SentenceTransformer model.
        """
        try:
            logger.info("Loading SentenceTransformer model: %s", model_name)
            self.model = SentenceTransformer(model_name)
        except Exception as e:
            logger.error("Failed to load model '%s': %s", model_name, e)
            raise
        self.index = None
        self.documents = None
        self.embeddings = None

    def build_index(self, documents):
        """
        Computes embeddings for a list of documents and builds a FAISS index.
        """
        if not documents:
            raise ValueError("The documents list is empty. Cannot build an index.")
        try:
            logger.info("Encoding %d documents", len(documents))
            embeddings = self.model.encode(documents, convert_to_numpy=True)
            dimension = embeddings.shape[1]
            logger.info("Embedding dimension: %d", dimension)
            # Create a FAISS index using L2 distance
            self.index = faiss.IndexFlatL2(dimension)
            self.index.add(embeddings)
            self.documents = documents
            self.embeddings = embeddings
            logger.info("Index built with %d documents", self.index.ntotal)
            return self.index
        except Exception as e:
            logger.error("Failed to build index: %s", e)
            raise

    def search(self, query, top_k=5, clean_text_func=None):
        """
        Searches the FAISS index for documents similar to the query.
        """
        if self.index is None:
            raise ValueError("Index has not been built. Call build_index(documents) first.")
        
        if clean_text_func is not None:
            try:
                query = clean_text_func(query)
            except Exception as e:
                logger.warning("Query cleaning failed; proceeding with the original query. Error: %s", e)
        
        try:
            logger.info("Encoding query: %s", query)
            query_embedding = self.model.encode([query], convert_to_numpy=True)
            distances, indices = self.index.search(query_embedding, top_k)
            logger.info("Search complete. Top %d indices: %s", top_k, indices)
            return distances, indices
        except Exception as e:
            logger.error("Search failed: %s", e)
            raise

def clean_text(text):
    import re, string
    # Lowercase the text
    text = text.lower()
    # Remove URLs
    text = re.sub(r'http\S+|www\S+', '', text)
    # Remove HTML tags
    text = re.sub(r'<.*?>', '', text)
    # Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

if __name__ == '__main__':
    # Example: Combining cleaned articles and transcripts from your pipeline.
    cleaned_articles = {
        "article1": "machine learning is transforming the world of technology",
        "article2": "deep learning is a subset of machine learning"
    }
    cleaned_transcripts = {
        "vid1": "advances in artificial intelligence and machine learning",
        "vid2": "latest research in neural networks and deep learning"
    }
    
    # Prepare the list of documents for indexing.
    documents = list(cleaned_articles.values()) + list(cleaned_transcripts.values())
    
    # Initialize and build the index.
    indexer = FaissVectorIndex(model_name='all-MiniLM-L6-v2')
    indexer.build_index(documents)
    
    # Define a sample query.
    query = "Latest advances in machine learning"
    
    # Perform a search (cleaning the query text with our clean_text function).
    distances, indices = indexer.search(query, top_k=3, clean_text_func=clean_text)
    
    # Log search results.
    logger.info("Search results (indices): %s", indices)
    for idx in indices[0]:
        if idx < len(documents):
            logger.info("Document: %s", documents[idx])
