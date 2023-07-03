# TueSearch

This project contains the source code of the final project from the course modern search engines at the University of
Tübingen.

# Table of Contents
- [Local set up for development](#local-set-up-for-development)
- [Remote set up for deployment](#remote-set-up-for-deployment)
- [Crawler set up at local computer](#crawler-set-up-at-local-computer)
- [Frontend](#frontend)
- [Quality check](#quality-check)

# Local set up for development

1. Tear down everything

```bash
./scripts/teardown.sh docker-compose.yml
```

2. Create output directories and initialize environment variables.

```bash
cp -rf example.env .env 
cp -rf example.frontend.env frontend/.env
```

3. Start the project locally

```bash
./scripts/startup.sh docker-compose.yml
```

# Remote set up for deployment

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

# Crawler set up at local computer

Important note: when stop a crawler, stop gracefully so it has time to unreserve its reserved jobs.

1. Add the `.env` file from Discord to the root directory and start the crawler with

```bash
docker-compose -f docker-compose.yml up loop_worker
```

2. To start more than once crawler, do

```bash
docker-compose -f docker-compose.yml  up --build --scale loop_worker=2 loop_worker
```

Change the number `2` to the number of crawlers you want to start. Start slowly and increase the number of crawlers
gracefully to see if everything works fine.

Be polite to other websites and use at most `4` crawlers at the same time to avoid overloading the crawled websites.

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

# Quality check

Some regularly used SQL queries to check quality:

- Test relevance ratio:

```sql
SELECT count(*) FROM `documents` where relevant = 1;
SELECT count(*) FROM `documents` where relevant = 0;
```

- Update priority list:
```sql
SELECT j.url, j.priority from jobs as j join documents as d where j.id = d.job_id and d.relevant = 1;
```

- Update block list:
```sql
SELECT j.url, j.priority from jobs as j join documents as d where j.id = d.job_id and d.relevant = 0;
```


# Team Members

- [Daniel Reimer](https://github.com/Seskahin)
- [Long Nguyen](https://github.com/longpollehn)
- [Lukas Listl](https://github.com/LukasListl)
- [Philipp Alber](https://github.com/coolusaHD)
