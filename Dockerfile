FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    python3-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Copy only requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies without cache
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy app source code
COPY . .

# Run the chatbot Streamlit app
CMD ["streamlit", "run", "bot_frontend.py", "--server.port=8501", "--server.enableCORS=false"]
