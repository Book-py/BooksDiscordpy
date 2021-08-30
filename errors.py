class BaseError(Exception):
    pass


class CommandError(BaseError):
    pass


class TooManyArguments(CommandError):
    pass


class NotEnoughArguments(CommandError):
    pass


__all__ = ["CommandError", "TooManyArguments", "NotEnoughArguments"]
