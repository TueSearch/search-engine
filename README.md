# TueSearch

This project contains the source code of the final project from the course modern search engines at the University of
Tübingen.

## Table of Contents

- [TueSearch](#tuesearch)
    - [Table of Contents](#table-of-contents)
- [Set up](#crawler-set-up)
- [Crawler](#crawler)
    - [Crawler usage](#crawler-usage)
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

3. Start the project on the server. Create external volumes

```bash
docker volume create prod_tuesearch_database
docker volume create prod_tuesearch
```

Change passwords in `.env` and start the containers with

```bash
./scripts/startup.sh prod.docker-compose.yml
```

Analog, tear down with

```bash
./scripts/teardown.sh prod.docker-compose.yml
```

And remove the external volumes (if needed) with 

```bash
docker volume rm prod_tuesearch_database
docker volume rm prod_tuesearch
```

# Crawler

## Crawler usage

1. Once the setup is done, you can start the crawling process at `local computer` by 
changing the variables 
- `CRAWLER_MANAGER_HOST` 
- `CRAWLER_MANAGER_PASSWORD`
- `CRAWL_WORKER_BATCH_SIZE`
in `.env` and run

```bash
docker-compose -f docker-compose.yml up loop_worker
```

2. To start more than once crawler, do

```bash
docker-compose -f docker-compose.yml  up --build --scale loop_worker=12 loop_worker
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
