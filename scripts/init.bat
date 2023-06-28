@echo off

REM Initialize environment variables
copy /Y example.mysql.env .mysql.env
copy /Y example.env .env
copy /Y example.env .docker.env
powershell -Command "(gc .env) -replace 'WORKING_DIR=/app', 'WORKING_DIR=%CD%' | Out-File -encoding ASCII .env"
powershell -Command "(gc .env) -replace 'MYSQL_SEARCH_ENGINE_CONNECTION_HOST=mysql', 'MYSQL_SEARCH_ENGINE_CONNECTION_HOST=localhost' | Out-File -encoding ASCII .env"

REM Initialize output directories and environment variables
mkdir "%LOG_FILES_PATH%"
mkdir "%MODELS_PATH%"

REM Install dependencies
IF NOT EXIST venv (
  python -m venv venv
)
venv\Scripts\activate
pip install -r requirements.txt

REM Install pre-commit hooks
pre-commit install
