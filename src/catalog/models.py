from dataclasses import dataclass
from dataclasses import field
from uuid import uuid4

from .errors import BrokenFile
from .errors import IncorrectEntity


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

    def to_dict(self) -> dict:
        return {
            "id": self.book_id,
            "title": self.title,
            "category": self.category,
            "author": self.author,
            "year": self.year,
            "page_count": self.page_count,
            "original_language": self.original_language,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Book":
        """Восстановление из JSON: id берётся из документа, а не генерируется снова
        Id генерируется в классе Book, а не передаётся пользователем, а при попытке восстановить книгу из JSON мы генерируем новую книгу с данными из словаря
        Поэтому id получается новым и не соответствует сохранённому, из-за чего мы его пересохраняем отдельно
        Args:
            data (dict): данные о книге (без id)

        Raises:
            BrokenFile: отсутствие поля
            BrokenFile: есть все ключи, но неправильные значения
            BrokenFile: отсутствие id или он неверен

        Returns:
            Book: из словаря получаем объект класса Book с привязанным к нему правильным id
        """
        try:
            book = cls(
                title=data["title"],
                category=data["category"],
                year=data["year"],
                author=data["author"],
                original_language=data["original_language"],
                pag_count=data["page_count"],
            )
        except KeyError as e:
            raise BrokenFile(f"в записи отсутствует поле: {e}") from e
        except IncorrectEntity as e:
            raise BrokenFile(f"невалидная запись: {e}") from e

        # Замена ненужного id на сохранённый
        saved_id = data.get("id")
        # Проверка (на всякий случай)
        if not isinstance(saved_id, str) or not saved_id.strip():
            raise BrokenFile("в записи отсутствует или некорректен id")
        book.book_id = saved_id
        return book
