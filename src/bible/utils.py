import random
import re
from functools import lru_cache

from pythonbible.bible import titles
from pythonbible.book_groups import BookGroup
from pythonbible.books import Book
from pythonbible.validator import is_valid_chapter
from pythonbible.verses import MAX_VERSE_NUMBER_BY_BOOK_AND_CHAPTER
from pythonbible.versions import Version

from src.bible.exceptions import InvalidArgumentsError


@lru_cache
def get_book(book: str) -> Book | None:
    """Gets a Book with a regex matching book.

    Args:
        book (str): name of the book to get.

    Returns:
        Book | None: A value from the Book enum or None.
    """
    for _book in Book:
        if re.search(
            _book.regular_expression,
            book,
            re.IGNORECASE,
        ):
            return _book


def random_book(
    book_group: BookGroup | None = None,
    bible_version: Version = Version.NEW_INTERNATIONAL,
) -> Book:
    """Returns random book from the Bible. If book_group is given, the
    book is chosen from that group.

    Args:
        book_group (BookGroup | None, optional): a book group to get from.
            Defaults to None.

    Returns:
        Book: a random book of the Bible
    """
    allowed_books = []

    if book_group:
        # Books in the selected group only
        allowed_books = list(book_group.books)
    else:
        # All books in the given version
        allowed_books = list(titles.SHORT_TITLES[bible_version].keys())

    return random.choice(allowed_books)


def random_chapter_from_book(book: Book) -> int:
    """Gets a random chapter from a book

    Args:
        book (Book): book to get a chapter from

    Returns:
        int: random chapter from book
    """
    number_chapters = len(MAX_VERSE_NUMBER_BY_BOOK_AND_CHAPTER.get(book))

    return random.choice(range(1, number_chapters + 1))


def random_full_verse(
    book: Book | None = None,
    chapter: int | None = None,
    verse_range: int = 1,
    book_group: BookGroup | None = None,
    bible_version: Version = Version.NEW_INTERNATIONAL,
) -> str:
    """Gets a random verse.

    Args:
        book (Book | None, optional): if given, verse is from this book.
            Defaults to None.
        chapter (int | None, optional): if given, verse is from this chapter.
            Defaults to None.
        verse_range (int, optional): number of verses to return. Defaults to 1.
        book_group (BookGroup | None, optional): if given, the book will be
            from this group. Defaults to None.
        bible_version (Version, optional): version of the bible to use. Defaults
            to NEW_INTERNATIONAL_VERSION (NIV).

    Raises:
        InvalidArgumentsError: Raised if the chapter is given and book
            is not given.
        InvalidArgumentsError: Raised if chapter is not found in given book
        InvalidArgumentsError: Raised if the verse_range is less than 1

    Returns:
        str: full verse

    Example:
    ```Python
    full_verse = random_full_verse(Book.Genesis, 1, 3)
    print(full_verse)   # Genesis 1:6-8

    full_verse = random_full_verse(verse_range=1, book_group=BookGroup.NEW_TESTAMENT_GOSPELS)
    print(full_verse)   # Mark 19:4-5
    ```
    """

    if not book and chapter:
        raise InvalidArgumentsError("Cannot provide chapter without book")

    if verse_range < 1:
        raise InvalidArgumentsError("verse_range must be greater than 0")

    if not book:
        _book = random_book(book_group=book_group, bible_version=bible_version)
        _chapter = random_chapter_from_book(_book)
    elif book and not chapter:
        _book = book
        _chapter = random_chapter_from_book(_book)
    else:
        _book = book

        if not is_valid_chapter(_book, chapter):
            raise InvalidArgumentsError(
                "chapter {} not in {}".format(chapter, _book.title)
            )

        _chapter = chapter

    number_verses = MAX_VERSE_NUMBER_BY_BOOK_AND_CHAPTER.get(_book)[
        _chapter - 1
    ]

    from_verse = random.choice(range(1, number_verses + 1 - (verse_range - 1)))

    return (
        "{} {}:{}-{}".format(
            _book.title, _chapter, from_verse, from_verse + verse_range - 1
        )
        if verse_range > 1
        else "{} {}:{}".format(_book.title, _chapter, from_verse)
    )
