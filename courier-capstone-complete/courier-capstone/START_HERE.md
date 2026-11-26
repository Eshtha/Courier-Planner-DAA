# Start here

- courier-planner/ : the complete project (this is what you submit)
- Courier_Planning_System_Report.pdf : the report
- extras/ : viva notes and the UI redesign prompt (for you; no need to submit)

## 1. Set up
Install Python 3.9+ (tick "Add Python to PATH") and VS Code.
Extract the zip. In VS Code: File > Open Folder > the courier-planner folder that
contains main.py. Then Terminal > New Terminal.

## 2. Install and test
    python -m pip install -r requirements.txt
    python -m unittest discover -s tests -t . -v

## 3. Run
    python main.py --dataset small
    python app.py
Open http://127.0.0.1:8000 . Press Ctrl+C in the terminal to stop.
