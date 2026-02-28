@echo off
REM News Intelligence System - Quick Start
echo Starting News Intelligence System...
echo.
echo 1. Ensure Endee is running: docker compose up -d
echo 2. Ensure Ollama is running: ollama serve
echo.
python main.py
