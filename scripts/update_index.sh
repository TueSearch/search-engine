#!/usr/bin/env bash
# Run on host

./script_teardown.sh
docker-compose up --build -d mysql
docker-compose up --build --exit-code-from update_index update_index
