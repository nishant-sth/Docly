import streamlit as st

def apply_theme():
    st.markdown("""
    <style>
    :root {
        --primary: #2563eb;
        --primary-hover: #1d4ed8;
        --primary-light: #dbeafe;
        --secondary: #64748b;
        --success: #16a34a;
        --danger: #dc2626;
        --warning: #f59e0b;
        --bg: #f8fafc;
        --card: #ffffff;
        --text: #1e293b;
        --text-muted: #64748b;
        --border: #e2e8f0;
        --shadow: 0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.06);
        --shadow-lg: 0 10px 25px rgba(0,0,0,0.1), 0 4px 6px rgba(0,0,0,0.05);
        --radius: 12px;
        --radius-sm: 8px;
    }

    .stApp {
        background-color: var(--bg);
    }

    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 900px;
    }

    h1, h2, h3, h4 {
        color: var(--text);
        font-weight: 600;
    }

    h1 { font-size: 1.75rem; margin-bottom: 0.5rem; }
    h2 { font-size: 1.375rem; margin-bottom: 0.75rem; }
    h3 { font-size: 1.125rem; margin-bottom: 0.5rem; }

    .card {
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        padding: 1.5rem;
        box-shadow: var(--shadow);
        margin-bottom: 1rem;
    }

    .card-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 1rem;
        padding-bottom: 0.75rem;
        border-bottom: 1px solid var(--border);
    }

    .card-title {
        font-size: 1rem;
        font-weight: 600;
        color: var(--text);
    }

    .stButton > button {
        background: var(--primary);
        color: white;
        border: none;
        border-radius: var(--radius-sm);
        padding: 0.625rem 1.25rem;
        font-size: 0.875rem;
        font-weight: 500;
        transition: all 0.15s ease;
        width: 100%;
    }

    .stButton > button:hover {
        background: var(--primary-hover);
        transform: translateY(-1px);
        box-shadow: var(--shadow);
    }

    .stButton > button:active {
        transform: translateY(0);
    }

    .stButton > button[kind="secondary"] {
        background: var(--card);
        color: var(--text);
        border: 1px solid var(--border);
    }

    .stButton > button[kind="secondary"]:hover {
        background: var(--bg);
        border-color: var(--secondary);
    }

    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > div,
    .stNumberInput > div > div > input {
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-sm) !important;
        background: var(--card) !important;
        color: var(--text) !important;
    }

    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 3px var(--primary-light) !important;
    }

    .stFileUploader > div {
        border: 2px dashed var(--border) !important;
        border-radius: var(--radius) !important;
        background: var(--card) !important;
        padding: 2rem !important;
    }

    .stFileUploader > div:hover {
        border-color: var(--primary) !important;
        background: var(--primary-light) !important;
    }

    .stChatMessage {
        background: var(--card) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius) !important;
        padding: 1rem 1.25rem !important;
        margin-bottom: 0.75rem !important;
        box-shadow: var(--shadow) !important;
    }

    .stChatMessage[data-testid="stChatMessage-user"] {
        background: var(--primary-light) !important;
        border-color: var(--primary) !important;
        margin-left: 2rem !important;
    }

    .stChatMessage[data-testid="stChatMessage-assistant"] {
        margin-right: 2rem !important;
    }

    .stChatInput > div {
        background: var(--card) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius) !important;
        box-shadow: var(--shadow-lg) !important;
    }

    .stSidebar {
        background: var(--card) !important;
        border-right: 1px solid var(--border) !important;
    }

    .stSidebar .stMarkdown h2,
    .stSidebar .stMarkdown h3,
    .stSidebar .stMarkdown h4 {
        color: var(--text) !important;
    }

    .sidebar-section {
        padding: 1rem 0;
        border-bottom: 1px solid var(--border);
    }

    .sidebar-section:last-child {
        border-bottom: none;
    }

    .sidebar-label {
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: var(--text-muted);
        margin-bottom: 0.5rem;
        display: block;
    }

    .stat-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.375rem;
        background: var(--primary-light);
        color: var(--primary);
        padding: 0.25rem 0.625rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 500;
    }

    .danger-zone {
        border: 1px solid var(--danger) !important;
        background: #fef2f2 !important;
    }

    .danger-zone .stButton > button {
        background: var(--danger) !important;
    }

    .danger-zone .stButton > button:hover {
        background: #b91c1c !important;
    }

    .empty-state {
        text-align: center;
        padding: 3rem 1.5rem;
        color: var(--text-muted);
    }

    .empty-state-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
        opacity: 0.5;
    }

    .toast-success {
        background: #dcfce7;
        color: #166534;
        border: 1px solid #bbf7d0;
        border-radius: var(--radius-sm);
        padding: 0.75rem 1rem;
        margin-bottom: 1rem;
    }

    .toast-error {
        background: #fef2f2;
        color: #991b1b;
        border: 1px solid #fecaca;
        border-radius: var(--radius-sm);
        padding: 0.75rem 1rem;
        margin-bottom: 1rem;
    }

    .toast-warning {
        background: #fffbeb;
        color: #92400e;
        border: 1px solid #fde68a;
        border-radius: var(--radius-sm);
        padding: 0.75rem 1rem;
        margin-bottom: 1rem;
    }

    .divider {
        height: 1px;
        background: var(--border);
        margin: 1.5rem 0;
    }

    @media (max-width: 640px) {
        .main .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }
        .card { padding: 1rem; }
    }
    </style>
    """, unsafe_allow_html=True)

def render_sidebar():
    with st.sidebar:
        try:
            st.image("images/docly_logo.png", clamp=True)
        except Exception:
            st.markdown("""
            <div style="text-align: center; padding: 1rem;">
                <div style="font-size: 3rem;">📄</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="text-align: center; padding: 0.5rem 1rem 1rem;">
            <p style="margin: 0.25rem 0 0; font-size: 0.875rem; color: var(--text-muted);">Your Private Local AI Document Assistant</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown('<span class="sidebar-label">Status</span>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Documents", st.session_state.get("doc_count", 0))
        with col2:
            st.metric("Messages", len(st.session_state.get("chat_history", [])))
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("""
        <div style="margin-top: 2rem; padding-top: 1rem; border-top: 1px solid var(--border); text-align: center;">
            <p style="margin: 0; font-size: 0.75rem; color: var(--text-muted);">© 2025 Docly</p>
        </div>
        """, unsafe_allow_html=True)

def show_toast(message, type="success"):
    css_class = f"toast-{type}"
    st.markdown(f'<div class="{css_class}">{message}</div>', unsafe_allow_html=True)

def render_empty_state(icon, title, description, action_label=None, action_callback=None):
    st.markdown(f"""
    <div class="empty-state">
        <div class="empty-state-icon">{icon}</div>
        <h3 style="margin: 0 0 0.5rem; color: var(--text);">{title}</h3>
        <p style="margin: 0; color: var(--text-muted);">{description}</p>
    </div>
    """, unsafe_allow_html=True)
    if action_label and action_callback:
        if st.button(action_label, use_container_width=True):
            action_callback()