from opensearchpy import OpenSearch, helpers
from src.constants import OPENSEARCH_HOST, OPENSEARCH_PORT
import logging
from src.utils import setup_logging
from typing import List, Any, Dict, Tuple
from src.constants import OPENSEARCH_INDEX

# Initialize logger
setup_logging()
logger = logging.getLogger(__name__)

def get_opensearch_client() -> OpenSearch:
    client = OpenSearch(
        hosts=[{"host": OPENSEARCH_HOST, "port": OPENSEARCH_PORT}],
        http_compress = True,
        timeout = 30,
        max_retries = 3,
        retry_on_timeout = True
    )
    logger.info("OpenSearch client initialized")
    return client


def hybrid_search(query_text: str, query_embedding: List[float], top_k: int=5):
    client = get_opensearch_client()

    query_body = {
        "_source": {"exclude": ["embedding"]},  # Exclude embeddings from the results
        "query": {
            "hybrid": {
                "queries": [
                    {"match": {"text": {"query": query_text}}},  # Text-based search
                    {
                        "knn": {
                            "embedding": {
                                "vector": query_embedding,
                                "k": top_k,
                            }
                        }
                    },
                ]
            }
        },
        "size": top_k,
    }

    response = client.search(
        index=OPENSEARCH_INDEX, 
        body=query_body, 
        search_pipeline="nlp-search-pipeline"
    )
    logger.info(f"Hybrid search completed for query '{query_text}' with top_k={top_k}.")

    # Type casting for compatibility with expected return type
    hits: List[Dict[str, Any]] = response["hits"]["hits"]
    return hits