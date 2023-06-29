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

# Set up

1. Create output directories and initialize environment variables.
```bash
cp -rf example.mysql.env .mysql.env
cp -rf example.env .env
```

2. Start the project

```bash
docker-compose up -d --build
```


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

3. Open the browser at `http://localhost:4000/`

# Docker

## Docker set up

Same as described in the section [Crawler](#crawler). Try this command if you have permission issues:

```bash
bash scripts/init.sh
```

# Team Members

- [Daniel Reimer](https://github.com/Seskahin)
- [Long Nguyen](https://github.com/longpollehn)
- [Lukas Listl](https://github.com/LukasListl)
- [Philipp Alber](https://github.com/coolusaHD)
