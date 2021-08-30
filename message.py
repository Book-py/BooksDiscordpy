import typing as t
from .guild import Guild
from .embed import Embed


class Message:
    def __init__(self, bot) -> None:
        self.bot = bot

    async def setup(self, message_json):
        self.content = message_json["content"]
        self.id = message_json["id"]
        self.channel = await self.bot.get_text_channel(message_json["channel_id"])
        self.author = message_json["author"]
        self.guild_id = message_json["guild_id"]

        self.guild = Guild(self.bot, await self.bot.get_guild(message_json["guild_id"]))

        return self
