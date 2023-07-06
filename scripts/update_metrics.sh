#!/usr/bin/env bash
# Run on host

./scripts/tear_down.sh
./scripts/start_database.sh
docker-compose up --build --exit-code-from update_metrics update_metrics
