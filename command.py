import typing as t
import asyncio
import inspect


class BotCommand:
    def __init__(
        self,
        bot,
        name: str,
        aliases: t.Optional[t.List[str]] = None,
        description: t.Optional[str] = None,
        *,
        callback: t.Coroutine
    ):

        # if not asyncio.iscoroutine(callback):
        # raise TypeError("The command must be a coroutine")

        if not isinstance(name, str):
            raise TypeError("Name of a command must be a string.")

        self.bot = bot
        self.name = name
        self.aliases = aliases or []
        self._callback = callback

        if description:
            self.description = description
        else:
            self.description = inspect.getdoc(callback)  # type: ignore
            if isinstance(self.description, bytes):
                self.description = self.description.decode("utf-8")

    @property
    def callback(self):
        return self.callback

    async def call_command(self, context):
        await self._callback(context)
