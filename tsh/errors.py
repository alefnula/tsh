class TshError(Exception):
    def __init__(self, message: str = ""):
        self.message = message

    def __str__(self):
        return f"{self.__class__.__name__}({self.message})"

    __repr__ = __str__


class CommandNotFound(TshError):
    pass
