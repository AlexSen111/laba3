from dataclasses import dataclass
from dataclasses import field
from uuid import uuid4

from errors import IncorrectEntity


def generate_id() -> str:
    return uuid4().hex


@dataclass
class Book:
    title: str
    category: str
    author: str
    year: int
    page_count: int
    original_language: str
    book_id: str = field(init=False, default_factory=generate_id, repr=True)

    def __post_init__(self) -> None:
        self._validate()

    def _validate(self) -> None:
        if not isinstance(self.book_id, str) or len(self.book_id.strip()) == 0:
            raise IncorrectEntity("Ошибка: ID книги должен быть непустой строкой")
        if not isinstance(self.title, str) or len(self.title.strip()) == 0:
            raise IncorrectEntity("Ошибка: Название книги должно быть непустой строкой")
        if not isinstance(self.author, str) or len(self.author.strip()) == 0:
            raise IncorrectEntity("Ошибка: Имя автора книги должно быть непустой строкой")
        if not isinstance(self.category, str) or len(self.category.strip()) == 0:
            raise IncorrectEntity("Ошибка: Жанр книги должен быть непустой строкой")
        if not isinstance(self.original_language, str) or len(self.original_language.strip()) == 0:
            raise IncorrectEntity("Ошибка: Язык оригинала книги должен быть непустой строкой")
        if not isinstance(self.year, int) or (self.year < 0 or self.year > 2026):
            raise IncorrectEntity(f"Ошибка: Год написания {self.year} отрицателен или больше текущего 2026 года")
        if not isinstance(self.page_count, int) or self.page_count < 1:
            raise IncorrectEntity("Ошибка: Количество страниц должно быть целым числом, большим нуля")
