import builtins
import pytest
import pytz
from package_lab13 import main
from datetime import datetime
from package_lab13.google_sheets import add_habit
from unittest.mock import patch
from package_lab13 import google_sheets



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

# Fixture to mock datetime
@pytest.fixture
def mock_datetime():
    with patch('package_lab13.google_sheets.datetime') as mock_datetime:
        # Mock datetime.now() to return a datetime object, not a string
        mock_datetime.now.return_value = datetime(2025, 4, 23, 14, 37)  # Return a datetime object
        yield mock_datetime

# Test function to test add_habit
def test_add_habit(mock_datetime):
    # Mock credentials and spreadsheet_id
    creds = "mock_credentials"
    spreadsheet_id = "mock_spreadsheet_id"
    habit = "Test Habit"
    
    # Mock input to simulate user input
    with patch('builtins.input', return_value='2025-05-01'):  # Mocking input() to return a fixed date
        with patch('package_lab13.google_sheets.build') as mock_build:
            mock_service = mock_build.return_value.spreadsheets.return_value
            mock_service.values().append.return_value.execute.return_value = None  # Mock the execute call

            # Run the add_habit function
            add_habit(creds, spreadsheet_id, habit)

            # Verify that the values().append().execute() was called once
            mock_service.values().append().execute.assert_called_once()

# Test: Editing an existing habit
def test_edit_habit_updates_timestamp(monkeypatch):
    # --- Arrange ---
    inputs = iter([
        "1",                    # Select habit #1
        "Drink water (updated)",  # New habit name
        "2025-05-01",           # New target date
        "02:30 PM",             # New target time
        "y"                     # Toggle status from ❌ to ✅
    ])
    monkeypatch.setattr(builtins, "input", lambda _: next(inputs))

    # Simulate one habit with placeholder data
    sheet_data = [
        ["Drink water", "2025-04-20 at 01:00 PM", "2025-04-21 at 12:00 PM", "❌", "-"]
    ]
    monkeypatch.setattr(google_sheets, "get_sheet_data", lambda c, s: sheet_data)
    monkeypatch.setattr(google_sheets, "is_habits_empty", lambda d: False)
    monkeypatch.setattr(google_sheets, "print_current_habits", lambda d: None)

    # Track update call
    calls = {"habit_updated": False, "timestamp_updated": False}

    class FakeValues:
        def update(self, spreadsheetId, range, valueInputOption, body):
            if "E" in range:  # Timestamp update
                calls["timestamp_updated"] = True
                # Make sure the timestamp is valid format
                assert datetime.strptime(body["values"][0][0], "%Y-%m-%d %H:%M")
            else:  # Habit row update
                calls["habit_updated"] = True
                assert "Drink water (updated)" in body["values"][0]
                assert "✅" in body["values"][0]
            return self
        def execute(self):
            return {}

    class FakeSpreadsheets:
        def values(self):
            return FakeValues()

    class FakeService:
        def spreadsheets(self):
            return FakeSpreadsheets()

    monkeypatch.setattr(google_sheets, "build", lambda *args, **kwargs: FakeService())

    # --- Act ---
    google_sheets.edit_habit(DUMMY_CREDS, DUMMY_SPREADSHEET_ID)

    # --- Assert ---
    assert calls["habit_updated"], "Habit row was not updated"
    assert calls["timestamp_updated"], "Timestamp was not updated"

def test_delete_habit_google_sheets_call(monkeypatch, capsys):
    # Mock sheet data: header + 3 habits
    sheet_data = [
        ["Task", "Date Created", "Target Date", "Status", "Updated Time"],
        ["Drink water", "2025-04-21", "2025-04-22", "❌", "-"],
        ["Exercise", "2025-04-21", "2025-04-22", "❌", "-"],
        ["Read", "2025-04-21", "2025-04-22", "❌", "-"]
    ]

    # Input: User selects the second habit (Exercise)
    inputs = iter(["2"])

    # Track the batchUpdate request
    called = {}

    class FakeBatchUpdate:
        def batchUpdate(self, spreadsheetId, body):
            called["spreadsheetId"] = spreadsheetId
            called["body"] = body
            return self

        def execute(self):
            return {}

    class FakeValuesGet:
        def get(self, spreadsheetId, range):
            # Return the mocked sheet data
            return self

        def execute(self):
            return {"values": sheet_data}

    class FakeSpreadsheets:
        def get(self, spreadsheetId):
            class GetRequest:
                def execute(self_inner):
                    return {
                        "sheets": [
                            {"properties": {"title": "Habit Tracker", "sheetId": 0}},
                            {"properties": {"title": "Another Sheet", "sheetId": 123}}
                        ]
                    }
            return GetRequest()

        def values(self):
            # Return the fake values.get object
            return FakeValuesGet()

        def batchUpdate(self, spreadsheetId, body):
            return FakeBatchUpdate().batchUpdate(spreadsheetId, body)

    class FakeService:
        def spreadsheets(self):
            return FakeSpreadsheets()

    monkeypatch.setattr(builtins, "input", lambda _: next(inputs))
    monkeypatch.setattr(google_sheets, "build", lambda *args, **kwargs: FakeService())
    monkeypatch.setattr(main, "get_sheet_data", lambda creds, sid: sheet_data)

    # Act
    main.delete_habit(DUMMY_CREDS, DUMMY_SPREADSHEET_ID)

    # Assert: Check if the correct spreadsheetId and request body were passed
    assert called["spreadsheetId"] == DUMMY_SPREADSHEET_ID
    # Check if 'deleteDimension' is in the request body
    assert "deleteDimension" in called["body"]["requests"][0]


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

