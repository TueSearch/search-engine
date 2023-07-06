# TueSearch

This project contains the source code of the final project from the course modern search engines at the University of
Tübingen.

# Table of Contents
- [Crawler manager, backend, etc. set up](#crawler-manager-backend-etc-set-up)
- [Frontend](#frontend)

# Crawler manager, backend, etc. set up

0. Create volumes and set up `.env` file.

```bash
docker volume create database_volume_2
docker volume create volume_2
```

1. Tear down everything

```bash
./scripts/tear_down.sh
```

2. Start the project. If the project is started for the first time on the computer, run 

```bash
./scripts/start_up.sh bootstrap
```

Any further time

```bash
./scripts/start_up.sh
```

3. Run the crawler

```bash
docker-compose up --build --scale loop_worker=2 loop_worker
```

Change the number `2` to the number of crawlers you want to start. Start slowly and increase the number of crawlers
gracefully to see if everything works fine. Be polite to other websites and use at most `4` crawlers at the same time to avoid overloading the crawled websites.

# Frontend

1. Set up the mock API 
```bash
docker-compose up --build backend_mockup_server
```
and test the API at `localhost:4001/search?q=tubingen`.

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
