# TueSearch

This project contains the source code of the final project from the course modern search engines at the University of
Tübingen.

# Table of Contents
- [Crawler set up](#crawler-set-up)
- [Frontend](#frontend)

# Crawler set up

0. Create volumes


```bash
docker volume create database_volume_1
docker volume create volume_1
```

1. Tear down everything

```bash
./scripts/teardown.sh
```

2. Create output directories and initialize environment variables.

```bash
cp -rf example.env .env 
cp -rf example.frontend.env frontend/.env
```

3. Start the project locally

```bash
./scripts/startup.sh
```

# Crawler set up at local computer

Important note: when stop a crawler, stop gracefully so it has time to unreserve its reserved jobs.

1. Move the same `.env` file from server to local.

```bash
docker-compose up --build loop_worker
```

2. To start more than once crawler, do

```bash
docker-compose up --build --scale loop_worker=2 loop_worker
```

Change the number `2` to the number of crawlers you want to start. Start slowly and increase the number of crawlers
gracefully to see if everything works fine.

Be polite to other websites and use at most `4` crawlers at the same time to avoid overloading the crawled websites.

# Frontend

1. Test the mock API at `localhost:4001/search?q=tubingen`

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
