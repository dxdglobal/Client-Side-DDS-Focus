@echo off
taskkill /f /im app.exe >nul 2>&1
pyinstaller --clean --noconfirm --onefile --windowed --add-data "templates;templates" --add-data "static;static" --hidden-import flaskwebgui app.py
pause
