#!/usr/bin/env bash

# Initialize environment variables
cp -rf example.mysql.env .mysql.env
cp -rf example.env .env
cp -rf example.env .docker.env
sed -i "s@WORKING_DIR=/app@WORKING_DIR=$PWD@" .env
sed -i "s@MYSQL_SEARCH_ENGINE_CONNECTION_HOST=mysql@MYSQL_SEARCH_ENGINE_CONNECTION_HOST=localhost@" .env

# https://stackoverflow.com/questions/43267413/how-to-set-environment-variables-from-env-file
set -a # automatically export all variables
source .env
set +a

# Initialize output directories and environment variables
sudo mkdir -m 777 -p ${LOG_FILES_PATH} ${MODELS_PATH}
sudo chmod -R 777 ${LOG_FILES_PATH} ${MODELS_PATH}

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