class RepositoryException(Exception):
    pass


class NotFoundException(RepositoryException):
    pass


class AlreadyExistsException(RepositoryException):
    pass
