#!/usr/bin/env bash

# Initialize output directories and environment variables
sudo mkdir -m 777 -p /opt/tuesearch/data /opt/tuesearch/log  && sudo chmod -R 777 /opt/tuesearch
cp -rf example.mysql.env .mysql.env
cp -rf example.env .env
cp -rf example.env .docker.env
sed -i "s@SERP_FILE=/app/crawler/data/serp.json@SERP_FILE=$PWD/crawler/data/serp.json@" .env
sed -i "s@MYSQL_SEARCH_ENGINE_CONNECTION_HOST=mysql@MYSQL_SEARCH_ENGINE_CONNECTION_HOST=localhost@" .env
sed -i "s@INITIAL_DOCUMENTS_FILE=/app/crawler/data/documents.json@INITIAL_DOCUMENTS_FILE=$PWD/crawler/data/documents.json @" .env

# Install dependencies
if [ ! -d venv ]; then
  python3 -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt

# Install pre-commit hooks
pre-commit install

# Install nltk stopwords
python3 -c "import nltk; nltk.download('stopwords');"