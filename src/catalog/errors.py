class CatalogError(Exception):
    pass


class IncorrectEntity(CatalogError):
    pass


class IDDuplicate(CatalogError):
    pass


class ObjectNotFound(CatalogError):
    pass


class UnsupportedFormatVersion(CatalogError):
    pass


class BrokenFile(CatalogError):
    pass
