from src.utils import setup_logging
import logging
import streamlit as st
from sentence_transformers import SentenceTransformer
from src.constants import EMBEDDING_MODEL_PATH
from typing import List, Dict, Tuple
import numpy as np

setup_logging()
logger = logging.getLogger(__name__)

@st.cache_resource(show_spinner=False)
def get_embedding_model() -> SentenceTransformer:
    logger.info(f"Loading embedding models form path: {EMBEDDING_MODEL_PATH}")
    return SentenceTransformer(EMBEDDING_MODEL_PATH)

def generate_embeddings(chunks: List[str]):
    model = get_embedding_model()
    embeddings = [np.array(model.encode(chunk)) for chunk in chunks]
    logger.info(f"Generated embeddings for {len(chunks)} text chunks.")
    return embeddings