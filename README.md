# TueSearch

This project contains the source code of the final project from the course modern search engines at the University of
Tübingen.

## Table of Contents

- [Project Structure](#project-structure)
- [Crawler](#crawler)
    - [Installation](#installation)
    - [Usage](#usage)
    - [Project Structure](#project-structure)
- [Backend](#backend)
    - [Usage](#usage)
- [Frontend](#frontend)
- [Docker](#docker)
- [Team](#team)

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
- `requirements.dev.txt`: This file contains the required dependencies for the project for local development.
- `requirements.prod.txt`: This file contains the required dependencies for the project for deployment.
- `package.json`: This file contains the required dependencies for the project's frontend.
- `python.Dockerfile`: This file contains the Dockerfile for the Python crawler & backend.
- `requirements.txt`: This file contains the required dependencies for the project's crawler & backend.

# Crawler

## Set up

Install dependencies

```bash
pip install -r requirements.dev.txt
```

3. Install MySQL and configure MySQL.

4. Configure `.env` file to match your local development.

6. Install pre-commit hooks:

```bash
pre-commit install
```

## Usage

Note: Before running the script, make sure to configure the database settings in the `.env file.
Refer to the `.env.example` file for the required configuration variables.

To use the web crawler, follow the workflow below:

1. (Optional) If you want new SERP, delete the `crawler/data/serp.json` file, fetch a new search engine results page (
   SERP) using
   the `fetch_serp.py` script.

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
python3 -m crawler.crawl
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

# Backend

## Set up

Same as described in the section [Crawler](#crawler).

## Usage

1. You can run the Flask application to search for documents using the `backend/app.py` script.

```bash
python3 -m backend.app
```

Open the browser and navigate to `http://localhost:5000` to access the search engine.

# Frontend

TODO

# Docker

## Set up

TODO

# Team Members

- [Philipp Alber]()
- [Lukas Listl]()
- [Daniel Reimer]()
- [Long Nguyen]()