@echo off
cd /d "%~dp0"
php -S localhost:8080 -t public
pause
