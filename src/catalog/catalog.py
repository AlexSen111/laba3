from typing import Iterator

from .errors import IDDuplicate
from .errors import IncorrectEntity
from .errors import ObjectNotFound
from .models import Book


class Catalog:
    def __init__(self) -> None:
        self._items: dict[str, Book] = {}

    def add(self, item: Book) -> None:
        """Добавление книги. (ID книги генерируется в Book автоматически)

        Args:
            item (Book): Книга

        Raises:
            IncorrectEntity: Попытка добавить в каталог объект другого типа
            IDDuplicate: Попытка добавить в каталог книгу с таким же id (почти невозможно, но стоит учесть)
        """
        if not isinstance(item, Book):
            raise IncorrectEntity(f"ожидался Book, получено {type(item).__name__}")
        if item.book_id in self._items:
            # На практике uuid4 не даёт коллизий, но на всякий случай проверяю на наличие дубликата
            raise IDDuplicate(f"книга с id='{item.book_id}' уже в каталоге")
        self._items[item.book_id] = item

    def get(self, item_id: str) -> Book:
        """Поиск по ID

        Args:
            item_id (str): необходимый ID

        Raises:
            ObjectNotFound: если данного ID нет в каталоге

        Returns:
            Book: Книга с нужным ID
        """
        try:
            return self._items[item_id]
        except KeyError:
            raise ObjectNotFound(f"книга с id='{item_id}' не найдена") from None

    def remove(self, item_id: str) -> None:
        """Удаление книги из каталога по ID

        Args:
            item_id (str): ID, по которому удаляем
        """
        self.get(item_id)  # Будет ошибка ObjectNotFound если нет id
        del self._items[item_id]

    def find_by_category(self, category: str) -> list[Book]:
        """Поиск книги по категории

        Args:
            category (str): категория, по которой ищем (поиск ЧУВСТВИТЕЛЕН к регистру)

        Returns:
            list[Book]: список книг в этой категории
        """
        return [self._items[i] for i in sorted(self._items) if self._items[i].category == category]

    def find_by_name(self, name: str) -> list[Book]:
        """Поиск книги по названию

        Args:
            name (str): название/часть названия (поиск НЕ чувствителен к регистру)

        Returns:
            list[Book]: список книг с содержащейся частью названия
        """
        title = name.lower()
        return [self._items[i] for i in sorted(self._items) if title in self._items[i].title.lower()]

    def __len__(self) -> int:
        """Вывод длины каталога

        Returns:
            int: длина каталога
        """
        return len(self._items)

    def __iter__(self) -> Iterator[Book]:
        """Ленивая итерация по каталогу

        Yields:
            Iterator[Book]: итератор, возвращающий объекты Book
        """
        for item_id in self._items:
            yield self._items[item_id]

    def __contains__(self, item_id: object) -> bool:
        """Проверка нахождения объекта в каталоге

        Args:
            item_id (object): необходимый объект

        Returns:
            bool: правда, если находится и ложь, если нет
        """
        return isinstance(item_id, str) and item_id in self._items
