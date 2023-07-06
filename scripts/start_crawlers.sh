#!/bin/bash

docker-compose up --build -d --scale loop_worker=$1 loop_worker