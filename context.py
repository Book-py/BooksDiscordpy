import typing as t
from .message import Message


class Context:
    def __init__(self, bot, message: Message):
        self.bot = bot
        self.message = message
        self.guild_id = message.guild_id
        self.channel = message.channel

    async def send(self, *args, **kwargs):
        await self.message.channel.send(*args, **kwargs)
