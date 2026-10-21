@echo off
rem Lance la fenetre du randomizer depuis le code source (Python 3.10 ou plus recent).
rem Sans Python : utiliser CTRNF-Randomizer.exe (page Releases), qui n'a besoin de rien.
cd /d "%~dp0"
where pyw >nul 2>nul && (start "" pyw -3 -m ctrnf_rando.gui & exit /b)
python -c "import sys; sys.exit(sys.version_info < (3, 10))" >nul 2>nul && (start "" pythonw -m ctrnf_rando.gui & exit /b)
echo.
echo Ce dossier est le code source du randomizer : il a besoin de Python pour se lancer.
echo.
echo Pas besoin d'installer quoi que ce soit : telechargez plutot le programme tout pret
echo CTRNF-Randomizer.exe dans la page des Releases (la page va s'ouvrir) :
echo   https://github.com/kyogre21/ctrnf-randomizer/releases/latest
echo puis lancez CTRNF-Randomizer.exe.
echo.
start "" https://github.com/kyogre21/ctrnf-randomizer/releases/latest
pause
