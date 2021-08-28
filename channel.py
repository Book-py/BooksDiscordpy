import typing as t

class TextChannel:
    def __init__(
        self,
        channel_json: t.Dict[t.Any, t.Any],
        bot
    ) -> None:

        self.http = bot.http
        self.loop = bot.loop

        # Defining all the attributes from what gets returned from the discord API in `channel_json`
        self.id = channel_json['id']
        self.last_message_id = channel_json['last_message_id']
        self.last_pin_timestamp = channel_json['last_pin_timestamp']
        self.type = channel_json['type']
        self.name = channel_json['name']
        self.position = channel_json['position']
        self.parent_id = channel_json['parent_id']
        self.topic = channel_json['topic']
        self.guild_id = channel_json['guild_id']
        self.permission_overwrites = channel_json['permission_overwrites']
        self.nsfw = channel_json['nsfw']
        self.rate_limit_per_user = channel_json['rate_limit_per_user']
    
    def send(
        self,
        content: t.Optional[str],
        *,
        tts: t.Optional[bool]=False,
        embeds: t.Optional[t.List[t.Dict[t.Any, t.Any]]]=None
        ) -> None:
        """Sends a message to a discord text channel

        Args:
            content `str`: The content
            tts `Optional[bool]`: If the message should be sent as a discord text-to-speach (tts) message. Defaults to False.
            embeds `Optional[List[Dict[Any, Any]]]`: A list of dictionaries representing discord embeds. Defaults to None.
        """

        if content is None and embeds is None or type(embeds) == list and len(embeds) == 0:
            raise ValueError("Discord requires either a message content or embed to send in a message")

        self.loop.run_until_complete(self.http.send_message(self.id, content, tts, embeds))