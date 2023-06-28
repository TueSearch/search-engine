# Table of Contents
- [Table of Contents](#table-of-contents)
- [Crawler cheatsheet](#crawler-cheatsheet)
    - [Show directories' content](#show-directories-content)
    - [Show logs](#show-logs)
- [Backend cheatsheet](#backend-cheatsheet)
    - [Test the API](#test-the-api)
- [Docker cheatsheet](#docker-cheatsheet)
    - [Show containers](#show-containers)
    - [Show logs](#show-logs-1)
    - [Enter containers](#enter-containers)
    - [Restart the services](#restart-the-services)
- [Clean up everything](#clean-up-everything)

# Crawler cheatsheet

## Show directories' content

```bash
ls -lha /opt/tuesearch/data/
```

```bash
ls -lha /opt/tuesearch/log/
```

# Backend cheatsheet

## Test the API

```bash
curl http://localhost:5000/search?q=tübingen
```

# Docker cheatsheet

## Show containers

```bash
docker container ps
```

## Run only one service

```bash
docker-compose up initialize_database
```

```bash
docker-compose up crawl
```

```bash
docker-compose up build_inverted_index
```

```bash
docker-compose up build_ranker
```

## Show logs

```bash
docker container logs mysql
```

```bash
docker container logs initialize_database
```

```bash
docker container logs crawl
```

```bash
docker container logs build_inverted_index
```

```bash
docker container logs build_ranker
```

```bash
docker container logs backend_server
```

## Enter containers

```bash
docker exec -it mysql bash
```

```bash
docker exec -it initialize_database bash
```

```bash
docker exec -it crawl bash
```

```bash
docker exec -it build_inverted_index bash
```

```bash
docker exec -it build_ranker bash
```

```bash
docker exec -it backend_server bash
```

## Restart the services

```bash
docker-compose down
docker-compose up -d --build
```

# Clean up everything

In case of unexplainable errors, try to clean up everything and start from scratch.

```bash
docker-compose down
docker system prune -a
docker volume prune --force
sudo rm -rf /opt/tuesearch
```
