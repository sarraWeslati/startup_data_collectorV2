@echo off

cd /d C:\Users\ASUS\Desktop\startup_data_collectorV2

call .venv\Scripts\activate.bat

python run_pipeline.py

pause