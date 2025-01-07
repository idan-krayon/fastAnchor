# FastAPI Spreadsheet Manager

A FastAPI-based application to manage spreadsheets with support for dynamic lookups, type validation, and cycle detection.

## Features

- Create and manage sheets with customizable column schemas.
- Set and get cell values with type validation.
- Support for `lookup` functions to reference other cells.
- Cycle detection for `lookup` dependencies.
- Comprehensive tests and linting for robust development.
- Handle concurrency with thread-safe operations.

---

## Requirements

- Python 3.9 or higher
- `pip` for package management

---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd <repository-name>
```

### 2. Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate 
```

### 3. Install the dependencies

```bash
pip install -r requirements.txt
```


### 4. Run the server
```bash
uvicorn main:app --reload
```

The server will start at http://127.0.0.1:8000

### 5. Run the tests
```bash
pytest
pytest -v # For verbose output
```

### 6. Integration Tests with the Client
```bash
python client_tests.py
```


### 7. Code Quality Checks
Used flake8, isort, black and mypy for code quality checks.
These tools can be used under pre-commit hooks before committing the code or pushed to the repository.
```bash
isort . && black . && flake8 . && mypy .
```

### 8. Notes
- The application uses an in-memory database to store the sheets and cell values, a proper database can be used for production.
