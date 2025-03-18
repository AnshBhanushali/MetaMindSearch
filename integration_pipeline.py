import logging
from webScrapper import WebScrapper
from youtubeScraper import get_youtube_transcript
from dataPreprocessing import clean_text_advanced
from dataVectorizion import FaissVectorIndex

def main():
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.StreamHandler()]
    )
    logger = logging.getLogger(__name__)
    
    # --- Step 1: Scrape Article Content ---
    article_url = "https://en.wikipedia.org/wiki/Machine_learning"
    try:
        logger.info("Scraping article from: %s", article_url)
        # Create a WebScrapper instance and scrape the article
        scraper = WebScrapper()
        article_text = scraper.scrape(article_url)
        logger.info("Article scraped (length: %d characters).", len(article_text))
    except Exception as e:
        logger.error("Error scraping article: %s", e)
        article_text = ""
    
    # --- Step 2: Retrieve YouTube Transcript ---
    video_id = "dQw4w9WgXcQ"  # Example video ID; replace as needed
    transcript_text = get_youtube_transcript(video_id)
    if transcript_text:
        logger.info("Successfully fetched transcript for video ID: %s", video_id)
    else:
        logger.warning("Could not fetch transcript for video ID: %s", video_id)
    
    # --- Step 3: Combine and Clean Documents ---
    documents = []
    if article_text:
        documents.append(article_text)
    if transcript_text:
        documents.append(transcript_text)
    
    if not documents:
        logger.error("No documents available after scraping. Exiting pipeline.")
        return
    
    logger.info("Cleaning documents using advanced cleaning.")
    cleaned_documents = [clean_text_advanced(doc) for doc in documents]
    
    # --- Step 4: Build FAISS Vector Index ---
    try:
        logger.info("Building FAISS vector index.")
        indexer = FaissVectorIndex(model_name='all-MiniLM-L6-v2')
        indexer.build_index(cleaned_documents)
        logger.info("Index built with %d documents.", indexer.index.ntotal)
    except Exception as e:
        logger.error("Error building FAISS index: %s", e)
        return
    
    # --- Step 5: Query the Index ---
    query = input("Enter your search query: ").strip()
    if not query:
        logger.error("No query provided. Exiting.")
        return
    
    try:
        # Use the same advanced cleaning on the query
        distances, indices = indexer.search(query, top_k=3, clean_text_func=clean_text_advanced)
        logger.info("Search completed. Returned indices: %s", indices)
        for idx in indices[0]:
            if idx < len(cleaned_documents):
                logger.info("Match (doc %d): %s", idx, cleaned_documents[idx][:200])
            else:
                logger.warning("Returned index %d is out of range.", idx)
    except Exception as e:
        logger.error("Error during search: %s", e)

if __name__ == '__main__':
    main()
