@echo off
REM Activar entorno virtual y ejecutar satchange.py

REM Cambia al directorio donde está el script si es necesario
cd /d %~dp0

REM Activar entorno virtual y ejecutar
call .venv\Scripts\activate.bat
python satchange.py
