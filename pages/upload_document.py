import logging
import os
import time
import streamlit as st
from PyPDF2 import PdfReader

from src.constants import OPENSEARCH_INDEX, TEXT_CHUNK_SIZE
from src.embeddings import generate_embeddings, get_embedding_model
from src.ingestion import (
    bulk_index_documents,
    create_index,
    delete_documents_by_document_name,
)
from src.opensearch import get_opensearch_client
from src.utils import chunk_text, setup_logging

setup_logging()
logger = logging.getLogger(__name__)

def save_uploaded_file(uploaded_file) -> str:
    UPLOAD_DIR = "uploaded_files"
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    logger.info(f"File '{uploaded_file.name}' saved to '{file_path}'.")
    return file_path

def load_documents_from_index():
    UPLOAD_DIR = "uploaded_files"
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    
    try:
        client = get_opensearch_client()
        create_index(client)
    except Exception as e:
        logger.error(f"Failed to connect to OpenSearch: {e}")
        st.error("Cannot connect to OpenSearch. Please ensure OpenSearch is running on localhost:9200.")
        return []
    
    try:
        query = {
            "size": 0,
            "aggs": {"unique_docs": {"terms": {"field": "document_name", "size": 10000}}},
        }
        response = client.search(index=OPENSEARCH_INDEX, body=query)
        buckets = response["aggregations"]["unique_docs"]["buckets"]
        document_names = [bucket["key"] for bucket in buckets]
    except Exception as e:
        logger.error(f"Failed to query OpenSearch: {e}")
        st.error("Failed to load documents from OpenSearch.")
        return []
    
    documents = []
    for document_name in document_names:
        file_path = os.path.join(UPLOAD_DIR, document_name)
        if os.path.exists(file_path):
            reader = PdfReader(file_path)
            text = "".join([page.extract_text() for page in reader.pages])
            documents.append({"filename": document_name, "content": text, "file_path": file_path})
        else:
            documents.append({"filename": document_name, "content": "", "file_path": None})
            logger.warning(f"File '{document_name}' does not exist locally.")
    
    return documents

def render_upload_page():
    st.title("Upload Documents")
    st.markdown('<p style="color: var(--text-muted); margin-top: -0.5rem; margin-bottom: 1.5rem;">Add PDF documents to your knowledge base for AI-powered Q&A</p>', unsafe_allow_html=True)

    if "embedding_models_loaded" not in st.session_state:
        with st.spinner("Loading embedding model..."):
            get_embedding_model()
            st.session_state["embedding_models_loaded"] = True
        logger.info("Embedding model loaded.")

    if "documents" not in st.session_state:
        with st.spinner("Loading documents..."):
            st.session_state["documents"] = load_documents_from_index()
        st.session_state["doc_count"] = len(st.session_state["documents"])

    if "deleted_file" in st.session_state:
        st.markdown(f'<div class="toast-success">The file <strong>{st.session_state["deleted_file"]}</strong> was successfully deleted.</div>', unsafe_allow_html=True)
        del st.session_state["deleted_file"]

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-header"><span class="card-title">Add New Documents</span></div>', unsafe_allow_html=True)
    
    uploaded_files = st.file_uploader(
        "Drag and drop PDF files here, or click to browse",
        type="pdf",
        accept_multiple_files=True,
        label_visibility="collapsed"
    )

    if uploaded_files:
        existing_names = {doc["filename"] for doc in st.session_state["documents"]}
        new_files = [f for f in uploaded_files if f.name not in existing_names]
        duplicate_files = [f for f in uploaded_files if f.name in existing_names]
        
        for dup in duplicate_files:
            st.markdown(f'<div class="toast-warning">File <strong>{dup.name}</strong> already exists in the index.</div>', unsafe_allow_html=True)
        
        if new_files:
            try:
                client = get_opensearch_client()
            except Exception as e:
                logger.error(f"Failed to connect to OpenSearch: {e}")
                st.error("Cannot connect to OpenSearch. Please ensure OpenSearch is running on localhost:9200.")
                st.stop()
            
            with st.spinner("Uploading and indexing documents..."):
                for uploaded_file in new_files:
                    file_path = save_uploaded_file(uploaded_file)
                    reader = PdfReader(file_path)
                    text = "".join([page.extract_text() for page in reader.pages])
                    chunks = chunk_text(text, chunk_size=TEXT_CHUNK_SIZE, overlap=100)
                    embeddings = generate_embeddings(chunks)

                    documents_to_index = [
                        {
                            "doc_id": f"{uploaded_file.name}_{i}",
                            "text": chunk,
                            "embedding": embedding,
                            "document_name": uploaded_file.name,
                        }
                        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings))
                    ]
                    bulk_index_documents(documents_to_index, client)
                    st.session_state["documents"].append({
                        "filename": uploaded_file.name,
                        "content": text,
                        "file_path": file_path,
                    })
                    logger.info(f"File '{uploaded_file.name}' uploaded and indexed.")
                
                st.session_state["doc_count"] = len(st.session_state["documents"])
            
            st.markdown(f'<div class="toast-success">Successfully uploaded and indexed {len(new_files)} document(s)!</div>', unsafe_allow_html=True)
            time.sleep(0.5)
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state["documents"]:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(f'<div class="card-header"><span class="card-title">Your Documents</span><span class="stat-badge">{len(st.session_state["documents"])} documents</span></div>', unsafe_allow_html=True)
        
        for idx, doc in enumerate(st.session_state["documents"]):
            char_count = len(doc['content'])
            with st.container():
                col1, col2 = st.columns([5, 1])
                with col1:
                    st.markdown(f"""
                    <div style="display: flex; align-items: center; gap: 0.75rem; padding: 0.75rem 0;">
                        <div style="width: 40px; height: 40px; border-radius: 8px; background: var(--primary-light); display: flex; align-items: center; justify-content: center; color: var(--primary); font-weight: 600;">📄</div>
                        <div>
                            <div style="font-weight: 500; color: var(--text);">{doc['filename']}</div>
                            <div style="font-size: 0.8rem; color: var(--text-muted);">{char_count:,} characters • {len(doc['content'].split()) if doc['content'] else 0:,} words</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    if st.button("Delete", key=f"delete_{doc['filename']}_{idx}", type="secondary", use_container_width=True):
                        if doc["file_path"] and os.path.exists(doc["file_path"]):
                            try:
                                os.remove(doc["file_path"])
                                logger.info(f"Deleted file '{doc['filename']}' from filesystem.")
                            except FileNotFoundError:
                                st.error(f"File '{doc['filename']}' not found in filesystem.")
                                logger.error(f"File '{doc['filename']}' not found during deletion.")
                        
                        delete_documents_by_document_name(doc["filename"])
                        st.session_state["documents"].pop(idx)
                        st.session_state["doc_count"] = len(st.session_state["documents"])
                        st.session_state["deleted_file"] = doc["filename"]
                        time.sleep(0.3)
                        st.rerun()
                
                if idx < len(st.session_state["documents"]) - 1:
                    st.markdown('<div class="divider" style="margin: 0;"></div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("""
        <div class="empty-state">
            <div class="empty-state-icon">📄</div>
            <h3 style="margin: 0 0 0.5rem; color: var(--text);">No documents yet</h3>
            <p style="margin: 0; color: var(--text-muted);">Upload your first PDF to start building your knowledge base</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

render_upload_page()