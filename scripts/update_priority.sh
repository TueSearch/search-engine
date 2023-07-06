#!/usr/bin/env bash
# Run on host

./script_teardown.sh
docker-compose down
docker-compose up --build -d mysql
docker-compose up --build --exit-code-from update_priority update_priority