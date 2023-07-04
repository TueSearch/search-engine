#!/usr/bin/env bash

set -e

if [ "$1" == "docker-compose.yml" ]; then
  if [ $# -ge 2 ] && [ "$2" = "test" ]; then
     touch pytest-results.xml
     chmod 777 pytest-results.xml
  fi
  docker-compose -f "$1" down -v
  docker-compose -f "$1" up --build -d mysql mysql
  sleep 5
  docker-compose -f "$1" up --build --exit-code-from initialize_database initialize_database
  docker-compose -f "$1" up -d --build manager
  curl --retry 30 --retry-all-errors --retry-delay 1 "localhost:6000"
  docker-compose -f "$1" up --build --exit-code-from worker worker
  docker-compose -f "$1" up --build --exit-code-from build_index build_index
  docker-compose -f "$1" up --build --exit-code-from build_metrics build_metrics
  docker-compose -f "$1" up --build -d backend_server
  curl --retry 30 --retry-all-errors --retry-delay 1 "localhost:4000/search?q=tubingen"
  if [ $# -ge 2 ] && [ "$2" = "test" ]; then
    docker-compose -f "$1" up --build --exit-code-from run_unit_tests run_unit_tests
  fi
elif [ "$1" == "prod.docker-compose.yml" ]; then
  docker-compose -f "$1" down
  docker-compose -f "$1" up --build -d prod_mysql prod_mysql
  sleep 5
  docker-compose -f "$1" up --build --exit-code-from prod_initialize_database prod_initialize_database
  docker-compose -f "$1" up --build -d prod_backend_server
  docker-compose -f "$1" up --build -d prod_frontend_server
  docker-compose -f "$1" up --build -d prod_nginx
  docker-compose -f "$1" up --build -d prod_phpmyadmin
  docker-compose -f "$1" up -d --build prod_manager
else
  echo "Unknown docker-compose file: $1"
  echo "Usage:"
  echo "  ./scripts/startup.sh docker-compose.yml [test]"
  echo "  ./scripts/startup.sh prod.docker-compose.yml"
  exit 1
fi
