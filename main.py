from google_auth_oauthlib.flow import InstalledAppFlow
from google_sheets import get_sheet_data

def main():
    scopes = ['https://www.googleapis.com/auth/spreadsheets'] # define the permissions the application requests
    creds = None # stores the user's OAuth credentials for authentication with Google APIs
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', scopes) # create the OAuth flow to handle authentication/authorization using the app's credentials and requested permissions

    creds = flow.run_local_server(port=0)  # attempt using the local server first
    print() # print a newline afterwards

    # Step 1: Read data from the sheet
    data = get_sheet_data(creds)
    print(data)

    while True:
        print("\nMenu:")
        print("1. Add Habit")
        print("2. Show Habit List")
        print("3. Exit")
        choice = input("Choose an option (1, 2, or 3): ")

        if choice == "1":
            habit = input("Enter a habit to track: ")
            #add habbit function  # Adds the habit to Google Sheets
            print("✅ Habit added successfully!")

        elif choice == "2":
            data = get_sheet_data(creds)  # Fetches the habit list from the sheet
            if not data:
                print(" No habits found.")
            else:
                print("\n Habit List:")
                for entry in data:
                    print(f"{entry['Date']} - {entry['Habit']}")  # Assuming data has 'Date' and 'Habit' columns

        elif choice == "3":
            print("Goodbye!")
            break  # Exit the program

        else:
            print("❌ Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    main()



if __name__ == "__main__":
    main()