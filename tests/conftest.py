import json
from pathlib import Path

import openpyxl
import pytest

from pyrecords.models import Data


@pytest.fixture
def people() -> Data:
    return [
        {"name": "Abdullah", "age": 32},
        {"name": "Rawaa", "age": 33},
        {"name": "Rama", "age": 25},
    ]


@pytest.fixture
def xlsx_file(tmp_path: Path, people: Data) -> Path:
    wb = openpyxl.Workbook()
    sheet = wb.active
    assert sheet is not None
    sheet.append(list(people[0]))
    for person in people:
        sheet.append(list(person.values()))
    path = tmp_path / "people.xlsx"
    wb.save(path)
    return path


@pytest.fixture
def json_file(tmp_path: Path, people: Data) -> Path:
    path = tmp_path / "people.json"
    path.write_text(json.dumps(people), encoding="utf-8")
    return path
