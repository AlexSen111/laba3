from dataclasses import dataclass


@dataclass
class Book:
    title: str
    category: str
    author: str
    year: int
    page_count: int
    original_language: str
