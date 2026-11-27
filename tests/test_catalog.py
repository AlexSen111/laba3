import json

import pytest

from src.catalog.catalog import Catalog
from src.catalog.errors import BrokenFile
from src.catalog.errors import IDDuplicate
from src.catalog.errors import IncorrectEntity
from src.catalog.errors import ObjectNotFound
from src.catalog.errors import UnsupportedFormatVersion
from src.catalog.memory import load_catalog
from src.catalog.memory import save_catalog
from src.catalog.models import Book


def make_book(**overrides) -> Book:
    base = dict(title="Книга", category="роман", author="Автор", year=2000, page_count=123, original_language="Русский")
    base.update(overrides)
    return Book(**base)


def test_valid_entity_has_generated_id():
    b = make_book()
    assert isinstance(b.book_id, str) and len(b.book_id) == 32


def test_ids_differ_between_books():
    assert make_book().book_id != make_book().book_id


@pytest.mark.parametrize(
    "field,value",
    [
        ("title", "   "),
        ("category", ""),
        ("year", -100),
        ("year", 9999),
        ("author", ""),
        ("page_count", -1),
    ],
)
def test_incorrect_entity(field, value):
    with pytest.raises(IncorrectEntity):
        make_book(**{field: value})


def test_add_works():
    c = Catalog()
    book = make_book()
    c.add(book)
    assert c.get(book.book_id) is book


def test_remove_missing_raises():
    c = Catalog()
    with pytest.raises(ObjectNotFound):
        c.remove("nonexistent")


def test_duplicate_id():
    c = Catalog()
    book = make_book()
    c.add(book)
    book2 = make_book(title="Другая")
    book2.book_id = book.book_id
    with pytest.raises(IDDuplicate):
        c.add(book2)


def test_find_by_category():
    c = Catalog()
    a = make_book(category="роман")
    b = make_book(category="роман")
    d = make_book(category="IT")
    c.add(a)
    c.add(b)
    c.add(d)
    assert {x.book_id for x in c.find_by_category("роман")} == {a.book_id, b.book_id}


def test_find_by_name():
    c = Catalog()
    book = make_book(title="Python Cookbook")
    c.add(book)
    assert [x.book_id for x in c.find_by_name("PYTHON")] == [book.book_id]
    assert [x.book_id for x in c.find_by_name("cook")] == [book.book_id]


def test_search_returns_new_list():
    c = Catalog()
    c.add(make_book())
    res = c.find_by_category("роман")
    res.clear()
    assert len(c) == 1


def test_iteration_order():
    c = Catalog()
    books = [make_book() for _ in range(3)]
    for b in books:
        c.add(b)
    assert [b.book_id for b in c] == [b.book_id for b in books]


def test_iteration_order_after_removal():
    c = Catalog()
    b1, b2, b3 = (make_book() for _ in range(3))
    c.add(b1)
    c.add(b2)
    c.add(b3)
    c.remove(b2.book_id)
    assert [b.book_id for b in c] == [b1.book_id, b3.book_id]


def test_round_trip_preserves_ids(tmp_path):
    c = Catalog()
    a = make_book()
    b = make_book(title="Другая")
    c.add(a)
    c.add(b)
    p = tmp_path / "cat.json"
    save_catalog(c, p)
    r = load_catalog(p)
    assert {x.book_id for x in r} == {a.book_id, b.book_id}
    assert {x.title for x in r} == {a.title, b.title}


def test_corrupted_json(tmp_path):
    p = tmp_path / "bad.json"
    p.write_text("{not json")
    with pytest.raises(BrokenFile):
        load_catalog(p)


def test_unsupported_version(tmp_path):
    p = tmp_path / "v99.json"
    p.write_text(json.dumps({"format_version": 99, "items": []}))
    with pytest.raises(UnsupportedFormatVersion):
        load_catalog(p)


def test_load_error(tmp_path):
    c = Catalog()
    keep = make_book()
    c.add(keep)
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps({"format_version": 1, "items": [{"title": "X"}]}))
    with pytest.raises(BrokenFile):
        load_catalog(bad)
    # исходный каталог нетронут
    assert len(c) == 1 and c.get(keep.book_id) is keep
