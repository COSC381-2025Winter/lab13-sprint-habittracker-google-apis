from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime
from googleapiclient.discovery import build

'''create_sheet uses the user's Google credentials and a sheet title they entered to create a new Google Spreadsheet '''
def create_sheet(creds, title: str):
    """Create a new Google Sheet with a worksheet named 'Habit Tracker' and return its spreadsheetId."""
    service = build('sheets', 'v4', credentials=creds)

    body = {
        'properties': {'title': title},  # Spreadsheet title
        'sheets': [
            {
                'properties': {
                    'title': 'Habit Tracker'  # Name of the first sheet/tab
                }
            }
        ]
    }

    sheet = service.spreadsheets().create(
        body=body,
        fields='spreadsheetId'
    ).execute()

    return sheet['spreadsheetId']

'''get_sheet_data retrieves data from a Google Sheet using the Google Sheets API.'''
def get_sheet_data(creds, spreadsheet_id):
    service = build('sheets', 'v4', credentials=creds)

    range_name = 'Habit Tracker!A2:E'  # Adjust range as needed
    sheet = service.spreadsheets()
    result = sheet.values().get(
        spreadsheetId=spreadsheet_id,
        range=range_name
    ).execute()

    values = result.get('values', [])
    return values

'''add_habit adds a new habit to the Google Sheet.'''
def add_habit(creds, spreadsheet_id, habit):
    service = build('sheets', 'v4', credentials=creds)
    sheet_name = 'Habit Tracker'

    new_row = [habit]
    range_name = f'{sheet_name}!A2'
    body = {'values': [new_row]}

    service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range=range_name,
        valueInputOption="RAW",
        body=body
    ).execute()

    print(f"\n✅ Habit '{habit}' added successfully!\n")

'''edit_habit allows the user to modify an existing habit in the Google Sheet.'''
def edit_habit(creds, spreadsheet_id):
    service = build('sheets', 'v4', credentials=creds)
    sheet_name = 'Habit Tracker'

    data = get_sheet_data(creds, spreadsheet_id)
    if not data:
        print("No habits to edit.\n")
        return

    print("\nCurrent Habits:")
    for i, row in enumerate(data, start=1):
        print(f"  {i}. {row[0]}")

    try:
        choice = int(input("\nEnter the number of the habit to edit: "))
        update_timestamp(creds,spreadsheet_id,choice+1)

        if choice < 1 or choice > len(data):
            print("Invalid selection.")
            return
    except ValueError:
        print("Invalid input. Please enter a number.")
        return

    new_value = input("Enter the new habit description: ").strip()
    if not new_value:
        print("No changes made.")
        return

    cell_range = f"{sheet_name}!A{choice + 1}"
    update_body = {'values': [[new_value]]}

    try:
        service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=cell_range,
            valueInputOption="RAW",
            body=update_body
        ).execute()
        print(f"\n✅ Habit updated to '{new_value}' successfully!\n")
    except Exception as e:
        print(f"❌ Error updating habit: {e}")

def update_timestamp(creds, spreadsheet_id, row_index):
    service = build('sheets', 'v4', credentials=creds)

    # Current date and time
    now = datetime.now().strftime('%Y-%m-%d %H:%M')

    # Target range in column E for the given row
    range_to_update = f'Habit Tracker!E{row_index}'

    body = {
        'values': [[now]]
    }

    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=range_to_update,
        valueInputOption='RAW',
        body=body
    ).execute()

    print(f"Timestamp updated in E{row_index}: {now}")
