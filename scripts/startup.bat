@echo off

if "%~1"=="docker-compose.yml" (
    if "%~2"=="test" (
        echo. 2> pytest-results.xml
        attrib -r pytest-results.xml
    )
    docker-compose -f "%~1" down -v
    docker-compose -f "%~1" up --build -d mysql mysql
    timeout /t 10
    docker-compose -f "%~1" up --build --exit-code-from initialize_database initialize_database
    docker-compose -f "%~1" up -d --build manager
    curl --retry 30 --retry-all-errors --retry-delay 1 "localhost:6000"
    docker-compose -f "%~1" up --build --exit-code-from worker worker
    docker-compose -f "%~1" up --build --exit-code-from build_index build_index
    docker-compose -f "%~1" up --build --exit-code-from build_metrics build_metrics
    docker-compose -f "%~1" up --build -d backend_server
    curl --retry 30 --retry-all-errors --retry-delay 1 "localhost:4000/search?q=tubingen"
    if "%~2"=="test" (
        docker-compose -f "%~1" up --build --exit-code-from run_unit_tests run_unit_tests
    )
) else if "%~1"=="prod.docker-compose.yml" (
    docker-compose -f "%~1" down
    docker-compose -f "%~1" up --build -d prod_mysql prod_mysql
    timeout /t 10
    docker-compose -f "%~1" up --build --exit-code-from prod_initialize_database prod_initialize_database
    docker-compose -f "%~1" up -d --build prod_manager
    docker-compose -f "%~1" up --build --exit-code-from prod_worker prod_worker
    docker-compose -f "%~1" up --build --exit-code-from prod_build_index prod_build_index
    docker-compose -f "%~1" up --build --exit-code-from prod_build_metrics prod_build_metrics
    docker-compose -f "%~1" up --build -d prod_backend_server
    docker-compose -f "%~1" up --build -d prod_frontend_server
    docker-compose -f "%~1" up --build -d prod_nginx
    docker-compose -f "%~1" up --build -d prod_phpmyadmin
) else (
    echo Unknown docker-compose file: %~1
    echo Usage:
    echo   .\scripts\startup.bat docker-compose.yml test
    echo   .\scripts\startup.bat prod.docker-compose.yml
    exit /b 1
)
