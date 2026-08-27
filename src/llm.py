import streamlit as st 
from src.constants import OLLAMA_MODEL_NAME, ASSYMETRIC_EMBEDDING
import ollama
import logging
from src.utils import setup_logging
from typing import List, Dict, Optional, Iterable
from src.embeddings import get_embedding_model
from src.opensearch import hybrid_search
from src.utils import setup_logging

# setup logger
setup_logging
logger = logging.getLogger(__name__)


@st.cache_resource(show_spinner=False)
def ensure_model_pulled(model: str) -> bool:
    
    try:
        available_models = ollama.list(model)
        if model not in available_models:
            logger.info(f"Model {model} not found locally. Pulling the model...")
            ollama.pull(model)
            logger.info(f"Model {model} has been pulled and is now available locally.")
        else:
            logger.info(f"Model {model} is already available locally.")
    except ollama.ResponseError as e:
        logger.error(f"Error checking or pulling model: {e.error}")
        return False
    return True


def run_llama_streaming(prompt, temperature):
    try:
        logger.info("Streaming response from Llama Model")
        stream = ollama.chat(
            model=OLLAMA_MODEL_NAME,
            messages=[{
                "role": "user", 
                "content": prompt
                }],
            stream=True,
            options={
                "temperature": temperature
                },
        )
    except ollama.ResponseError as e:
        logger.error(f"Error during streaming: {e.error}")
        return None
    return stream


def prompt_template(query: str, context: str, history: List[Dict[str, str]]):
    """Builds the prompt with the content, conversation history and query.

    Args:
        query (str): The user's query
        context (str): Context texts from the hybrid search
        history (List[Dict[str, str]]): Past conversation history of the user
    """
    
    prompt = "You are a knowledgeable chatbot assistant"
    if context:
        prompt += ("Use the following context to answer the user's questions. \n Context:" + {context}+ "\n")
    else:
        prompt += "Answer the question with best of your knowledge. \n"
        
    if history:
        prompt += "Conversation History:\n"
        for msg in history:
            role = "User" if msg["role"] == "user" else "Assistant"
            content = msg["content"]
            prompt += f"{role}: {content}\n"
        prompt += "\n"

    prompt += f"User: {query}\nAssistant:"
    logger.info("Prompt constructed with context and conversation history.")
    return prompt


def generate_response_streaming(
    query: str,
    use_hybrid_search: bool,
    num_results: int,
    temperature: float,
    chat_history: Optional[List[Dict[str, str]]] = None,
    ) -> Optional[Iterable[str]]:
    """
    Generates a chatbot response by performing hybrid search and incorporating conversation history.

    Args:
        query (str): The user's query.
        use_hybrid_search (bool): Whether to use hybrid search for context.
        num_results (int): The number of search results to include in the context.
        temperature (float): The temperature for the response generation.
        chat_history (Optional[List[Dict[str, str]]]): List of chat history messages.

    Returns:
        Optional[Iterable[str]]: A generator yielding response chunks as strings, or None if an error occurs.
    """
    chat_history = chat_history or []
    max_history_messages = 10
    history = chat_history[-max_history_messages:]
    context = ""

    # Include hybrid search results if enabled
    if use_hybrid_search:
        logger.info("Performing hybrid search.")
        if ASSYMETRIC_EMBEDDING:
            prefixed_query = f"passage: {query}"
        else:
            prefixed_query = f"{query}"
            
        embedding_model = get_embedding_model()
        
        query_embedding = embedding_model.encode(prefixed_query).tolist()  # Convert tensor to list of floats
        search_results = hybrid_search(query, query_embedding, top_k=num_results)
        logger.info("Hybrid search completed.")

        # Collect text from search results
        for i, result in enumerate(search_results):
            context += f"Document {i}:\n{result['_source']['text']}\n\n"

    # Generate prompt using the prompt_template function
    prompt = prompt_template(query, context, history)

    return run_llama_streaming(prompt, temperature)