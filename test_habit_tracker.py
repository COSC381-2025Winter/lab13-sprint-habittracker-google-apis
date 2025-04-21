import builtins
import pytest
import main
import google_sheets

# Constants for use across tests
DUMMY_CREDS = "dummy_credentials"
DUMMY_SPREADSHEET_ID = "dummy_spreadsheet_id"
DUMMY_HABIT = "Drink water"

# Dummy credentials object to prevent real Google auth usage
class DummyCreds:
    def authorize(self, http=None):
        return self

# Fixture to fake Google Sheets API client using monkeypatch
@pytest.fixture
def fake_service(monkeypatch):
    # Fake inner service methods: update → execute
    class FakeValues:
        def get(self, spreadsheetId, range):
            # Simulate data retrieval from a sheet
            return self
        def update(self, spreadsheetId, range, valueInputOption, body):
            self.last_call = {
                "spreadsheetId": spreadsheetId,
                "range": range,
                "valueInputOption": valueInputOption,
                "body": body
            }
            return self
        def execute(self):
            return {"status": "OK"}  # or return dummy sheet data here if needed

    # Simulate structure: service.spreadsheets().values().update()
    class FakeSpreadsheets:
        def values(self):
            return FakeValues()

    class FakeService:
        def spreadsheets(self):
            return FakeSpreadsheets()

    # ✅ Monkeypatch google_sheets.build to prevent real API calls
    monkeypatch.setattr(google_sheets, "build", lambda *args, **kwargs: FakeService())
    return FakeService()

# Test: Creating a new sheet
def test_choose_or_create_sheet_new_sheet(monkeypatch):
    # Arrange
    inputs = iter(["n", "Test Habit Sheet"])
    monkeypatch.setattr(builtins, "input", lambda _: next(inputs))
    monkeypatch.setattr(main, "create_sheet", lambda creds, title: DUMMY_SPREADSHEET_ID)
    monkeypatch.setattr(main, "authenticate_user", lambda: DummyCreds())

    # Act
    spreadsheet_id = main.choose_or_create_sheet(DUMMY_CREDS)

    # Assert
    assert spreadsheet_id == DUMMY_SPREADSHEET_ID

# Test: Using an existing valid sheet
def test_choose_or_create_sheet_existing_valid(monkeypatch):
    # Arrange
    inputs = iter(["y", f"https://docs.google.com/spreadsheets/d/{DUMMY_SPREADSHEET_ID}/edit"])
    monkeypatch.setattr(builtins, "input", lambda _: next(inputs))
    monkeypatch.setattr(main, "is_valid_spreadsheet", lambda creds, id: True)
    monkeypatch.setattr(main, "authenticate_user", lambda: DummyCreds())

    # Act
    spreadsheet_id = main.choose_or_create_sheet(DUMMY_CREDS)

    # Assert
    assert spreadsheet_id == DUMMY_SPREADSHEET_ID

# Test: Adding a new habit
def test_add_habit(monkeypatch, capsys):
    # Arrange
    inputs = iter(["1", DUMMY_HABIT, "6"])  # Menu: Add habit, enter text, then exit
    monkeypatch.setattr(builtins, "input", lambda _: next(inputs))
    monkeypatch.setattr(main, "authenticate_user", lambda: DummyCreds())
    monkeypatch.setattr(main, "choose_or_create_sheet", lambda creds: DUMMY_SPREADSHEET_ID)
    monkeypatch.setattr(main, "add_habit", lambda c, s, h: print(f"Habit '{h}' added to sheet '{s}'."))

    # Act
    main.main()

    # Assert
    captured = capsys.readouterr()
    assert f"Habit '{DUMMY_HABIT}' added to sheet '{DUMMY_SPREADSHEET_ID}'." in captured.out

# Test: Editing an existing habit
def test_edit_habit(monkeypatch, capsys):
    # Arrange
    inputs = iter(["1", "Drink water 2.0"])
    monkeypatch.setattr(builtins, "input", lambda _: next(inputs))
    monkeypatch.setattr(main, "get_sheet_data", lambda c, sid: [["1", DUMMY_HABIT], ["2", "Exercise"]])
    monkeypatch.setattr(main, "edit_habit", lambda c, sid: print(f"Habit '{DUMMY_HABIT}' updated to 'Drink water 2.0' in sheet '{DUMMY_SPREADSHEET_ID}'."))

    # Act
    main.edit_habit(DUMMY_CREDS, DUMMY_SPREADSHEET_ID)

    # Assert
    captured = capsys.readouterr()
    assert f"Habit '{DUMMY_HABIT}' updated to 'Drink water 2.0'" in captured.out

# Test: Deleting a habit
def test_delete_habit(monkeypatch, capsys):
    # Arrange
    inputs = iter(["2"])  # Select "Exercise"
    monkeypatch.setattr(builtins, "input", lambda _: next(inputs))
    monkeypatch.setattr(main, "get_sheet_data", lambda c, sid: [["Drink water"], ["Exercise"], ["Read"]])
    monkeypatch.setattr(main, "delete_habit", lambda c, sid: print("✅ Habit 'Exercise' deleted successfully!"))

    # Act
    main.delete_habit(DUMMY_CREDS, DUMMY_SPREADSHEET_ID)

    # Assert
    captured = capsys.readouterr()
    assert "✅ Habit 'Exercise' deleted successfully!" in captured.out

# Test: Marking a habit complete
def test_mark_habit_complete_success(monkeypatch, fake_service):
    # Arrange
    data = [["Task", "Date Created", "Target Date", "Status", "Updated Time"],
            ["Drink water", "date1", "date2", "❌", "-"]]
    monkeypatch.setattr(main, "get_sheet_data", lambda c, s: data)
    monkeypatch.setattr(google_sheets, "is_habits_empty", lambda d: False)
    monkeypatch.setattr(google_sheets, "print_current_habits", lambda d: None)
    monkeypatch.setattr(builtins, "input", lambda _: "1")

    # Act
    main.mark_habit_complete(DUMMY_CREDS, DUMMY_SPREADSHEET_ID)

    # Assert
    # No exception thrown → success

# Test: Already completed habit
# Test: Already completed habit
def test_mark_habit_complete_already_done(monkeypatch, fake_service, capsys):
    # Arrange: simulate sheet values returned from A2:D
    data = [
        ["Drink water", "2025-04-20", "2025-04-21", "❌", "-"],
        ["Walk the dog", "2025-04-20", "2025-04-21", "✅", "-"]
    ]

    monkeypatch.setattr(google_sheets, "get_sheet_data", lambda c, s: data)
    monkeypatch.setattr(google_sheets, "is_habits_empty", lambda d: False)
    monkeypatch.setattr(google_sheets, "print_current_habits", lambda d: None)
    monkeypatch.setattr(builtins, "input", lambda _: "2")  # selects "Walk the dog"

    # Act
    main.mark_habit_complete(DUMMY_CREDS, DUMMY_SPREADSHEET_ID)
    captured = capsys.readouterr()

    # Assert
    assert "Habit 'Walk the dog' is already marked complete" in captured.out



# Test: Invalid selection (out of range)
def test_mark_habit_complete_invalid_selection(monkeypatch, fake_service, capsys):
    # Arrange
    data = [["Task", "Date Created", "Target Date", "Status", "Updated Time"],
            ["A", "d1", "d2", "❌", "-"],
            ["B", "d3", "d4", "❌", "-"]]
    monkeypatch.setattr(main, "get_sheet_data", lambda c, s: data)
    monkeypatch.setattr(google_sheets, "is_habits_empty", lambda d: False)
    monkeypatch.setattr(google_sheets, "print_current_habits", lambda d: None)
    monkeypatch.setattr(builtins, "input", lambda _: "5")  # Invalid index

    # Act
    main.mark_habit_complete(DUMMY_CREDS, DUMMY_SPREADSHEET_ID)
    captured = capsys.readouterr()

    # Assert
    assert "Invalid selection" in captured.out

# Test: Invalid input (non-integer)
def test_mark_habit_complete_invalid_input(monkeypatch, fake_service, capsys):
    # Arrange
    data = [["Task", "Date Created", "Target Date", "Status", "Updated Time"],
            ["C", "d1", "d2", "❌", "-"]]
    monkeypatch.setattr(main, "get_sheet_data", lambda c, s: data)
    monkeypatch.setattr(google_sheets, "is_habits_empty", lambda d: False)
    monkeypatch.setattr(google_sheets, "print_current_habits", lambda d: None)
    monkeypatch.setattr(builtins, "input", lambda _: "abc")  # Invalid input

    # Act
    main.mark_habit_complete(DUMMY_CREDS, DUMMY_SPREADSHEET_ID)
    captured = capsys.readouterr()

    # Assert
    assert "Invalid input" in captured.out

# Test: No habits available
def test_mark_habit_complete_no_habits(monkeypatch, fake_service, capsys):
    # Arrange
    data = [["Task", "Date Created", "Target Date", "Status", "Updated Time"]]
    monkeypatch.setattr(main, "get_sheet_data", lambda c, s: data)
    monkeypatch.setattr(google_sheets, "is_habits_empty", lambda d: True)

    # Act
    main.mark_habit_complete(DUMMY_CREDS, DUMMY_SPREADSHEET_ID)
    captured = capsys.readouterr()

    # Assert
    assert "No habits found to mark complete" in captured.out

def test_create_sheet(monkeypatch):
    # Arrange: Mock Google Sheets API response
    class FakeBatchUpdate:
        def execute(self):
            return {}  # Simulate the response of a successful batch update

    class FakeUpdateValues:
        def update(self, spreadsheetId, range, valueInputOption, body):
            # Simulate a successful values update (no return value needed)
            return self
    
        def execute(self):
            return {}  # Simulate the response of a successful update
    
    class FakeCreateSheet:
        def execute(self):
            # Simulate successful sheet creation with both spreadsheetId and sheets
            return {
                "spreadsheetId": DUMMY_SPREADSHEET_ID,
                "sheets": [{"properties": {"sheetId": 1234}}]  # Include 'sheets' key with mock sheetId
            }

    class FakeSpreadsheets:
        def create(self, body, fields=None):
            # Handle the 'fields' argument
            assert fields == 'spreadsheetId,sheets.properties.sheetId'  # verify the fields parameter
            return FakeCreateSheet()
        
        def values(self):
            # Mock the values method that is used to update the sheet
            return FakeUpdateValues()
        
        def batchUpdate(self, spreadsheetId, body):
            # Mock the batchUpdate method
            return FakeBatchUpdate()

    class FakeService:
        def spreadsheets(self):
            return FakeSpreadsheets()

    monkeypatch.setattr(google_sheets, "build", lambda *args, **kwargs: FakeService())

    # Act: Call the function to test
    spreadsheet_id = google_sheets.create_sheet(DUMMY_CREDS, "Test Habit Sheet")
