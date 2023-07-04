#!/usr/bin/env bash

set -e

if [ "$1" == "prod.docker-compose.yml" ]; then
  docker-compose -f "$1" down
  docker-compose -f "$1" up --build -d prod_mysql prod_mysql
  docker-compose -f "$1" up --build --exit-code-from build_index build_index
  docker-compose -f "$1" up --build --exit-code-from build_metrics build_metrics
else
  echo "Unknown docker-compose file: $1"
  echo "Usage:"
  echo "  ./scripts/start_index.sh prod.docker-compose.yml"
  exit 1
fi
