# Use the image from the Docker Hub to accelerate the build
FROM ghcr.io/tuesearch/search-engine/tuesearch-backend-base:latest

# Copy the requirements.txt file to the container
#COPY requirements.txt .

# Install the project dependencies
#RUN python3 -m pip install -r requirements.txt

# Copy backend
COPY backend ./backend

# Copy crawler
COPY crawler ./crawler

# Copy crawler
COPY scripts ./scripts