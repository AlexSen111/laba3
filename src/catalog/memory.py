import json

from pathlib import Path

from .catalog import Catalog
from .errors import BrokenFile
from .errors import IDDuplicate
from .errors import UnsupportedFormatVersion
from .models import Book


def save_catalog(catalog: Catalog, path: str | Path) -> None:
    document = {"format_version": 1, "items": [book.to_dict() for book in catalog]}
    Path(path).write_text(json.dumps(document, ensure_ascii=False, indent=4), encoding="utf-8")


def load_catalog(path: str | Path) -> Catalog:
    raw = Path(path).read_text(encoding="utf-8")
    try:
        document = json.loads(raw)
    except json.JSONDecodeError as e:
        raise BrokenFile(f"невалидный JSON: {e}") from e

    if not isinstance(document, dict):
        raise BrokenFile("корневой элемент должен быть объектом")

    version = document.get("format_version")
    if version is None:
        raise BrokenFile("отсутствует format_version")
    if not isinstance(version, int) or version != 1:
        raise UnsupportedFormatVersion(f"версия '{version}' не поддерживается")

    items_data = document.get("items")
    if not isinstance(items_data, list):
        raise BrokenFile("items должен быть списком")

    tmp = Catalog()
    for entry in items_data:
        if not isinstance(entry, dict):
            raise BrokenFile("элемент items должен быть объектом")
        book = Book.from_dict(entry)
        try:
            tmp.add(book)
        except IDDuplicate as e:
            raise BrokenFile(f"дубликат id в файле: {e}") from e
    return tmp
