#!/usr/bin/env bash
# Run on host

./scripts/tear_down.sh
./scripts/start_database.sh
docker-compose up --build --exit-code-from train_url_classifier train_url_classifier