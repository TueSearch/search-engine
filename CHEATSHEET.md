# Docker cheatsheet

## Restart

```bash
docker-compose up -d --build
```

## Show containers

```bash
docker container ps
```

## Run only one service

```bash
docker-compose up -d initialize_database
```

```bash
docker-compose up -d crawl
```

```bash
docker-compose up build_inverted_index
```

```bash
docker-compose up build_ranker
```

```bash
docker-compose up -d backend_server
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
```

```bash
docker-compose up -d --build
```

# Clean up everything

In case of unexplainable errors, try to clean up everything and start from scratch.

```bash
docker-compose down
```

```bash
docker system prune -a
```

```bash
docker volume prune --force
```

```bash
sudo rm -rf /opt/tuesearch
```
