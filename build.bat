  @echo off
  REM Projektverzeichnis setzen
  cd /d "%~dp0"

  echo.
  echo Vorherige Build-Ordner löschen ...
  rmdir /s /q release >nul 2>&1

  echo.
  echo Starte PyInstaller ...
  pyinstaller --onefile --add-data "assets;assets" --add-data "data;data" main.py

  echo.
  echo Release-Ordner erstellen ...
  mkdir release

  echo.
  echo Kopiere Executable ...
  move /y "dist\main.exe" "release\JungleExplorer.exe" >nul

  echo.
  echo Kopiere Assets und Daten ...
  xcopy /s /i /y "assets" "release\assets\" >nul
  xcopy /s /i /y "data" "release\data\" >nul

  echo.
  echo Entferne temporäre Ordner ...
  rmdir /s /q build
  rmdir /s /q dist
  del /q main.spec

  echo.
  echo Fertig. Dein Spiel liegt jetzt in 'release\'.
  echo Starte JungleExplorer.exe im Release-Ordner, um das Spiel zu testen.
  pause