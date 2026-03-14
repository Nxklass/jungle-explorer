@echo off
chcp 65001
echo Starting Jungle Explorer...

REM Dynamisch ins Projekt-Stammverzeichnis wechseln (Elternordner von jungle_explorer)
set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..") do set "PROJECT_DIR=%%~fI"
cd /d "%PROJECT_DIR%"

REM Prüfen, ob das Verzeichnis existiert
if not exist "%CD%" (
    echo Fehler: Das Verzeichnis %CD% wurde nicht gefunden.
    pause
    exit /b 1
)

REM Python-Skript als Modul ausführen
py -3 -m jungle_explorer.main
if %ERRORLEVEL% NEQ 0 python -m jungle_explorer.main
if %ERRORLEVEL% NEQ 0 (
    echo Fehler: Das Spiel ist abgestürzt. Überprüfe die Fehlermeldung oben.
)

REM Fenster offen lassen für Fehlermeldungen
pause