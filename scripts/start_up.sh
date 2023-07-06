#!/usr/bin/env bash
# Run on host

set -e

if [ $# -ge 1 ] && [ "$1" = "bootstrap" ]; then
  docker volume create database_volume_2
  docker volume create volume_2
fi
docker-compose down -v
docker-compose up --build -d mysql
docker-compose up --build -d phpmyadmin
sleep 10
docker-compose up --build --exit-code-from train_url_classifier train_url_classifier
docker-compose up --build --exit-code-from initialize_database initialize_database
docker-compose up -d --build manager
curl --retry 30 --retry-all-errors --retry-delay 1 "localhost:6000"
if [ $# -ge 1 ] && [ "$1" = "bootstrap" ]; then
  docker-compose up --build --exit-code-from worker worker
fi
if [ $# -ge 1 ] && [ "$1" = "bootstrap" ]; then
  docker-compose up --build --exit-code-from update_index update_index
  docker-compose up --build --exit-code-from update_metrics update_metrics
fi
docker-compose up --build -d backend_server
docker-compose up --build -d backend_mockup_server
docker-compose up --build -d backend_statistic_server
curl --retry 30 --retry-all-errors --retry-delay 1 "localhost:4000/search?q=tubingen"
curl --retry 30 --retry-all-errors --retry-delay 1 "localhost:4001/search?q=tubingen"
curl --retry 30 --retry-all-errors --retry-delay 1 "localhost:4002"
#docker-compose up --build -d frontend_server

if [ $# -ge 1 ] && [ "$1" = "bootstrap" ]; then
  touch pytest-results.xml
  chmod 777 pytest-results.xml
  docker-compose up --build --exit-code-from run_unit_tests run_unit_tests
fi
