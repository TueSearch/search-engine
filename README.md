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

2. Start the project locally

```bash
./scripts/startup.sh docker-compose.yml
```

and tear down with

```bash
./scripts/teardown.sh docker-compose.yml
```

3. Start the project on the server. Create unmanaged volumes (root access required)

```bash
sudo docker volume create prod_tuesearch_database
```

and in the similar manner

```bash
sudo docker volume create prod_tuesearch
```

Change passwords in `.env` and start the containers with

```bash
./scripts/startup.sh prod.docker-compose.yml
```

Analog, tear down with

```bash
./scripts/teardown.sh prod.docker-compose.yml
```

# Crawler

## Crawler usage

The crawler should be used at local computer.

1. Once the setup is done, you can start the crawling process by

```bash
docker-compose -f docker-compose.yml up worker
```

2. To crawl in loop (more than once), remove `-n 1` in `docker-compose.yml`.

3. To start up more than one crawler, remove `name: worker` and do

```bash
docker-compose -f docker-compose.yml  up --build --scale worker=12 worker
```

4. To send the crawler's data to remote database, change the variables `CRAWLER_MANAGER_HOST`
   and `CRAWLER_MANAGER_PASSWORD` in `.env`.

# Backend

## Backend set up

Same as described in the section [Crawler](#crawler).

## Backend usage

1. After collecting enough data, you can build the index as

```bash

docker-compose -f docker-compose.yml up build_index
```

This step should be repeated regularly to keep the index fresh. Replace `docker-compose.yml`
with `prod.docker-compose.yml` for production.

2. For the ranking, the metrics must be built as

```bash
docker-compose -f docker-compose.yml up build_metrics
```

This step should be repeated regularly to keep the metrics fresh. Replace `docker-compose.yml`
with `prod.docker-compose.yml` for production.

4. Test the API with

```bash
curl http://localhost:4000/search?q=tubingen
```

# Frontend

1. Start mock up server

```bash
docker-compose -f docker-compose.yml up --build backend_mockup_server
```

and test the mock API at `localhost:4001/search?q=tubingen`

2. Install dependencies

```bash
npm install
```

3. Start the frontend

```bash
npm run dev
```

4. Open the browser at `http://localhost:5000/`

# Team Members

- [Daniel Reimer](https://github.com/Seskahin)
- [Long Nguyen](https://github.com/longpollehn)
- [Lukas Listl](https://github.com/LukasListl)
- [Philipp Alber](https://github.com/coolusaHD)
