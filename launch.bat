@echo off
REM Create virtual environment if it doesn't exist
if not exist venv (
    python -m venv venv
)

REM Open PowerShell, activate venv, install requirements, run Streamlit, and leave shell open
powershell -NoExit -NoProfile -ExecutionPolicy Bypass -Command ^
  "& { .\venv\Scripts\Activate.ps1; pip install -r requirements.txt; streamlit run .\start_streamlit.py }"
