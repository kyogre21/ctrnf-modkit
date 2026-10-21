@echo off
rem Fabrique dist\CTRNF-ModKit.exe (Python 3.10 ou plus recent ; un Python a part est cree dans build\venv).
cd /d "%~dp0"
if not exist build\venv\Scripts\python.exe (
  py -3 -m venv build\venv || python -m venv build\venv || (pause & exit /b)
  build\venv\Scripts\python -m pip install --upgrade pip
  build\venv\Scripts\python -m pip install pyinstaller sv-ttk==2.6.1 -r ..\autocollants\requirements.txt || (pause & exit /b)
)
build\venv\Scripts\python -m PyInstaller --noconfirm --onefile --windowed --noupx --collect-data sv_ttk --name CTRNF-ModKit ^
  --paths "%~dp0." --paths "%~dp0..\randomizer" --paths "%~dp0..\autocollants" ^
  --add-data "%~dp0..\autosplitter\CTRNF.asl;autosplitter" ^
  --distpath dist --workpath build\work --specpath build lanceur.py
echo.
echo Exe : %~dp0dist\CTRNF-ModKit.exe
if not "%1"=="auto" pause
