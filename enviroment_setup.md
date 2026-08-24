# Prerequisites and Environment Setup

# 📗 01 — Prerequisites & Environment Setup

> **Mission:** walk step‑by‑step through every installation and validation task required for this RAG workshop.  

**Supported OS:** macOS (Apple & Intel) • Windows 10/11 • Linux (Ubuntu/Debian).  

---

### 🗺 Roadmap

1. Check / install Python 3.11 +  
2. Install Docker Desktop  
3. Install fast tooling (`uv`, `ruff`)  
4. Clone the course repo  
5. Create & activate a virtual‑env  
6. Install course dependencies  
7. Pull & run services (OpenSearch + Dashboards + Ollama)  
8. Create `constants.py`  
9. Verify docTR OCR  
10. Sanity‑check all services  

*(Total hands‑on time: ≈ 25 minutes on a decent connection)*

---

## 1 — Python 3.11 or newer 🐍

Guide - https://realpython.com/installing-python/

#### macOS

```bash
# Homebrew (recommended)
brew install python@3.12
echo 'export PATH="/opt/homebrew/opt/python@3.12/libexec/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

which python3.12  
python3 --version 

```
#### Windows 10/11

```powershell
# Winget
winget install Python.Python.3.12
# OR Microsoft Store: "Python 3.12"

python3 --version 

```


---

### 1.2 — Install `uv`

Document - https://docs.astral.sh/uv/getting-started/installation/#standalone-installer

#### macOS / Linux (bash / zsh)

```bash
curl -LsSf https://astral.sh/uv/install.sh | less

brew install uv 
```

#### Windows (PowerShell)

```powershell
python3 -m pip install uv 

py -m pip install -U uv 
```


---

### 1.3 Create, Activate & Register a `uv` Kernel 🐍

We will create an isolated environment for this course using `uv` and then register it as a kernel so Jupyter can use it.

**Run these commands in your terminal**, from the `build_your_local_RAG_system` folder.

#### 1.3.1 Create & Activate

```bash
# Create a virtual env using Python 3.12
uv venv -p python3.12 .venv

# Activate it (your prompt should get a (.venv) prefix)
source .venv/bin/activate
```

> **Windows Users?**  
> Use `.venv\Scripts\Activate.ps1` (PowerShell) or `.venv\Scripts\activate.bat` (CMD) to activate.

#### 1.3.2 Install

```bash
# Install the kernel package into our new env
uv pip install ipykernel
```

#### 1.3.3 Register the Kernel 
```bash
uv run python -m ipykernel install --user --name docly --display-name "Docly"
```

**Restart your Jupyter server now.**

Once it reloads, click here in the notebook and select from the top menu:

`Kernel` → `Change kernel` → `Docly (Python 3.12)`

After selecting it, the final check below should pass.


---

## 2 — Install Course Dependencies 📦

```bash
uv pip install -r requirements.txt               # main deps
```

---

## 3 — Docker Desktop 🐳

Download & install:

* **macOS (Apple/Intel):** <https://www.docker.com/products/docker-desktop/>
* **Windows 10/11:** same link (WSL 2 required)
* **Linux:** `sudo apt install docker.io docker-compose-plugin`

After installation **reboot** or at least restart your terminal so the `docker` command is on your PATH.


---

## 4 — Install Ollama

Download & install:

* https://ollama.com/download


Lets download Qwen3 model:


* https://ollama.com/library/qwen3

```bash
ollama run qwen3:8b 
```



---

## 5 — Pull & Run Core Services 

### 5.1 OpenSearch (single‑node)

```bash
docker pull opensearchproject/opensearch:2.19.2
docker pull opensearchproject/opensearch-dashboards:2.19.2

docker run -d --name opensearch `
  -p 9200:9200 -p 9600:9600 `
  -e "discovery.type=single-node" `
  -e "DISABLE_SECURITY_PLUGIN=true" `
  opensearchproject/opensearch:2.19.2

docker run -d --name opensearch-dashboards `
  -p 5601:5601 `
  --link opensearch:opensearch `
  -e "OPENSEARCH_HOSTS=http://opensearch:9200" `
  -e "DISABLE_SECURITY_DASHBOARDS_PLUGIN=true" `
  opensearchproject/opensearch-dashboards:2.19.2
```


> Visit http://localhost:5601 in your browser to access the OpenSearch Dashboard. If you see the dashboard, you’re all set! 🎉


### 5.2 Add Hybrid functionality to OpenSearch

 > Open the OpenSearch Dashboard, go to Dev Tools, paste the below JSON, and hit Run. This pipeline will be essential for blending the BM25 and semantic scores for improved search quality.

json
```
PUT /_search/pipeline/nlp-search-pipeline
{
  "description": "Post processor for hybrid search",
  "phase_results_processors": [
    {
      "normalization-processor": {
        "normalization": {
          "technique": "min_max"
        },
        "combination": {
          "technique": "arithmetic_mean",
          "parameters": {
            "weights": [
              0.3,
              0.7
            ]
          }
        }
      }
    }
  ]
}

```


---

## 6 — Install and Verify OCR Engine (Tesseract)

For our OCR tasks, we will use `pytesseract`, a Python wrapper for Google's Tesseract-OCR engine. This requires a two-part setup: first installing the engine on your operating system, and then installing the Python library that connects to it.

### 6.1 Install External Dependencies (Tesseract & Poppler)

`pytesseract` needs **Tesseract** to read characters, and its helper library `pdf2image` needs **Poppler** to convert PDF pages into images. You must install both.

#### **macOS (via Homebrew)**

Open your terminal and run this single command:
```bash
brew install tesseract poppler
```

#### **Windows**

1.  **Install Tesseract:**
    *   Download the official installer from the [Tesseract at UB Mannheim page](https://github.com/UB-Mannheim/tesseract/wiki).
    *   Run the installer. **Important:** Take note of the installation path, which is usually `C:\Program Files\Tesseract-OCR`.
    or
    winget install Tesseract-OCR

2.  **Install Poppler:**
    *   Download the latest Poppler binary from [this GitHub repository](https://github.com/oschwartz10612/poppler-windows/releases).
    *   Unzip the file into a permanent location, like `C:\poppler`.
    *   Add the `bin` subfolder (e.g., `C:\poppler\poppler-24.02.0\bin`) to your system's PATH environment variable.
    Guide - https://github.com/oschwartz10612/poppler-windows/issues/42

### 6.2 Install Python Libraries

With the external tools installed, now install the Python libraries into your active virtual environment.

```bash
uv pip install pytesseract pdf2image Pillow fpdf2
```
> We install `fpdf2` just to create a dummy PDF for the test below.

### 6.3 Run Verification Test

The final step is to run the code cell below. It will:
1.  Create a simple, one-page PDF file named `ocr_test.pdf`.
2.  Use `pdf2image` and `pytesseract` to read the text from it.
3.  Print the extracted text and a success message.

> **Note for Windows Users:** You may need to uncomment and set the `tesseract_cmd` path in the code below if it's not found automatically.