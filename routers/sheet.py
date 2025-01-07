from typing import Any, Dict

from fastapi import APIRouter, HTTPException
from pydantic import ValidationError

from models import SetCellRequest, SheetCreateRequest
from service import SheetManager

router = APIRouter()
manager = SheetManager()


@router.post("/sheet/")
async def create_sheet(request: SheetCreateRequest) -> Dict[str, str]:
    """
    Create a new sheet.
    :param request: Sheet creation request.
    :return:
    """
    try:
        sheet_id = manager.create_sheet(request.columns)
        return {"sheetId": sheet_id}
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/sheet/{sheet_id}")
async def get_sheet(sheet_id: str) -> Any:
    """
    Get a sheet by ID.
    :param sheet_id:
    :return:
    """
    try:
        sheet = manager.get_sheet(sheet_id)
        return sheet.model_dump()
    except KeyError:
        raise HTTPException(status_code=404, detail="Sheet not found.")


@router.post("/sheet/{sheet_id}/set")
async def set_cell(sheet_id: str, request: SetCellRequest) -> Dict[str, str]:
    """
    Set a cell value.
    :param sheet_id: Sheet ID.
    :param request: Set cell request.
    :return:
    """
    try:
        manager.set_cell(sheet_id, request.row, request.column, request.value)
        return {"status": "success"}
    except (KeyError, ValueError, TypeError) as e:
        raise HTTPException(status_code=400, detail=str(e))
