# docker build -f docker/backend.base.Dockerfile -t ghcr.io/tuesearch/search-engine/tuesearch-backend-base:latest .
# docker tag ghcr.io/tuesearch/search-engine/tuesearch-backend-base:latest ghcr.io/tuesearch/search-engine/tuesearch-backend-base:latest
# docker push ghcr.io/tuesearch/search-engine/tuesearch-backend-base:latest

FROM ubuntu:22.04

# Pyppeteer
RUN apt-get update -y && apt-get install chromium-chromedriver python3-pip -y

# Install chromium dependencies
RUN apt-get install -y gconf-service libasound2 libatk1.0-0 libc6 libcairo2 libcups2 libdbus-1-3 libexpat1 libfontconfig1 libgcc1 libgconf-2-4 libgdk-pixbuf2.0-0 libglib2.0-0 libgtk-3-0 libnspr4 libpango-1.0-0 libpangocairo-1.0-0 libstdc++6 libx11-6 libx11-xcb1 libxcb1 libxcomposite1 libxcursor1 libxdamage1 libxext6 libxfixes3 libxi6 libxrandr2 libxrender1 libxss1 libxtst6 ca-certificates fonts-liberation libappindicator1 libnss3 lsb-release xdg-utils wget

# Install dependencies for Polyglot
RUN apt-get install icu-devtools libicu-dev pkg-config -y
# Add user
RUN useradd -ms /bin/bash tuesearch

# Create directories
RUN mkdir -p /opt/tuesearch/

# Give rights
RUN chown -R tuesearch:tuesearch /opt/tuesearch

# Set the working directory in the container
WORKDIR /app

# Change ownership of the /app directory to the tuesearch user
RUN chown -R tuesearch:tuesearch /app

# Switch user
USER tuesearch

# Copy the requirements.txt file to the container
COPY requirements.txt .

# Install the project dependencies
RUN python3 -m pip install -r requirements.txt

# Install chromium once
RUN python3 -c 'import pyppeteer; pyppeteer.chromium_downloader.download_chromium()'

RUN python3 -m spacy download en_core_web_md

# Copy backend
COPY backend ./backend

# Copy crawler
COPY crawler ./crawler

# Copy crawler
COPY scripts ./scripts

# Copy data
COPY data ./data