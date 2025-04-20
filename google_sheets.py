from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

'''create_sheet uses the user's Google credentials and a sheet title they entered to create a new Google Spreadsheet '''
def create_sheet(creds, title: str):
    """Create a new Google Sheet and return its spreadsheetId."""
    service = build('sheets', 'v4', credentials=creds)
    body = {
        'properties': {'title': title}
    }
    sheet = service.spreadsheets().create(
        body=body,
        fields='spreadsheetId'
    ).execute() # create a Google Sheet with the provided title
    return sheet['spreadsheetId'] # return the spreadsheet ID

'''get_sheet_data retrieves data from a Google Sheet using the Google Sheets API. '''
def get_sheet_data(creds, spreadsheet_id):
    service = build('sheets', 'v4', credentials = creds) # create a Google Sheets API client authenticated with the user's credentials
    
    # Get the sheet metadata to check the sheet name(s)
    # sheet_metadata = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
    # sheet_titles = [sheet['properties']['title'] for sheet in sheet_metadata['sheets']]
    # print("Available Sheets:", sheet_titles)
    
    range_name = 'Habit Tracker!A2:D' # specifies a sheet and cell range to fetch data from

    sheet = service.spreadsheets() # reference to the Google Sheets API for spreadsheet operations
    result = sheet.values().get(spreadsheetId=spreadsheet_id, range=range_name).execute() # fetch data from the spreadsheet over the specified range of cells

    values = result.get('values', []) # list of lists containing the values read from the spreadsheet (rows of the spreadsheet)

    return values

'''add_habit adds a new habit to the Google Sheet.'''
def add_habit(creds, spreadsheet_id, habit):
    service = build('sheets', 'v4', credentials=creds)  # Google Sheets API client
    sheet_name = 'Habit Tracker'  # Name of the sheet to modify

    # Prepare data to append
    new_row = [habit]  # Habit to add 

    # Append new habit to the sheet
    range_name = f'{sheet_name}!A2'  # Start appending from row 2 because row 1 are headers
    body = {
        'values': [new_row]
    }

    # Append the new habit to the sheet
    sheet = service.spreadsheets()
    sheet.values().append(
        spreadsheetId=spreadsheet_id,
        range=range_name,
        valueInputOption="RAW",  # Values are inserted as raw text
        body=body
    ).execute()

    print(f"\n✅ Habit '{habit}' added successfully!\n")