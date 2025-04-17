from google_auth_oauthlib.flow import InstalledAppFlow
from google_sheets import get_sheet_data

def main():
    scopes = ['https://www.googleapis.com/auth/spreadsheets.readonly'] # define the permissions the application requests
    creds = None # stores the user's OAuth credentials for authentication with Google APIs
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', scopes) # create the OAuth flow to handle authentication/authorization using the app's credentials and requested permissions

    creds = flow.run_local_server(port=0)  # attempt using the local server first
    print() # print a newline afterwards

    # Step 1: Read data from the sheet
    data = get_sheet_data(creds)

    print(data)

if __name__ == "__main__":
    main()