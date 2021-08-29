import typing as t
import asyncio
import json

from . import http
from . import channel
from .guild import Guild
import websockets


class Bot:
    """Basic bot implementation.

    This is the class to use for starting, stopping, controlling and developing
    the bot. You can subclass this class to get extra functionality and features not already added.
    """

    def __init__(self, debug: t.Optional[bool] = True, *, token: str) -> None:

        self.running = False
        self.loop = asyncio.get_event_loop()

        if debug:
            self.loop.set_debug(True)

        self.http = http.DiscordHttpClient(self.loop)
        self.is_closed = False
        self.token = token

        self.http.login(self.token)

    async def connect(self):
        """Connect the bot to the discord servers

        Args:
            reconnect (bool): If we should try to reconnect to discord after the connection is closed. Defaults to True.
        """

        headers = {
            "Authorization": f"Bot {self.token}",
            "bot": "True",
            "Content-type": "application/json",
        }

        async with websockets.connect(  # type: ignore
            uri="wss://gateway.discord.gg/?v=9&encoding=json", extra_headers=headers
        ) as discord_websocket:
            data = await discord_websocket.recv()
            print(data)

            payload = f"""{{
        "op": 2,
        "d": {{
            "token": "{self.token}",
            "intents": {1 << 9},
            "properties": {{
                "$os": "linux",
                "$browser": "books_discord_py",
                "$device": "books_discord_py"
            }}
        }}
    }}"""
            await discord_websocket.send(payload)

            ready_data = await discord_websocket.recv()

            should_receive = True

            while should_receive:
                data = await discord_websocket.recv()

                self.handle_events(json.loads(data))

    def handle_events(self, event_data) -> None:

        if event_data["op"] != 0:
            return

        if event_data["t"] == "MESSAGE_CREATE":
            asyncio.ensure_future(self.on_message_create(event_data["d"]))

    async def on_message_create(self, message_data: dict):
        print(f"Recieved a message!\nContent: {message_data['content']}")

    async def send_message(
        self,
        channel_id: int,
        content: t.Optional[str],
        *,
        tts: t.Optional[bool] = False,
        embeds: t.Optional[t.List[t.Dict[t.Any, t.Any]]] = None,
    ):
        """Sends a message as the bot to the specified discord text channel

        Args:
            channel_id (int): The id of the discord channel to send the message to
            content (str): The content of the message to send
            tts (t.Optional[bool], optional): If it should be a discord text-to-speach (tts) message: Defaults to False.
            embeds (t.Optional[t.List[t.Dict[str, str]]], optional): List of dictionaries for embeds to send. The embeds must be in the discord desired format: Defaults to None.
        """

        if (
            content is None
            and embeds is None
            or type(embeds) == list
            and len(embeds) == 0
        ):
            raise ValueError(
                "Discord requires either a message content or embed to send in a message"
            )

        await self.http.send_message(channel_id, content, tts, embeds)

    def get_text_channel(self, channel_id: int) -> channel.TextChannel:
        """Get the discord text channel for a given id

        Args:
            channel_id (int): The id of the text channel to get

        Returns:
            channel.TextChannel: The channel object that corresponds to the id provided
        """

        channel_json = self.loop.run_until_complete(self.http.get_channel(channel_id))
        return channel.TextChannel(channel_json, self)  # type: ignore

    def get_guild(self, guild_id: int) -> Guild:
        json = self.loop.run_until_complete(self.http.get_guild(guild_id))
        return Guild(self, json)

    def complete_pending_tasks(self):
        def get_pending_tasks():
            tasks = asyncio.all_tasks()
            pending = [
                task for task in tasks if task != run_main_task and not task.done()
            ]
            return pending

        async def run_all_pending_tasks():
            while True:
                pending_tasks = get_pending_tasks()
                if len(pending_tasks) == 0:
                    return
                await asyncio.gather(*pending_tasks)

        run_main = run_all_pending_tasks()
        run_main_task = self.loop.create_task(run_main)
        self.loop.run_until_complete(run_main_task)

    def start(self) -> None:
        """Starts the bot and establishes a connection to discord"""

        loop = asyncio.new_event_loop()
        loop.create_task(self.connect())
        loop.run_forever()

        # {"t":null,"s":null,"op":10,"d":{"heartbeat_interval":41250,"_trace":["[\"gateway-prd-main-h3kg\",{\"micros\":0.0}]"]}}

    def close(self):

        asyncio.run(self.http.close())
        self.loop.close()
