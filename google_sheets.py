from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

'''get_sheet_data retrieves data from a Google Sheet using the Google Sheets API. '''
def get_sheet_data(creds):
    service = build('sheets', 'v4', credentials = creds) # create a Google Sheets API client authenticated with the user's credentials

    spreadsheet_id = '1qIaMrjCJX4aTkngXQ2IwECH3FMuhXRLMy9-uEOWffa4' # unique identifier for the target Google Spreadsheet
    
    # Get the sheet metadata to check the sheet name(s)
    # sheet_metadata = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
    # sheet_titles = [sheet['properties']['title'] for sheet in sheet_metadata['sheets']]
    # print("Available Sheets:", sheet_titles)
    
    range_name = 'Habit Tracker!A2:D' # specifies a sheet and cell range to fetch data from

    sheet = service.spreadsheets() # reference to the Google Sheets API for spreadsheet operations
    result = sheet.values().get(spreadsheetId=spreadsheet_id, range=range_name).execute() # fetch data from the spreadsheet over the specified range of cells

    values = result.get('values', []) # list of lists containing the values read from the spreadsheet (rows of the spreadsheet)

    return values