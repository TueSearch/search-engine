#!/usr/bin/env bash
# Run on host

docker-compose up --build -d mysql
docker-compose up --build -d phpmyadmin
docker-compose up --build -d backend_statistic_server