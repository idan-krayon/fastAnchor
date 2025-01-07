import threading
from typing import Any, Dict, List
from uuid import uuid4

from models import ColumnSchema, SheetSchema


class SheetManager:
    """
    Manages sheets.
    """

    def __init__(self) -> None:
        """
        Initialize the sheet manager.
        """
        self.sheets: Dict[str, SheetSchema] = {}
        self.lock = threading.Lock()

    def create_sheet(self, columns: List[ColumnSchema]) -> str:
        """
        Create a new sheet.
        :param columns: List of columns.
        :return: The ID of the new sheet.
        """
        with self.lock:
            sheet_id = str(uuid4())
            self.sheets[sheet_id] = SheetSchema(id=sheet_id, columns=columns)
            return sheet_id

    def get_sheet(self, sheet_id: str) -> SheetSchema:
        """
        Get a sheet by ID.
        :param sheet_id: Sheet ID.
        :return: The sheet schema.
        """
        with self.lock:
            if sheet_id not in self.sheets:
                raise KeyError(f"Sheet {sheet_id} not found.")

            sheet = self.sheets[sheet_id]
            resolved_data = {}
            for row, row_data in sheet.data.items():
                resolved_row = {}
                for column, value in row_data.items():
                    resolved_row[column] = self.lookup_value(
                        sheet, column, row, value, visited=set()
                    )
                resolved_data[row] = resolved_row

            # Return a copy of the SheetSchema object with resolved data
            return SheetSchema(id=sheet.id, columns=sheet.columns, data=resolved_data)

    def set_cell(self, sheet_id: str, row: int, column: str, value: Any) -> None:
        """
        Set a cell value.
        :param sheet_id: Sheet ID.
        :param row: Row index.
        :param column: Column name.
        :param value: Value to set.
        :return: None
        """
        with self.lock:
            sheet = self.sheets.get(sheet_id, None)
            if not sheet:
                raise KeyError(f"Sheet {sheet_id} not found.")

            # Detect cycles
            if isinstance(value, str) and value.startswith("lookup("):
                try:
                    self.lookup_value(sheet, column, row, value, visited=set())
                except ValueError as e:
                    raise ValueError(f"Invalid lookup function: {e}")

            # If no cycles, proceed to set the cell value
            sheet.validate_value(column, value)
            if row not in sheet.data:
                sheet.data[row] = {}
            sheet.data[row][column] = value

    def lookup_value(
        self, sheet: SheetSchema, column: str, row: int, value: Any, visited: set
    ) -> Any:
        """
        Resolve the value of a cell, including lookups.
        :param sheet: The sheet schema.
        :param column: The column of the cell.
        :param row: The row of the cell.
        :param value: The value of the cell.
        :param visited: Set of visited nodes to prevent cycles.
        :return: Resolved value.
        """
        try:
            if isinstance(value, str) and value.startswith("lookup("):
                args = value[len("lookup(") : -1].split(",")
                ref_column = args[0].strip()
                ref_row = int(args[1].strip())

                # Instead of going through the entire sheet, we can just check if the
                # cell is in the visited set
                if (ref_column, ref_row) in visited:
                    raise ValueError(
                        f"Cycle detected involving cell ({column}, {row})."
                    )

                visited.add((column, row))

                if ref_row not in sheet.data or ref_column not in sheet.data[ref_row]:
                    return value

                return self.lookup_value(
                    sheet, ref_column, ref_row, sheet.data[ref_row][ref_column], visited
                )
        except IndexError:
            raise ValueError("Invalid lookup function format.")

        return value
