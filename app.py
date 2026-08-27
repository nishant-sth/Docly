import logging
import streamlit as st
from src.utils import setup_logging
from src.theme import apply_theme, render_sidebar

setup_logging()

st.set_page_config(
    page_title="Docly - Your Private Local AI Document Assistant",
    page_icon="images/docly_logo.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_theme()
render_sidebar()

# Define pages with custom labels and icons
chat_page = st.Page("pages/chatbot.py", title="Chat", icon="💬")
upload_page = st.Page("pages/upload_document.py", title="Upload Documents", icon="📤")

pg = st.navigation([chat_page, upload_page])
pg.run()