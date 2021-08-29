import typing as t


class Message:
    def __init__(self, bot) -> None:
        self.bot = bot

    async def setup(self, message_json):
        self.content = message_json["content"]
        self.id = message_json["id"]
        self.channel = await self.bot.get_text_channel(message_json["channel_id"])
        self.author = message_json["author"]

        return self
