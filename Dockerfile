FROM python:3.9-slim

WORKDIR /app

# ✅ Install system dependencies required for PyMuPDF & other dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    make \
    gcc \
    libffi-dev \
    pkg-config \
    libfreetype6-dev \
    libssl-dev \
    libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ✅ Upgrade pip to avoid outdated dependency conflicts
RUN pip install --no-cache-dir --upgrade pip

# ✅ Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ✅ Copy the rest of the application first
COPY . .

# ✅ Create .streamlit directory and config file
RUN mkdir -p .streamlit && \
    echo '[server]\nenableCORS = true\nenableXsrfProtection = false\n\n[browser]\ngatherUsageStats = false' > .streamlit/config.toml

# ✅ Expose correct ports (Hugging Face uses 7860)
EXPOSE 7860

# ✅ Start Streamlit with Hugging Face port
CMD streamlit run app.py --server.address 0.0.0.0 --server.port 7860
