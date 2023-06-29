# TueSearch

This project contains the source code of the final project from the course modern search engines at the University of
Tübingen.

## Table of Contents

- [TueSearch](#tuesearch)
    - [Table of Contents](#table-of-contents)
- [Set up](#crawler-set-up)
- [Crawler](#crawler)
    - [Crawler usage](#crawler-usage)
- [Backend](#backend)
    - [Backend usage](#backend-usage)
- [Frontend](#frontend)
- [Team Members](#team-members)
- [Project Structure](#project-structure)

# Set up

1. Create output directories and initialize environment variables.

<<<<<<< HEAD
- `.github`: This directory contains the GitHub workflow files for the project.
- `backend`: This directory contains the Flask application for the search engine.
  - `app.py`: This script contains the Flask API for the search engine.
  - `build_inverted_index.py`: The script for building the inverted index from the crawled documents.
  - `build_ranker.py`: The script for building the ranker from the inverted index and query.
  - `rank.py`: This module contains the ranker class, which uses the built ranker to rank the documents based on the
    query.
  - `streamers.py`: This module contains the streamers class, which is used to stream the documents from the database
    to the ranker.
- `crawler`: This directory contains the main source code of the web crawler.
  - `data`: This directory contains the data files for the project.
    - `serp.json`: This file contains the search engine results page (SERP) for the query "Tübingen".
    - `documents.json`: This file contains some initial crawled documents so local development gets a bit easier.
  - `models`: SQL models for the database.
    - `base.py`: This file contains the base model for the database.
    - `document.py`: This file contains the model for the documents table.
    - `job.py`: This file contains the model for the jobs table.
  - `relevance_classification`: Classify URL's, document's and job's relevance.
    - `document_relevance.py`: Determines if a document should be indexed.
    - `job_relevance.py`: Determines if a job should be executed.
    - `url_relevance.py`: Determines if a URL should be crawled and when it should be crawled.
  - `tests`: This directory contains the test files for the project. (Note: The test directory could be improved
    further to include more comprehensive testing scenarios and coverage.)
  - `utils`:
    - `io`: This module contains the functions for reading and writing data to files.
    - `log`: This module contains the functions for logging the crawling process.
    - `text`: Contains the function to preprocess text before feed it to ranker and classifier.
  - `crawl.py`: Determine a crawler. A crawler is a single process that crawls a single URL.
  - `fetch_serp.py`: The script for fetching the search engine results page (SERP) and saving it as a JSON file.
  - `initialize_database.py`: The script for initializing the database and creating the necessary tables and add
    initial data.
  - `main.py`: Start the crawler.
  - `priority_queue.py`: Contains the priority queue class, which is used to determine which server and which link is
    preferred.
- `docker`: This directory contains the docker files for the project.
  - `my.cnf`: This file contains the configuration for the MySQL database.
  - `mysql.cnf`: This file contains the configuration for the MySQL database.
  - `python.Dockerfile`: This file contains the Dockerfile for the Python crawler & backend.
- `frontend`: This directory contains the frontend application for the search engine.
- `scripts`: This directory contains the scripts for the project. Wil run only on Ubuntu at the time of writing.
  - `migration.py`: This script contains the migration for the database.
  - `init.sh`: This script contains the initialization for the project.
  - `*.sql`: These files contain the SQL queries for the project's migration.
- `.pre-commit-config.yaml`: This file contains the configuration for the pre-commit hooks.
- `.pylintrc`: This file contains the configuration for the pylint linter.
- `CHEATSHEET.md`: This file contains the cheatsheet for the project.
- `CODEOWNERS`. This file contains the GitHub code owners for the project.
- `docker-compose.yml`: Configuration for docker-compose for local development and deployment.
- `example.env`: This file contains the example environment variables for the project.
- `example.mysql.env`: This file is specifically for the MySQL's instance in the docker-compose file.
- `requirements.dev.txt`: This file contains the required dependencies for the project's crawler & backend at local.
- `requirements.prod.txt`: This file contains the required dependencies for the project's crawler & backend at
  production. Should contain fewer dependencies.
=======
```bash
cp -rf example.mysql.env .mysql.env
cp -rf example.env .env
```

2. Start the project

```bash
docker-compose up -d --build
```
>>>>>>> 5d34e01 (Renamed cheatsheet)

# Crawler

## Crawler usage

To use the web crawler, follow the workflow below:

1. Once the setup is done, you can start the crawling process using the `crawler/main.py` script.

```bash
python3 -m crawler.main -n 10 # Crawl 10 items
```

or simply

```bash
python3 -m crawler.main # Craw in loop
```

# Backend

## Backend set up

Same as described in the section [Crawler](#crawler).

## Backend usage

1. After crawling, you can build the inverted index using the `backend/build_inverted_index.py` script. This script
   analyzes
   the crawled documents and constructs an inverted index to enable efficient searching.

```bash
python3 -m backend.build_inverted_index
```

This step should be repeated regularly to keep the index fresh.

2. Build the ranker using the `backend/build_ranker.py` script.
   This script builds the models needed to rank websites. After training, the model
   will be stored in paths defined in the `.env` file.

```bash
python3 -m backend.build_ranker
```

This step should be repeated regularly to keep the ranker fresh.

3. You can run the Flask application to search for documents using the `backend/app.py` script.

```bash
python3 -m backend.app
```

4Test the API with

```bash
curl http://localhost:4000/search?q=tubingen
```

# Frontend

1. Install dependencies

```bash
npm install
```

2. Start the frontend

```bash
npm run dev
```

<<<<<<< HEAD
3. Open the browser at `http://localhost:4000/`

# Docker

## Docker set up

Same as described in the section [Crawler](#crawler). Try this command if you have permission issues:

```bash
bash scripts/init.sh
```

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

should show only 3 containers running, `mysql`, `frontend_server` and `backend_server`.

Note that port of the container's backend is not the same as
the port of the host's backend.
=======
3. Open the browser at `http://localhost:5000/`
>>>>>>> 5d34e01 (Renamed cheatsheet)

# Team Members

- [Daniel Reimer](https://github.com/Seskahin)
- [Long Nguyen](https://github.com/longpollehn)
- [Lukas Listl](https://github.com/LukasListl)
- [Philipp Alber](https://github.com/coolusaHD)

# Project Structure

The project has the following structure:

- `.github`: This directory contains the GitHub workflow files for the project.
- `backend`: This directory contains the Flask application for the search engine.
    - `app.py`: This script contains the Flask API for the search engine.
    - `build_inverted_index.py`: The script for building the inverted index from the crawled documents.
    - `build_ranker.py`: The script for building the ranker from the inverted index and query.
    - `rank.py`: This module contains the ranker class, which uses the built ranker to rank the documents based on the
      query.
    - `streamers.py`: This module contains the streamers class, which is used to stream the documents from the database
      to the ranker.
- `crawler`: This directory contains the main source code of the web crawler.
    - `models`: SQL models for the database.
        - `base.py`: This file contains the base model for the database.
        - `document.py`: This file contains the model for the documents table.
        - `job.py`: This file contains the model for the jobs table.
        - `server.py`: This file models a domain.
    - `relevance_classification`: Classify URL's, document's and job's relevance.
        - `document_relevance.py`: Determines if a document should be indexed.
        - `job_relevance.py`: Determines if a job should be executed.
        - `url_relevance.py`: Determines if a URL should be crawled and when it should be crawled.
    - `tests`: This directory contains the test files for the project. (Note: The test directory could be improved
      further to include more comprehensive testing scenarios and coverage.)
    - `utils`:
        - `io`: This module contains the functions for reading and writing data to files.
        - `log`: This module contains the functions for logging the crawling process.
        - `text`: Contains the function to preprocess text before feed it to ranker and classifier.
        - `url`: This module contains the functions for parsing and manipulating URLs.
    - `crawl.py`: Determine a crawler. A crawler is a single process that crawls a single URL.
    - `main.py`: Start the crawler.
    - `priority_queue.py`: Contains the priority queue class, which is used to determine which server and which link is
      preferred.
- `docker`: This directory contains the docker files for the project.
    - `frontend.Dockerfile`: This file contains the Dockerfile for the frontend.
    - `my.cnf`: This file contains the configuration for the MySQL database.
    - `mysql.cnf`: This file contains the configuration for the MySQL database.
    - `python.Dockerfile`: This file contains the Dockerfile for the Python crawler & backend.
- `frontend`: This directory contains the frontend application for the search engine.
- `scripts`: This directory contains the scripts for the project. Wil run only on Ubuntu at the time of writing.
    - `drop_database.py`: This script contains the drop database for the project.
    - `migration.py`: This script contains the migration for the database.
    - `init.sh`: This script contains the initialization for the project.
    - `*.sql`: These files contain the SQL queries for the project's migration.
- `.pre-commit-config.yaml`: This file contains the configuration for the pre-commit hooks.
- `.pylintrc`: This file contains the configuration for the pylint linter.
- `CHEATSHEET.md`: This file contains the cheatsheet for the project.
- `CODEOWNERS`. This file contains the GitHub code owners for the project.
- `docker-compose.yml`: Configuration for docker-compose for local development and deployment.
- `example.env`: This file contains the example environment variables for the project.
- `example.mysql.env`: This file is specifically for the MySQL's instance in the docker-compose file.
- `requirements.txt`: This file contains the required dependencies for the project's crawler & backend at
  production.