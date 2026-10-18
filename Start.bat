@echo off
cd /d "%~dp0"
py -m pip install --quiet --upgrade instaloader
where pyw >nul 2>&1 && (start "" pyw ig_gui.py) || (py ig_gui.py)
