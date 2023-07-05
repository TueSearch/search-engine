FROM ghcr.io/tuesearch/search-engine/tuesearch-backend-base:latest

# Copy the requirements.txt file to the container
COPY requirements.txt .

# Install the project dependencies
RUN python3 -m pip install -r requirements.txt

RUN python3 -m spacy download en_core_web_md

# Copy backend
COPY backend ./backend

# Copy crawler
COPY crawler ./crawler

# Copy crawler
COPY scripts ./scripts

# Copy data
COPY data ./data