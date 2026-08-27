from opensearchpy import OpenSearch, helpers
from src.constants import OPENSEARCH_HOST, OPENSEARCH_PORT
import logging
from src.utils import setup_logging
from typing import List, Any, Dict, Tuple
from src.constants import OPENSEARCH_INDEX

# Initialize logger
setup_logging()
logger = logging.getLogger(__name__)

SEARCH_PIPELINE_NAME = "nlp-search-pipeline"

def get_opensearch_client() -> OpenSearch:
    client = OpenSearch(
        hosts=[{"host": OPENSEARCH_HOST, "port": OPENSEARCH_PORT}],
        http_compress=True,
        timeout=30,
        max_retries=3,
        retry_on_timeout=True
    )
    logger.info("OpenSearch client initialized")
    return client


def create_search_pipeline(client: OpenSearch) -> None:
    """Create the hybrid search pipeline if it doesn't exist."""
    pipeline_body = {
        "description": "Hybrid search pipeline for neural + keyword search",
        "phase_results_processors": [
            {
                "normalization-processor": {
                    "normalization": {"technique": "min_max"},
                    "combination": {"technique": "arithmetic_mean", "parameters": {"weights": [0.3, 0.7]}}
                }
            }
        ]
    }
    
    try:
        if not client.transport.perform_request("GET", f"/_search/pipeline/{SEARCH_PIPELINE_NAME}"):
            pass
    except Exception:
        try:
            client.transport.perform_request(
                "PUT", 
                f"/_search/pipeline/{SEARCH_PIPELINE_NAME}", 
                body=pipeline_body
            )
            logger.info(f"Created search pipeline: {SEARCH_PIPELINE_NAME}")
        except Exception as e:
            logger.warning(f"Could not create search pipeline (may not be supported): {e}")


def hybrid_search(query_text: str, query_embedding: List[float], top_k: int=5):
    client = get_opensearch_client()

    # Ensure search pipeline exists
    create_search_pipeline(client)

    query_body = {
        "_source": {"exclude": ["embedding"]},
        "query": {
            "hybrid": {
                "queries": [
                    {"match": {"text": {"query": query_text}}},
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

    try:
        response = client.search(
            index=OPENSEARCH_INDEX, 
            body=query_body, 
            search_pipeline=SEARCH_PIPELINE_NAME
        )
    except Exception as e:
        logger.warning(f"Hybrid search with pipeline failed, falling back to simple search: {e}")
        # Fallback: simple kNN + BM25 without pipeline
        query_body = {
            "_source": {"exclude": ["embedding"]},
            "query": {
                "bool": {
                    "should": [
                        {"match": {"text": {"query": query_text, "boost": 0.3}}},
                        {"knn": {"embedding": {"vector": query_embedding, "k": top_k, "boost": 0.7}}}
                    ]
                }
            },
            "size": top_k,
        }
        response = client.search(index=OPENSEARCH_INDEX, body=query_body)
    
    logger.info(f"Hybrid search completed for query '{query_text}' with top_k={top_k}.")
    hits: List[Dict[str, Any]] = response["hits"]["hits"]
    return hits