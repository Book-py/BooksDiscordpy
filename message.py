import typing as t
from .guild import Guild


class Message:
    def __init__(self, bot) -> None:
        self.bot = bot

    async def setup(self, message_json):
        self.content = message_json["content"]
        self.id = message_json["id"]
        self.channel = await self.bot.get_text_channel(message_json["channel_id"])
        self.author = message_json["author"]

        guild_json = await self.bot.get_guild(message_json["guild_id"])
        self.guild = Guild(self.bot, guild_json)

        return self
