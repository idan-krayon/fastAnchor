import pytest

from models import ColumnSchema


def test_create_valid_column(valid_column):
    assert valid_column.name == "A"
    assert valid_column.type == "int"


def test_create_invalid_column():
    with pytest.raises(ValueError) as exc_info:
        ColumnSchema(**{"name": "A", "type": "invalid_type"})
    assert "Invalid column type" in str(exc_info.value)


def test_create_invalid_column_name():
    with pytest.raises(ValueError) as exc_info:
        ColumnSchema(**{"name": "", "type": "int"})
    assert "Invalid column name" in str(exc_info.value)


def test_validate_correct_value(valid_column):
    valid_column.validate_value(42)


def test_validate_incorrect_value(valid_column):
    with pytest.raises(TypeError) as exc_info:
        valid_column.validate_value("string_value")

    assert "Invalid value for column A" in str(exc_info.value)
