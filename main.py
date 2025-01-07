from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from routers import sheet

app = FastAPI(redirect_slashes=False)

app.include_router(sheet.router, prefix="/api/v1", tags=["sheets"])


@app.get("/")
async def root() -> dict:
    """
    Root endpoint.
    :return: A simple message.
    """
    return {"message": "Hello Anchor"}


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """
    Custom exception handler for validation errors.
    :param request: The request.
    :param exc: The exception.
    :return:
    """
    errors = [
        (
            {
                **error,
                "ctx": {
                    **error.get("ctx", {}),
                    "error": str(error.get("ctx", {}).get("error", "")),
                },
            }
            if "ctx" in error
            else error
        )
        for error in exc.errors()
    ]

    return JSONResponse(
        status_code=400,
        content={
            "detail": "Invalid input schema",
            "errors": errors,
        },
    )
