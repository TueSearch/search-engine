# TueSearch

This project contains the source code of the final project from the course modern search engines at the University of
Tübingen.

# Table of Contents
- [Crawler manager, backend, etc. set up](#crawler-manager-backend-etc-set-up)
- [Taking care of index and models](#taking-care-of-index-and-models)
- [Frontend](#frontend)

# Crawler manager, backend, etc. set up

1. Tear down everything

```bash
./scripts/tear_down.sh
```

2. Start the project. If the project starts for the first time, run 

```bash
./scripts/start_up.sh bootstrap
```

Any further time, the keyword `bootstrap` can be left out.

3. Run the crawler

```bash
./scripts/start_crawlers.sh 2
```

Change the number `2` to the number of crawlers you want to start. Start slowly and increase the number of crawlers
gracefully to see if everything works fine. Be polite to other websites and use at most `4` crawlers at the same time to avoid overloading the crawled websites.

4. Stop the crawler

```bash
./scripts/stop_crawlers.sh
```

# Taking care of index and models

Regularly the index for the search engine must be updated. Also the prediction model for URL's relevance must be fed with new data.

1. Update the index.

```bash
./scripts/update_index.sh
```

2. Update the mtrics.

```bash
./scripts/update_metrics.sh
```

3. Update the ML model and priority of jobs in the queue with new data. 

```bash
./scripts/update_priority.sh
```

4. Start the services, again

```bash
./scripts/start_up.sh
```

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
