@echo off
title FREESHION - Luxury E-Commerce Server
color 0A
echo ===================================================
echo     FREESHION - LUXURY MENSWEAR E-COMMERCE
echo ===================================================
echo.
echo [1/2] Kiem tra moi truong va CSDL...
python database.py
echo.
echo [2/2] Khoi dong may chu Flask tai http://127.0.0.1:5000 ...
echo Nhan Ctrl + C de dung may chu.
echo.
python app.py
pause
