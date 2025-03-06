# HEAL SYNC

A RAG system for clinical protocols using fine-tuned embeddings.

## Features
- Custom-trained embeddings for clinical protocols
- Hybrid search across multiple collections
- PDF processing and chunking
- Interactive Q&A interface

## Installation

```bash
# Clone repository
git clone [your-repo]

# Install requirements
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```

## Usage

1. Start the app:
```bash
streamlit run app.py
```

2. Upload a protocol PDF
3. Ask questions about the content

## System Requirements
- Python 3.8+
- 4GB RAM minimum
- GPU optional but recommended

## Architecture
- Frontend: Streamlit
- Embeddings: Custom fine-tuned model
- Vector Store: Qdrant
- LLM: GPT-4
