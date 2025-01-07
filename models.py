from typing import Any, Dict, List

from pydantic import BaseModel, field_validator


class ColumnSchema(BaseModel):
    """
    Schema for a column in a sheet.
    """

    name: str
    type: str

    @field_validator("name")
    def validate_name(cls, value: str) -> str:
        """
        Validate the column name.
        :param value:
        :return:
        """
        if not value.isidentifier() or len(value) == 0:
            raise ValueError(f"Invalid column name: {value}")

        return value

    @field_validator("type")
    def validate_type(cls, value: Any) -> Any:
        """
        Validate the column type.
        :param value:
        :return:
        """
        if value not in {"boolean", "int", "double", "string"}:
            raise ValueError(f"Invalid column type: {value}")

        return value

    def validate_value(self, value: Any) -> None:
        """
        Validate a value against the column's type.
        :param value: Value to validate.
        :raises TypeError: If the value does not match the column's type.
        """
        if self.type == "boolean" and not isinstance(value, bool):
            raise TypeError(f"Invalid value for column {self.name}: expected boolean.")
        if self.type == "int" and not isinstance(value, int):
            raise TypeError(f"Invalid value for column {self.name}: expected int.")
        if self.type == "double" and not isinstance(value, float):
            raise TypeError(f"Invalid value for column {self.name}: expected double.")
        if self.type == "string" and not isinstance(value, str):
            raise TypeError(f"Invalid value for column {self.name}: expected string.")


class SheetSchema(BaseModel):
    """
    Schema for a sheet.
    """

    id: str
    columns: List[ColumnSchema]
    data: Dict[int, Dict[str, Any]] = {}

    def validate_value(self, column: str, value: Any) -> None:
        """
        Validate a value for a column by delegating to the column schema.
        :param column: Column name.
        :param value: Value to validate.
        :raises ValueError: If the column does not exist.
        :raises TypeError: If the value does not match the column's type.
        """
        col = next((c for c in self.columns if c.name == column), None)
        if not col:
            raise ValueError(f"Column {column} does not exist.")

        col.validate_value(value)


class SheetCreateRequest(BaseModel):
    """
    Request schema for creating a new sheet.
    """

    columns: List[ColumnSchema]


class SetCellRequest(BaseModel):
    """
    Request schema for setting a cell value.
    """

    row: int
    column: str
    value: Any
