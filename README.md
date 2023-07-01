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
cp -rf example.env .env
cp -rf example.frontend.env frontend/.env
```

2. Start the project

```bash
docker-compose up -d --build
```

# Crawler

## Crawler usage

To use the web crawler, follow the workflow below:

1. Once the setup is done, you can start the crawling process using

```bash
docker-compose up worker
```

2. To crawl in loop (more than once), remove `-n 1` in `docker-compose.yml`.

3. To start up more than one crawler

```
docker-compose up --scale worker=12
```

4. To send crawled data to remote server, set

```dotenv
# Where to retrieve jobs
CRAWLER_MANAGER_PORT=6000

# Where to retrieve jobs
CRAWLER_MANAGER_HOST=http://manager:${CRAWLER_MANAGER_PORT}

# Password
CRAWLER_MANAGER_PASSWORD=pw
```

to desired remove server

# Backend

## Backend set up

Same as described in the section [Crawler](#crawler).

## Backend usage

1. After collecting enough data, you can build the index as

```bash

docker-compose up build_index
```

This step should be repeated regularly to keep the index fresh.

2. For the ranking, the metrics must be built as

```bash
docker-compose up build_metrics
```

This step should be repeated regularly to keep the metrics fresh.

4. Test the API with

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

3. Open the browser at `http://localhost:5000/`

# Team Members

- [Daniel Reimer](https://github.com/Seskahin)
- [Long Nguyen](https://github.com/longpollehn)
- [Lukas Listl](https://github.com/LukasListl)
- [Philipp Alber](https://github.com/coolusaHD)
