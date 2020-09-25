"""
:synopsis: Exceptions used with metarelations.
"""


class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class InputError(Error):
    """Raise exceptions for errors in the input.

    :param str message: Explanation of the error
    """

    def __init__(self, message):
        self.message = message
