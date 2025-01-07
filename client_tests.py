import httpx

BASE_URL = "http://127.0.0.1:8000/api/v1"

def create_sheet(columns):
    """
    Create a new sheet.
    """
    url = f"{BASE_URL}/sheet/"
    response = httpx.post(url, json={"columns": columns})
    response.raise_for_status()
    data = response.json()
    print(f"Created sheet with ID: {data['sheetId']}")
    return data["sheetId"]


def get_sheet(sheet_id):
    """
    Get a sheet by ID.
    """
    url = f"{BASE_URL}/sheet/{sheet_id}"
    response = httpx.get(url, timeout=1000)
    response.raise_for_status()
    if response.status_code == 200:
        print(f"Sheet data: {response.json()}")
    else:
        print(f"Failed to get sheet. Status code: {response.status_code}, Detail: {response.json()}")
    return response.json()


def set_cell(sheet_id, row, column, value):
    """
    Set a cell value in a sheet.
    """
    url = f"{BASE_URL}/sheet/{sheet_id}/set"
    response = httpx.post(url, json={"row": row, "column": column, "value": value}, timeout=1000)
    response.raise_for_status()
    if response.status_code == 200:
        print(f"Successfully set cell ({column}, {row}) to {value}")
    else:
        print(f"Failed to set cell. Status code: {response.status_code}, Detail: {response.json()}")


def test_good_flow():
    """
    Test the standard good flow: create sheet, set valid cell values, and resolve lookups.
    """
    columns = [
        {"name": "A", "type": "string"},
        {"name": "B", "type": "boolean"},
        {"name": "C", "type": "string"}
    ]

    sheet_id = create_sheet(columns)

    set_cell(sheet_id, row=10, column="A", value="hello")
    set_cell(sheet_id, row=11, column="B", value=True)
    set_cell(sheet_id, row=1, column="C", value="lookup(A,10)")

    sheet = get_sheet(sheet_id)
    assert sheet["data"]["10"]["A"] == "hello", "Value mismatch in A,10"
    assert sheet["data"]["11"]["B"] is True, "Value mismatch in B,11"
    assert sheet["data"]["1"]["C"] == "hello", "Lookup resolution failed in C,1"

    print("Good flow test passed!")


def test_bad_column():
    """
    Test setting a value for a non-existent column.
    """
    columns = [
        {"name": "A", "type": "string"},
        {"name": "B", "type": "boolean"}
    ]

    sheet_id = create_sheet(columns)

    try:
        set_cell(sheet_id, row=1, column="Z", value="invalid")
    except httpx.HTTPStatusError as e:
        print(f"Expected failure: {e.response.json()['detail']}")


def test_cycle_detection():
    """
    Test detecting a cycle in lookups.
    """
    columns = [
        {"name": "A", "type": "string"},
        {"name": "C", "type": "string"}
    ]

    sheet_id = create_sheet(columns)

    set_cell(sheet_id, row=1, column="C", value="lookup(A,10)")
    set_cell(sheet_id, row=10, column="A", value="hello")

    try:
        set_cell(sheet_id, row=10, column="A", value="lookup(C,1)")
    except httpx.HTTPStatusError as e:
        print(f"Cycle detection test passed: {e.response.json()['detail']}")


def test_invalid_lookup_format():
    """
    Test setting an invalid lookup function.
    """
    columns = [
        {"name": "A", "type": "string"}
    ]

    sheet_id = create_sheet(columns)

    try:
        set_cell(sheet_id, row=1, column="A", value="lookup(B)")
    except httpx.HTTPStatusError as e:
        print(f"Expected failure for invalid lookup format: {e.response.json()['detail']}")



def test_type_mismatch():
    """
    Test setting a value with a type mismatch.
    """
    columns = [
        {"name": "A", "type": "string"},
        {"name": "B", "type": "boolean"}
    ]

    sheet_id = create_sheet(columns)

    try:
        set_cell(sheet_id, row=1, column="A", value=True)
    except httpx.HTTPStatusError as e:
        print(f"Expected type mismatch failure: {e.response.json()['detail']}")


def main():
    """
    Run all tests.
    """
    print("Running good flow test...")
    test_good_flow()

    print("\nRunning bad column test...")
    test_bad_column()

    print("\nRunning cycle detection test...")
    test_cycle_detection()

    print("\nRunning invalid lookup format test...")
    test_invalid_lookup_format()

    print("\nRunning type mismatch test...")
    test_type_mismatch()


if __name__ == "__main__":
    """
    Main entry point.
    """
    main()
