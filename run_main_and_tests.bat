@echo off
echo Starting main.py...
cd HW_1
start cmd /k uvicorn main:app
echo Running tests...
cd..
pytest "HW_1/tests.py" & pytest "tests/test_homework_1.py" & pause
