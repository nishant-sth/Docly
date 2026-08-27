import logging
import os
import streamlit as st

from src.llm import (
    ensure_model_pulled,
    generate_response_streaming,
    get_embedding_model,
)
from src.ingestion import create_index, get_opensearch_client
from src.constants import OLLAMA_MODEL_NAME, OPENSEARCH_INDEX
from src.utils import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

def render_chatbot_page():
    st.title("Chat")
    st.markdown('<p style="color: var(--text-muted); margin-top: -0.5rem; margin-bottom: 1.5rem;">Ask questions about your uploaded documents</p>', unsafe_allow_html=True)

    if "use_hybrid_search" not in st.session_state:
        st.session_state["use_hybrid_search"] = True
    if "num_results" not in st.session_state:
        st.session_state["num_results"] = 5
    if "temperature" not in st.session_state:
        st.session_state["temperature"] = 0.7
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    with st.expander("⚙️ Settings", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.session_state["use_hybrid_search"] = st.checkbox(
                "Enable RAG (Document Search)",
                value=st.session_state["use_hybrid_search"],
                help="Search uploaded documents for relevant context"
            )
        with col2:
            st.session_state["num_results"] = st.number_input(
                "Context Results",
                min_value=1,
                max_value=10,
                value=st.session_state["num_results"],
                step=1,
                help="Number of document chunks to include as context"
            )
        with col3:
            st.session_state["temperature"] = st.slider(
                "Temperature",
                min_value=0.0,
                max_value=1.0,
                value=st.session_state["temperature"],
                step=0.1,
                help="Higher = more creative, Lower = more focused"
            )
        
        if st.session_state["chat_history"]:
            if st.button("Clear Conversation", type="secondary", use_container_width=True):
                st.session_state["chat_history"] = []
                st.rerun()

    if "embedding_models_loaded" not in st.session_state:
        with st.spinner("Loading models..."):
            get_embedding_model()
            ensure_model_pulled(OLLAMA_MODEL_NAME)
            st.session_state["embedding_models_loaded"] = True
        logger.info("Models loaded.")

    try:
        client = get_opensearch_client()
        create_index(client)
    except Exception as e:
        logger.error(f"Failed to connect to OpenSearch: {e}")
        st.error("Cannot connect to OpenSearch. Please ensure OpenSearch is running on localhost:9200.")
        st.stop()

    for message in st.session_state["chat_history"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask a question..."):
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Use history WITHOUT the current prompt for context
        history_for_context = st.session_state["chat_history"][-10:]
        st.session_state["chat_history"].append({"role": "user", "content": prompt})
        logger.info("User input received.")

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response_placeholder = st.empty()
                response_text = ""

                response_stream = generate_response_streaming(
                    prompt,
                    use_hybrid_search=st.session_state["use_hybrid_search"],
                    num_results=st.session_state["num_results"],
                    temperature=st.session_state["temperature"],
                    chat_history=history_for_context,
                )

            if response_stream is not None:
                for chunk in response_stream:
                    if (
                        isinstance(chunk, dict)
                        and "message" in chunk
                        and "content" in chunk["message"]
                    ):
                        response_text += chunk["message"]["content"]
                        response_placeholder.markdown(response_text + "▌")
                    else:
                        logger.error("Unexpected chunk format in response stream.")
            else:
                response_text = "Error: Failed to generate response. Please check if Ollama is running and the model is available."
                logger.error("Response stream is None - generation failed")
            
            response_placeholder.markdown(response_text)
            st.session_state["chat_history"].append(
                {"role": "assistant", "content": response_text}
            )
            logger.info("Response generated and displayed.")

render_chatbot_page()