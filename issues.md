# Docly - Issues & Bugs Analysis

Ordered by priority (Critical → High → Medium → Low)

---

## 🔴 CRITICAL

### 1. ~~OpenSearch Hybrid Search Pipeline Not Created~~ ✅ **FIXED**
**Files:** `src/opensearch.py`, `src/ingestion.py`
**Fixed:** Added `create_search_pipeline()` function that creates the pipeline automatically on index creation. Added fallback to simple kNN+BM25 search if pipeline fails.

### 2. ~~Setup Logging Called Without Parentheses~~ ✅ **FIXED**
**File:** `src/llm.py:12`
**Fixed:** Changed `setup_logging` to `setup_logging()`

### 3. ~~Ollama Model List Check Broken~~ ✅ **FIXED**
**File:** `src/llm.py:20-21`
**Fixed:** Now properly extracts model names from `ollama.list()` response: `[m.get('name', '') for m in available_models.get('models', [])]`

### 4. ~~Asymmetric Embedding Prefix Mismatch~~ ✅ **FIXED**
**File:** `src/llm.py:111`
**Fixed:** Changed search query prefix from `"passage: "` to `"query: "` for asymmetric embeddings. Ingestion still correctly uses `"passage: "` for documents.

### 5. ~~No Error Handling for OpenSearch Connection~~ ✅ **FIXED**
**Files:** `pages/upload_document.py`, `pages/chatbot.py`
**Fixed:** Added try/except blocks with user-friendly error messages and `st.stop()` when OpenSearch is unreachable.

---

## 🟠 HIGH

### 6. ~~Duplicate OpenSearch Client Creation~~ ✅ **FIXED**
**File:** `src/ingestion.py:45`
**Fixed:** `bulk_index_documents()` now accepts optional `client` parameter. Callers pass existing client.

### 7. PDF Text Extraction Fails Silently
**Files:** `pages/upload_document.py:109-110`, `pages/upload_document.py:48-49`
**Issue:** `PdfReader` with PyPDF2 fails on many PDFs (encrypted, scanned, complex layouts). No fallback to OCR (pytesseract is in requirements but unused) and no user feedback when extraction yields empty text.

### 8. Session State Not Persisted Across Page Navigation
**Files:** `app.py`, `pages/upload_document.py`, `pages/chatbot.py`
**Issue:** With Streamlit's native multipage, each page runs as separate script. Session state persists, but model loading (`embedding_models_loaded`) runs on each page independently. No shared initialization.

### 9. ~~Chat History Includes Current Prompt Twice~~ ✅ **FIXED**
**Files:** `pages/chatbot.py:82-101`, `src/llm.py:101-103`
**Fixed:** Now passes `history_for_context = st.session_state["chat_history"][-10:]` (without current prompt) to `generate_response_streaming()`.

### 10. ~~No Streaming Response Handling for Errors~~ ✅ **FIXED**
**Files:** `pages/chatbot.py:104-117`, `src/llm.py:33-50`
**Fixed:** Shows error message when `response_stream` is None: "Error: Failed to generate response. Please check if Ollama is running and the model is available."

---

## 🟡 MEDIUM

### 11. Index Config Template Variable Not Replaced
**File:** `src/index_config.json:16`
**Issue:** `"dimension": "{{EMBEDDING_DIMENSION}}"` uses template syntax but `load_index_config()` only replaces it in Python code. If index is created via other means, dimension will be literal string `"{{EMBEDDING_DIMENSION}}"` causing errors.

### 12. Chunk Size in Characters Not Tokens
**File:** `src/utils.py:38-58`, `src/constants.py:6`
**Issue:** `TEXT_CHUNK_SIZE = 300` is treated as word count (split by space) but named as character count. For sentence-transformers, chunking should be by tokens, not words.

### 13. No Document Deduplication Check in Index
**File:** `src/ingestion.py:45-74`
**Issue:** `bulk_index_documents` doesn't check if document already exists in index. Duplicate uploads create duplicate entries with different doc_ids.

### 14. Embedding Model Reloaded on Every Page
**Files:** `pages/upload_document.py:61-65`, `pages/chatbot.py:60-65`
**Issue:** Each page independently loads the embedding model. With `@st.cache_resource` this is cached, but the spinner shows on each page visit.

### 15. Delete Doesn't Refresh Document List from Index
**File:** `pages/upload_document.py:156-161`
**Issue:** After deleting from OpenSearch, the local session state is updated but if user refreshes page, `load_documents_from_index()` queries OpenSearch again - this is correct. But the local file deletion and index deletion should be atomic.

---

## 🟢 LOW

### 16. Hardcoded Paths
**Files:** `src/ingestion.py:16`, `pages/upload_document.py:92`
**Issue:** Relative paths like `"src/index_config.json"` and `"uploaded_files"` assume working directory. Breaks if app run from different directory.

### 17. No Input Validation on Upload
**File:** `pages/upload_document.py:79-84`
**Issue:** No file size limit, no validation of PDF content, no malware scanning. Users can upload arbitrarily large files.

### 18. Typo in Constant Name
**File:** `src/constants.py:4`
**Issue:** `ASSYMETRIC_EMBEDDING` should be `ASYMMETRIC_EMBEDDING` (double S). Used consistently but incorrect spelling.

### 19. Unused Imports
**Files:** `src/llm.py:1` (streamlit imported but only used for cache), `src/llm.py:9` (duplicate setup_logging import), `src/embeddings.py:6` (Dict, Tuple imported but unused)

### 20. No Health Check Endpoint
**General:** No way to verify OpenSearch, Ollama, and model availability before using the app.

### 21. Log File Directory May Not Exist
**File:** `src/utils.py:13`, `src/constants.py:13`
**Issue:** `logs/app.log` assumes `logs/` directory exists. First run will fail if directory missing.

### 22. Temperature Not Validated
**File:** `pages/chatbot.py:47-52`
**Issue:** Slider allows 0.0-1.0 but Ollama may support different range. No validation.

### 23. Conversation History Grows Unbounded
**File:** `src/llm.py:101-103`
**Issue:** Only last 10 messages used for prompt, but full history stored in session_state indefinitely. Memory leak in long sessions.

### 24. No Loading State for Model Pull
**File:** `src/llm.py:16-30`
**Issue:** `ensure_model_pulled` pulls model without progress indication. Large models (8B params) take minutes with no UI feedback.

### 25. Sidebar Metrics Show Stale Data
**File:** `src/theme.py:285-290`
**Issue:** `doc_count` and `chat_history` length shown in sidebar but only update on page rerun. Not reactive to changes from other pages.

---

## Summary by Category

| Priority | Total | Fixed | Remaining |
|----------|-------|-------|-----------|
| Critical | 5 | **5** | 0 |
| High | 5 | **3** | 2 |
| Medium | 5 | 0 | 5 |
| Low | 10 | 0 | 10 |
| **Total** | **25** | **8** | **17** |

---

## Next Recommended Fixes (High Priority)

1. **PDF Extraction with OCR Fallback** (Issue #7) - Add pytesseract fallback for scanned/image-based PDFs
2. **Shared Model Initialization** (Issue #8) - Move model loading to `app.py` to avoid duplicate loading per page

## Next Recommended Fixes (Medium Priority)

3. **Fix Index Config Template** (Issue #11) - Replace `{{EMBEDDING_DIMENSION}}` placeholder properly
4. **Token-based Chunking** (Issue #12) - Use sentence-transformers tokenizer for proper chunk sizing
5. **Document Deduplication** (Issue #13) - Check index before bulk indexing

## Quick Wins (Low Priority)

6. **Create logs directory** (Issue #21) - Add `os.makedirs("logs", exist_ok=True)` in `setup_logging()`
7. **Fix constant typo** (Issue #18) - Rename `ASSYMETRIC` → `ASYMMETRIC` (requires updating all references)
8. **Clean unused imports** (Issue #19)