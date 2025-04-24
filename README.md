# 🧠 Habit Tracker w/ Google Sheets Integration

This is a simple command-line habit tracker that uses the **Google Sheets API** to store, update, and manage daily habits in a spreadsheet. The goal is to create an accessible and persistent cloud-based habit tracking solution.

## 📋 Features

- ➕ Add new habits with a creation date and target completion time
- 📝 Edit existing habits and update timestamps
- ❌ Delete habits
- ✅ Mark habits as completed
- 📄 Show current list of habits
- 🔐 Secure authentication using OAuth 2.0

## 🔧 Technologies Used

- Python 3.12+
- Google Sheets API (via `google-api-python-client`)
- `pytz` for timezone handling
- `pytest` for testing

## 🚀 Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/your-username/habit-tracker-google-sheets.git
cd habit-tracker-google-sheets
```

### 2. Set up a virtual environment (optional)
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the application
```bash
python3 python3 src/package_lab13/main.py
google sheet url: https://docs.google.com/spreadsheets/d/1qIaMrjCJX4aTkngXQ2IwECH3FMuhXRLMy9-uEOWffa4/edit?gid=0#gid=0

```


### 5. Uploading Deployment
```bash
Here's the guide for more detail on Deployment:
https://packaging.python.org/en/latest/tutorials/packaging-projects/

Uploading python3 -m pip install --upgrade twine

python3 -m build

python3 -m twine upload --repository testpypi dist/*  

use your token

python3 python3 src/package_lab13/main.py
google sheet url: https://docs.google.com/spreadsheets/d/1qIaMrjCJX4aTkngXQ2IwECH3FMuhXRLMy9-uEOWffa4/edit?gid=0#gid=0


TEST run pytest

```
### 6. Installing Deployment & Running
```bash
to install  package from testpypi
Project's linke
https://test.pypi.org/project/lab13/0.0.3/

python3 -m pip install --index-url https://test.pypi.org/simple/ \
--no-deps lab13 --upgrade

or

pip install -i https://test.pypi.org/simple/ lab13==0.0.3


to run:
python3 src/package_lab13/main.py

google sheet url: https://docs.google.com/spreadsheets/d/1qIaMrjCJX4aTkngXQ2IwECH3FMuhXRLMy9-uEOWffa4/edit?gid=0#gid=0


TEST run: pytest

```










