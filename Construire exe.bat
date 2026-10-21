@echo off
rem Fabrique dist\CTRNF-Stickers.exe (Python 3.10 ou plus recent ; un Python a part est cree dans build\venv).
cd /d "%~dp0"
if not exist build\venv\Scripts\python.exe (
  py -3 -m venv build\venv || python -m venv build\venv || (pause & exit /b)
  build\venv\Scripts\python -m pip install --upgrade pip
  build\venv\Scripts\python -m pip install pyinstaller -r requirements.txt || (pause & exit /b)
)
build\venv\Scripts\python -m PyInstaller --noconfirm --onefile --windowed --name CTRNF-Stickers ^
  --distpath dist --workpath build\work --specpath build lanceur.py
echo.
echo Exe : %~dp0dist\CTRNF-Stickers.exe
if not "%1"=="auto" pause
