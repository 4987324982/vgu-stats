@echo off
chcp 65001 >nul
title ВГУstats - бэкенд
echo ============================================
echo  ВГУstats  -  запуск локального сервера
echo  Сайт откроется в браузере автоматически.
echo  Остановить сервер: закройте это окно.
echo ============================================
echo.
cd /d "%~dp0"
start "" http://localhost:8555/
python server.py
pause