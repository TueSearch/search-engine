#!/usr/bin/env bash

set -e

if [ "$1" == "prod.docker-compose.yml" ]; then
  docker-compose -f "$1" down
  docker-compose -f "$1" up --build -d prod_mysql prod_mysql
  docker-compose -f "$1" up --build --exit-code-from prod_build_index prod_build_index
  docker-compose -f "$1" up --build --exit-code-from prod_build_metrics prod_build_metrics
  ./scripts/startup.sh "$1"
else
  echo "Unknown docker-compose file: $1"
  echo "Usage:"
  echo "  ./scripts/start_index.sh prod.docker-compose.yml"
  exit 1
fi
