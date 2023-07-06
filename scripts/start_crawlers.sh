#!/bin/bash

docker-compose up --build --scale loop_worker=$1 loop_worker