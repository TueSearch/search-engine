#!/usr/bin/env bash

docker-compose -f "$1" down -v --remove-orphans