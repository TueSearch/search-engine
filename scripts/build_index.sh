#!/usr/bin/env bash

docker-compose down
docker-compose up --build -d mysql
docker-compose up --build --exit-code-from build_index build_index
docker-compose up --build --exit-code-from build_metrics build_metrics
