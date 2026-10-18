@echo off
rem Lance la fenetre du randomizer (Python 3.10 ou plus recent).
cd /d "%~dp0"
where pyw >nul 2>nul && (start "" pyw -3 -m ctrnf_rando.gui & exit /b)
where pythonw >nul 2>nul && (start "" pythonw -m ctrnf_rando.gui & exit /b)
where python >nul 2>nul && (python -m ctrnf_rando.gui & if not errorlevel 1 exit /b)
echo.
echo Python est introuvable (ou trop ancien).
echo Installez Python 3.10 ou plus recent depuis https://www.python.org/downloads/
echo en cochant "Add python.exe to PATH" pendant l'installation, puis relancez ce fichier.
echo.
pause
