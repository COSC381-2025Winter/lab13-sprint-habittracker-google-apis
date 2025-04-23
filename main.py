from google_auth_oauthlib.flow import InstalledAppFlow
from google_sheets import create_sheet, get_sheet_data, add_habit, edit_habit, show_habits, delete_habit, mark_habit_complete, update_timestamp
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']  # define required permissions from user's Google account

'''authenticate_user authenticates the user's Google account using OAuth flow, ensuring that the program has the necessary permissions to create a new Google Spreadsheet, make edits to it as necessary, and make changes to their Google Calendar. Upon successful authentication, credentials are returned.'''
def authenticate_user():
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)  # create the user authentication window with necessary permissions
    creds = flow.run_local_server(port=0)  # run user authentication window 
    print()  # print newline after the browser‑redirect log
    return creds

''' Check to see if the user entered a valid Google Sheets URL. '''
def is_valid_spreadsheet(creds, spreadsheet_id):
    try:
        service = build('sheets', 'v4', credentials=creds)
        service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        return True
    except HttpError as error:
        if error.resp.status in [403, 404]:
            print("Error: Unable to access the spreadsheet. Make sure the URL is valid and shared with your account.")
        else:
            print(f"An unexpected error occurred: {error}")
        return False

''' Ask the user if they want to reuse an existing sheet or create a new one. Returns the chosen spreadsheet_id. '''
def choose_or_create_sheet(creds):
    choice = input("Use existing Habit Tracker sheet? (y/n): ").strip().lower()
    while True:
        if choice == 'y':
            spreadsheet_url = input("Copy and paste your Google Sheet URL here: ").strip()
            try:
                spreadsheet_id = spreadsheet_url.split("/d/")[1].split("/edit")[0]  # try splitting the Google Sheet URL to get only the spreadsheet id
                if is_valid_spreadsheet(creds, spreadsheet_id):
                    print(f"Using existing sheet.\n")
                    return spreadsheet_id
                else:
                    print("Please enter a valid and accessible spreadsheet URL.\n")
            except IndexError:
                print("That doesn't look like a valid Google Sheet URL. Try again.\n")
        elif choice == 'n':
            title = input("Enter a title for your new Habit Tracker sheet: ").strip()
            spreadsheet_id = create_sheet(creds, title)
            print(f"Created new sheet: https://docs.google.com/spreadsheets/d/{spreadsheet_id}\n")
            return spreadsheet_id
        else:
            choice = input("Please enter either y or n: ")

'''create_new_sheet is a helper function that creates a Google Spreadsheet after prompting the user to enter a title for it'''
def create_new_sheet(creds):
    title = input("Enter a title for your new Habit Tracker sheet: ")  # prompt the user to enter a new title for their habit tracker sheet

    spreadsheet_id = create_sheet(creds, title)  # create a spreadsheet using the create_sheet function in google_sheets.py
    print(f"✅ Created Spreadsheet: https://docs.google.com/spreadsheets/d/{spreadsheet_id}\n")
    return spreadsheet_id

'''main handles the logic for displaying the main menu and processing user interactions'''
def main():
    creds = authenticate_user()  # get the user's Google credentials

    # check if the user already has a habit tracker sheet, handle program logic accordingly, and get a reference to the spreadsheet id
    spreadsheet_id = choose_or_create_sheet(creds)

    # main menu logic
    while True:
        print("Menu:")
        print("  1. Add Habit")
        print("  2. Mark Habit Complete")
        print("  3. Edit Habit")
        print("  4. Delete Habit")
        print("  5. Show Habit List")
        print("  6. Exit")
        choice = input("Choose an option (1–6): ")

        if choice == "1":
            habit = input("Enter a habit to track: ")
            add_habit(creds, spreadsheet_id, habit)
        elif choice == "2":
            mark_habit_complete(creds, spreadsheet_id)
        elif choice == "3":
            edit_habit(creds, spreadsheet_id)
        elif choice == "4":
            delete_habit(creds, spreadsheet_id)
        elif choice == "5":
            show_habits(creds, spreadsheet_id)
        elif choice == "6":
            print("\nGoodbye!")
            break
        else:
            print("\nInvalid choice.\n")

if __name__ == "__main__":
    main()
