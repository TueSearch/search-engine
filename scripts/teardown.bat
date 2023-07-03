@echo off

docker-compose -f "%~1" down -v --remove-orphans
