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
python3 main.py
```











