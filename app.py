import logging
import streamlit as st
from src.utils import setup_logging
from src.theme import apply_theme, render_sidebar

setup_logging()
logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="Docly - Your Private Local AI Document Assistant",
    page_icon="images/docly_logo.png",
    layout="wide",
    initial_sidebar_state="expanded",
)
# Function to display main content
def display_main_content() -> None:
    """Displays the main welcome content on the page."""
    st.title("Personal Document Assistant 📄🤖")
    st.markdown(
        """
        Welcome to the AI-Powered Document Retrieval Assistant 👋
                
        This app allows you to interact with an AI-powered assistant and upload documents for processing and retrieval.
        
        **Features:**
        - **Chatbot**: Have a conversation with the AI using the latest LLM model.
        - **Document Upload**: Upload PDFs and retrieve data from them using OpenSearch as a Hybrid RAG System.
        
        **Choose a page from the sidebar to begin!**
        """
    )
    logger.info("Displayed main welcome content.")

apply_theme()
render_sidebar()
display_main_content()