import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


@pytest.fixture
def create_valid_sheet(valid_sheet_schema):
    """
    Creates a valid sheet via the API and returns the sheet ID.
    """
    response = client.post("/api/v1/sheet/", json=valid_sheet_schema)
    assert response.status_code == 200
    return response.json()["sheetId"]


def test_create_sheet_good_call(valid_sheet):
    """
    Test creating a sheet with a valid schema.
    """
    response = client.post(
        "/api/v1/sheet/",
        json=valid_sheet,
    )
    assert response.status_code == 200
    assert response.json()["sheetId"]


def test_create_sheet_bad_call(invalid_sheet_schema):
    """
    Test creating a sheet with an invalid schema.
    """
    response = client.post("/api/v1/sheet/", json=invalid_sheet_schema)
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data


def test_get_sheet_good_call(create_valid_sheet):
    """
    Test retrieving a sheet with a valid sheet ID.
    """
    sheet_id = create_valid_sheet

    response = client.get(f"/api/v1/sheet/{sheet_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == sheet_id
    assert "columns" in data
    assert "data" in data


def test_get_sheet_bad_call_non_existent_id():
    """
    Test retrieving a sheet with a non-existent sheet ID.
    """
    response = client.get("/api/v1/sheet/non_existent_id")
    assert response.status_code == 404
    assert "detail" in response.json()


def test_set_cell_good_call(create_valid_sheet):
    """
    Test setting a cell with valid data.
    """
    sheet_id = create_valid_sheet

    response = client.post(
        f"/api/v1/sheet/{sheet_id}/set",
        json={"row": 10, "column": "A", "value": "hello"},
    )
    assert response.status_code == 200
    assert response.json() == {"status": "success"}

    get_response = client.get(f"/api/v1/sheet/{sheet_id}")
    assert get_response.status_code == 200
    sheet = get_response.json()
    assert sheet["data"]["10"]["A"] == "hello"


def test_set_cell_bad_call_invalid_column(create_valid_sheet):
    """
    Test setting a cell with an invalid column.
    """
    sheet_id = create_valid_sheet

    response = client.post(
        f"/api/v1/sheet/{sheet_id}/set",
        json={"row": 10, "column": "Z", "value": "hello"},
    )
    assert response.status_code == 400
    assert "detail" in response.json()
    assert "Column Z does not exist." in response.json()["detail"]


def test_big_test_with_sheet_and_data(create_valid_sheet):
    """
    Test setting cell values and resolving a lookup function.
    """
    sheet_id = create_valid_sheet
    set_response_a = client.post(
        f"/api/v1/sheet/{sheet_id}/set",
        json={"row": 10, "column": "A", "value": "hello"},
    )
    assert set_response_a.status_code == 200
    assert set_response_a.json() == {"status": "success"}

    set_response_b = client.post(
        f"/api/v1/sheet/{sheet_id}/set", json={"row": 11, "column": "B", "value": True}
    )
    assert set_response_b.status_code == 200
    assert set_response_b.json() == {"status": "success"}

    set_response_c = client.post(
        f"/api/v1/sheet/{sheet_id}/set",
        json={"row": 1, "column": "C", "value": "lookup(A,10)"},
    )
    assert set_response_c.status_code == 200
    assert set_response_c.json() == {"status": "success"}

    get_response = client.get(f"/api/v1/sheet/{sheet_id}")
    assert get_response.status_code == 200
    sheet = get_response.json()

    assert sheet["data"]["10"]["A"] == "hello"
    assert sheet["data"]["11"]["B"] == True
    assert sheet["data"]["1"]["C"] == "hello"  # ("C", 1) -> "hello" (via lookup)


def test_set_cell_cycle_detection(create_valid_sheet):
    """
    Test detecting cycles in cell dependencies.
    """
    sheet_id = create_valid_sheet

    set_response_a = client.post(
        f"/api/v1/sheet/{sheet_id}/set",
        json={"row": 1, "column": "C", "value": "lookup(A,1)"},
    )
    assert set_response_a.status_code == 200
    assert set_response_a.json() == {"status": "success"}

    set_response_b = client.post(
        f"/api/v1/sheet/{sheet_id}/set",
        json={"row": 1, "column": "A", "value": "lookup(B,1)"},
    )
    assert set_response_b.status_code == 200
    assert set_response_b.json() == {"status": "success"}

    cycle_response = client.post(
        f"/api/v1/sheet/{sheet_id}/set",
        json={"row": 1, "column": "B", "value": "lookup(C,1)"},
    )

    assert cycle_response.status_code == 400
    assert "Cycle detected" in cycle_response.json()["detail"]


def test_set_cell_cycle_detection2(create_valid_sheet):
    """
    Test detecting cycles in cell dependencies.
    """
    sheet_id = create_valid_sheet

    set_response_a = client.post(
        f"/api/v1/sheet/{sheet_id}/set",
        json={"row": 1, "column": "C", "value": "lookup(A,10)"},
    )
    assert set_response_a.status_code == 200
    assert set_response_a.json() == {"status": "success"}

    set_response_b = client.post(
        f"/api/v1/sheet/{sheet_id}/set",
        json={"row": 10, "column": "A", "value": "lookup(C,1)"},
    )

    assert set_response_b.status_code == 400
    assert "Cycle detected" in set_response_b.json()["detail"]
