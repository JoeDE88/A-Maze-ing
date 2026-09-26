from typing import Callable


def red_text(func: Callable[[str], None]) -> Callable[[str], None]:
    def wrapper(arg: str) -> None:
        narg = "\033[91m" + arg + "\033[00m"
        func(narg)
    return wrapper


@red_text
def print_text(str: str) -> None:
    print(str, end=" ")


class CustomException(Exception):
    def __init__(self, message: str) -> None:
        print_text("[error]")
        super().__init__(message)


class WrongUsageError(CustomException):
    def __init__(self, prog_name: str) -> None:
        message = f"Example of usage: {prog_name} <config_file>"
        super().__init__(message)


class MissingKeyError(CustomException):
    def __init__(self, file: str, keys: list[str]) -> None:
        message = (f"'{file}' has the following missing key:\n"
                   f" - {keys[0]}")
        super().__init__(message)


class KeyValueError(CustomException):
    def __init__(self, file: str, key: str) -> None:
        message = (f"'{file}' must contain 'KEY=VALUE' lines, "
                   f"error on key: {key}")
        super().__init__(message)


class CapitalizedError(CustomException):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class SizeError(CustomException):
    def __init__(self, dimension: str) -> None:
        message = f"{dimension} must be more than 1"
        super().__init__(message)


class OutBoundsError(CustomException):
    def __init__(self, coordinate: str, data: str) -> None:
        message = f"{coordinate} is out of bounds in {data} value"
        super().__init__(message)


class SameDoorsError(CustomException):
    def __init__(self) -> None:
        message = "ENTRY and EXIT have same position"
        super().__init__(message)


class FortyTwoShapeError(CustomException):
    def __init__(self) -> None:
        message = "Maze size is too small to add '42' shape"
        super().__init__(message)


class DoorInFortyTwoError(CustomException):
    def __init__(self, door: str) -> None:
        message = f"{door} can't be inside the '42' pattern"
        super().__init__(message)
