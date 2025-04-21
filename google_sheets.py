from google.oauth2.credentials import Credentials
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

def show_habits(creds, spreadsheet_id):
    data = get_sheet_data(creds, spreadsheet_id)
    if is_habits_empty(data):
        print("\nNo habits found.\n")
        return
    
    print("\nHabit List:")
    for row in data:
        # assuming columns are Date, Habit, …
        print("  " + " | ".join(row))
    print() # print a newline

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

'''is_habits_empty checks if the Habit Tracker spreadsheet is empty and returns True or False accordingly.'''
def is_habits_empty(data):
    if not data:
        return True
    else:
        return False

'''print_current_habits displays the current habits the user has entered with a number identifier for selection.'''
def print_current_habits(data):
    print("\nCurrent Habits:")
    for i, row in enumerate(data, start=1):
        print(f"  {i}. {row[0]}")

'''edit_habit allows the user to modify an existing habit in the Google Sheet.'''
def edit_habit(creds, spreadsheet_id):
    service = build('sheets', 'v4', credentials=creds)
    sheet_name = 'Habit Tracker'

    data = get_sheet_data(creds, spreadsheet_id)

    if is_habits_empty(creds, spreadsheet_id, data):
        print("\nNo habits found to edit.\n")
        return

    print_current_habits(data)

    try:
        choice = int(input("\nEnter the number of the habit to edit: "))
        if choice < 1 or choice > len(data):
            print("Invalid selection.\n")
            return
    except ValueError:
        print("Invalid input. Please enter a number.\n")
        return

    new_value = input("Enter the new habit description: ").strip()
    if not new_value:
        print("No changes made.\n")
        return
    
    # Row number in the sheet = index + 2 (1-based sheet rows, plus header)
    row_number = choice + 1
    cell_range = f"{sheet_name}!A{row_number}"
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

'''delete_habit allows the user to remove a habit from their Habit Tracker Sheet'''
def delete_habit(creds, spreadsheet_id):
    service = build('sheets', 'v4', credentials=creds)
    sheet_name = 'Habit Tracker'
    values = get_sheet_data(creds, spreadsheet_id)

    if is_habits_empty(creds, spreadsheet_id, values):
        print("\nNo habits found to delete.\n")
        return

    habits = [row[0] for row in values if row]  # filter out empty rows

    print("\nCurrent Habits:")
    for idx, habit in enumerate(habits, 1):
        print(f"{idx}. {habit}")

    try:
        index = int(input("\nEnter the number of the habit to delete: ")) - 1
        habit_to_delete = habits[index]
    except (ValueError, IndexError):
        print("❌ Invalid selection.\n")
        return

    range_to_clear = f"{sheet_name}!A{index + 2}"  # A2 is the first habit
    service.spreadsheets().values().clear(spreadsheetId=spreadsheet_id, range=range_to_clear, body={}).execute()
    print(f"✅ Habit '{habit_to_delete}' deleted successfully!\n")

'''mark_habit_complete changes the completion status of a habit.'''
def mark_habit_complete(creds, spreadsheet_id):
    service = build('sheets', 'v4', credentials=creds)
    sheet_name = 'Habit Tracker'

    # Get sheet data
    data = get_sheet_data(creds, spreadsheet_id)

    # Check if the habit list is empty before proceeding
    if is_habits_empty(creds, spreadsheet_id, data):
        print("\nNo habits found to mark complete.\n")
        return

    # Display habit list to the user
    print_current_habits(data)

    # Prompt user for selection
    try:
        choice = int(input("\nEnter the number of the habit to mark complete: "))
        if choice < 1 or choice > len(data):
            print("Invalid selection.\n")
            return
    except ValueError:
        print("Invalid input. Please enter a number.\n")
        return

    # Get habit name for confirmation message
    selected_row = data[choice - 1]
    habit_name = selected_row[0] if len(selected_row) > 0 else "Unknown Habit"

    # Check if the habit is already marked complete
    status = selected_row[3] if len(selected_row) > 3 else ""
    if status == "✅":
        print(f"Habit '{habit_name}' is already marked complete.\n")
        return

    # Row number in the sheet = index + 2 (1-based sheet rows, plus header)
    row_number = choice + 1
    cell_range = f"{sheet_name}!D{row_number}"
    update_body = {'values': [["✅"]]}

    try:
        service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=cell_range,
            valueInputOption="RAW",
            body=update_body
        ).execute()
        print(f"\n✅ Habit '{habit_name}' marked complete!\n")
    except Exception as e:
        print(f"❌ Error updating habit: {e}\n")
