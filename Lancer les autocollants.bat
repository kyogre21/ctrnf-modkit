@echo off
rem Lance la fenetre des autocollants (Python 3.10 ou plus recent ; numpy et Pillow sont installes au besoin).
cd /d "%~dp0"
set PY=
where py >nul 2>nul && py -3 -c "import sys; sys.exit(sys.version_info < (3, 10))" >nul 2>nul && set PY=py -3
if not defined PY python -c "import sys; sys.exit(sys.version_info < (3, 10))" >nul 2>nul && set PY=python
if not defined PY (
  echo Python 3.10 ou plus recent est necessaire : https://www.python.org/downloads/
  start "" https://www.python.org/downloads/
  pause
  exit /b
)
%PY% -c "import numpy, PIL" >nul 2>nul || (
  echo Premiere utilisation : installation de numpy et Pillow...
  %PY% -m pip install --user -r requirements.txt || (pause & exit /b)
)
if "%PY%"=="py -3" (start "" pyw -3 -m ctrnf_stickers) else (start "" pythonw -m ctrnf_stickers)
