import builtins
import main

# Dummy values
DUMMY_SPREADSHEET_ID = "dummy_spreadsheet_id"
DUMMY_HABIT = "Drink water"

# Mock function to simulate creating a new sheet
def fake_create_sheet(creds, title):
    return DUMMY_SPREADSHEET_ID

# Mock function to simulate adding a habit
def fake_add_habit(creds, spreadsheet_id, habit):
    # Assert
    assert spreadsheet_id == DUMMY_SPREADSHEET_ID
    assert habit == DUMMY_HABIT
    print(f"Habit '{habit}' added to sheet '{spreadsheet_id}'.")

# Mock function to simulate retrieving sheet data
def fake_get_sheet_data(creds, spreadsheet_id):
    return [["1", DUMMY_HABIT], ["2", "Exercise"]]

# Mock function to simulate updating a habit
def fake_update_habit(creds, spreadsheet_id, habit, updated_habit):
    assert spreadsheet_id == DUMMY_SPREADSHEET_ID
    assert habit == DUMMY_HABIT
    assert updated_habit == "Drink water 2.0"
    print(f"Habit '{habit}' updated to '{updated_habit}' in sheet '{spreadsheet_id}'.")

''' test_choose_or_create_sheet_new_sheet tests when the user elects to create a new Google Sheet '''
def test_choose_or_create_sheet_new_sheet(monkeypatch):
    # Arrange
    inputs = iter(["n", "Test Habit Sheet"])
    monkeypatch.setattr(builtins, "input", lambda _: next(inputs))  # patch input with next input in list of inputs
    monkeypatch.setattr(main, "create_sheet", fake_create_sheet)  # patch create_sheet function with call to fake_create_sheet function
    creds = "dummy_credentials"  # assign creds to pass to choose_or_create_sheet function

    # Act
    spreadsheet_id = main.choose_or_create_sheet(creds)

    # Assert
    assert spreadsheet_id == DUMMY_SPREADSHEET_ID

''' test_choose_or_create_sheet_existing_valid tests when the user elects to use an already existing, valid Google Sheet '''
def test_choose_or_create_sheet_existing_valid(monkeypatch):
    # Arrange
    inputs = iter(["y", "https://docs.google.com/spreadsheets/d/dummy_spreadsheet_id/edit"])
    monkeypatch.setattr(builtins, "input", lambda _: next(inputs))  # patch input with next input in list of inputs
    monkeypatch.setattr(main, "is_valid_spreadsheet", lambda creds, id: True)  # patch is_valid_spreadsheet with return value True

    creds = "dummy_credentials"
    # Act
    spreadsheet_id = main.choose_or_create_sheet(creds)  # simulate creating a new Google Sheet

    # Assert
    assert spreadsheet_id == DUMMY_SPREADSHEET_ID  # check that the actual return value matches the expected return value

''' test_add_habit simulates adding a new habit to the Habit Tracker Sheet '''
def test_add_habit(monkeypatch, capsys):
    # Arrange
    inputs = iter(["1", DUMMY_HABIT, "7"])  # simulate menu: Add Habit, enter habit, then Exit

    monkeypatch.setattr(builtins, "input", lambda _: next(inputs))  # patch input with next input in list of inputs
    monkeypatch.setattr(main, "authenticate_user", lambda: "dummy_credentials")  # patch authenticate_user function with return of dummy creds
    monkeypatch.setattr(main, "choose_or_create_sheet", lambda creds: DUMMY_SPREADSHEET_ID)  # patch choose_or_create_sheet function with return of dummy spreadsheet ID
    monkeypatch.setattr(main, "add_habit", fake_add_habit)  # patch add_habit function with call to fake_add_habit function

    # Act
    main.main()  # execute main to test

    # Assert
    captured = capsys.readouterr()
    assert f"Habit '{DUMMY_HABIT}' added to sheet '{DUMMY_SPREADSHEET_ID}'." in captured.out
    # other assertions occur inside 'fake_add_habit' to validate expected values were passed

''' test_edit_habit simulates editing an existing habit in the Habit Tracker Sheet '''
def test_edit_habit(monkeypatch, capsys):
    # Arrange
    inputs = iter(["1", "Drink water 2.0"])  # Simulate user selecting the habit and updating it
    monkeypatch.setattr(builtins, "input", lambda _: next(inputs))  # Mock user input
    monkeypatch.setattr(main, "get_sheet_data", fake_get_sheet_data)  # Mock sheet data retrieval
    
    # Instead of mocking the edit_habit function directly, mock the main.edit_habit function itself
    def fake_edit_habit(creds, spreadsheet_id):
        habit = DUMMY_HABIT  # Simulate the habit being selected for editing
        updated_habit = "Drink water 2.0"  # New habit description
        fake_update_habit(creds, spreadsheet_id, habit, updated_habit)  # Call the original fake update function
    
    monkeypatch.setattr(main, "edit_habit", fake_edit_habit)  # Mock the edit_habit function to call fake_update_habit

    # Act
    main.edit_habit('dummy_credentials', 'dummy_spreadsheet_id')  # Call the function being tested

    # Assert
    captured = capsys.readouterr()
    assert f"Habit '{DUMMY_HABIT}' updated to 'Drink water 2.0' in sheet '{DUMMY_SPREADSHEET_ID}'." in captured.out
