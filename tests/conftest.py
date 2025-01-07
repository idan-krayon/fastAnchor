import pytest

from models import ColumnSchema


@pytest.fixture
def valid_column():
    """
    Returns a ColumnSchema instance using valid data.
    """
    return ColumnSchema(**{"name": "A", "type": "int"})


@pytest.fixture
def valid_sheet():
    """
    Provides valid data for creating a SheetSchema.
    """
    return {
        "columns": [
            {"name": "A", "type": "string"},
            {"name": "B", "type": "boolean"},
            {"name": "C", "type": "string"},
        ]
    }


@pytest.fixture
def valid_sheet_schema():
    """
    Provides a valid sheet schema for API calls.
    """
    return {
        "columns": [
            {"name": "A", "type": "string"},
            {"name": "B", "type": "boolean"},
            {"name": "C", "type": "string"},
        ]
    }


@pytest.fixture
def invalid_sheet_schema():
    """
    Provides an invalid sheet schema for API calls.
    """
    return {
        "columns": [
            {"name": "A", "type": "invalid_type"},  # Invalid column type
        ]
    }
