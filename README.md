


# TueSearch

This project contains the source code of the final project from the course modern search engines at the University of
Tübingen.

## Table of Contents

- [Project Structure](#project-structure)
- [Crawler](#crawler)
    - [Crawler set up](#crawler-set-up)
    - [Crawler usage](#crawler-usage)
    - [Cheat cheatsheet](#crawler-cheatsheet)
        - [Show directories' content](#show-directories-content)
        - [Show logs](#show-logs)
- [Backend](#backend)
    - [Backend set up](#backend-set-up)
    - [Backend usage](#backend-usage)
    - [Backend cheatsheet](#backend-cheatsheet)
        - [Test the API](#test-the-api)
- [Frontend](#frontend)
- [Docker](#docker)
    - [Docker set up](#docker-set-up)
    - [Docker usage](#docker-usage)
    - [Docker cheatsheet](#docker-cheatsheet)
        - [Show containers](#show-containers)
        - [Show logs](#show-logs)
        - [Enter containers](#enter-containers)
        - [Restart the services](#restart-the-services)
        - [Clean everything](#clean-everything)
- [Team Members](#team-members)

# Project Structure

The project has the following structure:

- `.github`: This directory contains the GitHub workflow files for the project.
- `backend`: This directory contains the Flask application for the search engine.
    - `app.py`: This script contains the Flask API for the search engine.
- `crawler`: This directory contains the main source code of the web crawler.
    - `data`: This directory contains the data files for the project.
        - `serp.json`: This file contains the search engine results page (SERP) for the query "Tübingen".
    - `tests`: This directory contains the test files for the project. (Note: The test directory could be improved
      further
      to include more comprehensive testing scenarios and coverage.)
    - `build_inverted_index.py`: The script for building the inverted index from the crawled documents.
    - `build_ranker.py`: The script for building the ranker from the inverted index and query.
    - `fetch_serp.py`: The script for fetching the search engine results page (SERP) and saving it as a JSON file.
    - `initialize_database.py`: The script for initializing the database and creating the necessary tables.
    - `crawl.py`: The script for the web crawling process, which fetches web pages, classifies their relevance, and
      stores them in the database.
    - `models.py`: This module defines the database models used for storing crawled documents and job management.
    - `rank.py`: This module contains the ranker class, which uses the built ranker to rank the documents based on the
      query.
    - `utils.py`: This module contains utility functions used in the crawling process.
- `.pre-commit-config.yaml`: This file contains the configuration for the pre-commit hooks.
- `.pylintrc`: This file contains the configuration for the pylint linter.
- `CODEOWNERS`. This file contains the GitHub code owners for the project.
- `docker-compose.yml`: Configuration for docker-compose for local development and deployment.
- `example.env`: This file contains the example environment variables for the project.
- `example.mysql.env`: This file is specifically for the MySQL's instance in the docker-compose file.
- `package.json`: This file contains the required dependencies for the project's frontend.
- `python.Dockerfile`: This file contains the Dockerfile for the Python crawler & backend.
- `requirements.dev.txt`: This file contains the required dependencies for the project's crawler & backend at local.
- `requirements.prod.txt`: This file contains the required dependencies for the project's crawler & backend at
  production. Should contain fewer dependencies.

# Crawler

## Crawler set up

1. Create output directories and initialize environment variables

```bash
sudo mkdir -m 777 -p /opt/tuesearch/data /opt/tuesearch/log  && sudo chmod -R 777 /opt/tuesearch
cp example.mysql.env .mysql.env
cp example.env .env
cp example.env .docker.env
```

Note: you might need to change some variables in `.env` according to
your local developmente environment.

2. Install dependencies

```bash
pip install -r requirements.dev.txt
```

3. Start MySQL database

```bash
docker-compose up -d --build mysql
```

4. (Optional) Install pre-commit hooks:

```bash
pre-commit install
```

## Crawler usage

To use the web crawler, follow the workflow below:

1. (Optional) If you want new SERP, delete the `crawler/data/serp.json` file, fetch a new search engine results page (
   SERP) using the `fetch_serp.py` script.

```bash
python3 -m crawler.fetch_serp
```

2. Run the `initialize_database.py` script. This script sets up the database
   and creates the necessary tables for storing crawled documents and job management.

```bash
python3 -m crawler.initialize_database
```

3. Once you have the initialized database, you can start the crawling process using the `craw.py` script.

```bash
python3 -m crawler.crawl -n 10 # Crawl 10 items
```

or simply

```bash
python3 -m crawler.crawl # Craw in loop
```

4. After crawling, you can build the inverted index using the `build_inverted_index.py` script. This script analyzes
   the crawled documents and constructs an inverted index to enable efficient searching.

```bash
python3 -m crawler.build_inverted_index
```

This step should be repeated regularly to keep the index fresh.

5. Build the ranker using the `build_ranker.py` script.
   This script builds the models needed to rank websites. After training, the model
   will be stored in paths defined in the `.env` file.

```bash
python3 -m crawler.build_ranker
```

This step should be repeated regularly to keep the ranker fresh.

## Crawler cheatsheet

### Show directories' content

```bash
ls -lha /opt/tuesearch/data/
```

```bash
ls -lha /opt/tuesearch/log/
```

### Show logs

```bash
cat /opt/tuesearch/log/crawl.log
```

```bash
cat /opt/tuesearch/log/database.log
```

```bash
cat /opt/tuesearch/log/fetch_serp.log
```

```bash
cat /opt/tuesearch/log/initialize_database.log
```

```bash
cat /opt/tuesearch/log/build_inverted_index.log
```

```bash
cat /opt/tuesearch/log/build_ranker.log
```

# Backend

## Backend set up

Same as described in the section [Crawler](#crawler).

## Backend usage

1. You can run the Flask application to search for documents using the `backend/app.py` script.

```bash
python3 -m backend.app
```

## Backend cheatsheet

### Test the API

```bash
curl http://localhost:5000/search?q=test
```

# Frontend

TODO

# Docker

## Docker set up

Same as described in the section [Crawler](#crawler).

## Docker usage

1. Start the services

```bash
docker-compose up -d --build
```

and wait at first time about 60 seconds for the crawler to fill the database.

2. If everything successes then

```bash
docker container ps
```

should show only 2 containers running, `mysql` and `backend_server`.

3. Test the API with

```bash
curl http://localhost:5001/search?q=test
```

Note that port of the container's backend is not the same as
the port of the host's backend.

## Docker cheatsheet

### Show containers

```bash
docker container ps
```

### Show logs

```bash
docker container logs mysql
```

```bash
docker container logs initialize_database
```

```bash
docker container logs crawl
```

```bash
docker container logs build_inverted_index
```

```bash
docker container logs build_ranker
```

```bash
docker container logs backend_server
```

### Enter containers

```bash
docker exec -it mysql bash
```

```bash
docker exec -it initialize_database bash
```

```bash
docker exec -it crawl bash
```

```bash
docker exec -it build_inverted_index bash
```

```bash
docker exec -it build_ranker bash
```

```bash
docker exec -it backend_server bash
```

### Restart the services

```bash
docker-compose down
```

```bash
docker-compose up -d --build
```

### Clean everything

```bash
docker system prune -a
```

# Team Members

- [Daniel Reimer](https://github.com/Seskahin)
- [Long Nguyen](https://github.com/longpollehn)
- [Lukas Listl](https://github.com/LukasListl)
- [Philipp Alber](https://github.com/coolusaHD)