@echo off
rem Lance le CTRNF Mod Kit depuis le code source (Python 3.10 ou plus recent ; numpy et Pillow pour les autocollants).
cd /d "%~dp0"
where pyw >nul 2>nul && (start "" pyw -3 -m ctrnf_modkit & exit /b)
start "" pythonw -m ctrnf_modkit
