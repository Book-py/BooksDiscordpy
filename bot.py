import asyncio
import inspect
import json
import typing as t

import websockets

from . import channel, errors, http
from .command import BotCommand
from .context import Context
from .embed import Embed
from .guild import Guild
from .message import Message
from .user import User


class Bot:
    """Basic bot implementation.

    This is the class to use for starting, stopping, controlling and developing
    the bot. You can subclass this class to get extra functionality and features not already added.
    """

    def __init__(
        self, debug: t.Optional[bool] = True, *, token: str, prefix: str
    ) -> None:

        self.running = False
        self.loop = asyncio.get_event_loop()

        if debug:
            self.loop.set_debug(True)

        self.prefix = prefix

        self.http = http.DiscordHttpClient(self.loop)
        self.is_closed = False
        self.token = token

        self.http.login(self.token)
        self.commands: t.List[BotCommand] = []

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
            user_json = json.loads(ready_data)
            self.user = User(user_json["d"]["user"], self)

            should_receive = True

            while should_receive:
                data = await discord_websocket.recv()

                asyncio.ensure_future(self.handle_events(json.loads(data)))

    async def handle_events(self, event_data) -> None:

        if event_data["op"] != 0:
            return

        if event_data["t"] == "MESSAGE_CREATE":
            message = await Message(self).setup(event_data["d"])
            asyncio.ensure_future(self.on_message_create(message))

        if event_data["t"] == "READY":
            asyncio.ensure_future(self.on_ready())

    async def on_ready(self):
        pass

    async def on_message_create(self, message: Message):
        await self.process_command(message)

    async def process_command(self, message: Message):
        """Processes the message to check if it is a command, and if so calls the command

        Args:
            message (Message): The message to process
        """
        try:
            if message.content.startswith(self.prefix):
                command_message = message.content[len(self.prefix) :]

                for command in self.commands:
                    if command_message.split(" ")[0] == command.name:
                        # They have ran a command

                        # Handle the arguments to the command
                        given_arguments = command_message.split(" ")[1:]

                        # The signature of the command
                        sig = inspect.signature(command.callback)

                        print(sig.parameters)

                        items = sig.parameters.items()

                        position = -1
                        for key, value in items:
                            if value.annotation == int:

                                given_arguments[position] = int(
                                    given_arguments[position]
                                )

                            if value.annotation == Guild:
                                if given_arguments[position].isnumeric():
                                    guild = await self.get_guild(
                                        int(given_arguments[position])
                                    )
                                    given_arguments[position] = guild

                            position += 1

                        # Check for the number of parameters given
                        if len(given_arguments) > len(sig.parameters) - 1:
                            raise errors.TooManyArguments(
                                "Too many arguments were passed"
                            )
                        elif len(given_arguments) < len(sig.parameters) - 1:
                            raise errors.NotEnoughArguments(
                                "Not enough arguments were passed"
                            )

                        # Get the context of the command, and invoke it
                        context = Context(self, message)
                        await command.call_command(context, *given_arguments)
                        return

                    if command_message.split(" ")[0] in command.aliases:
                        # They have run a command
                        context = Context(self, message)
                        await command.call_command(context)
                        return

        except Exception as e:
            context = Context(self, message)
            await self.on_command_error(e, context)

    async def on_command_error(self, exc: Exception, context: Context):
        raise exc

    async def send_message(
        self,
        channel_id: int,
        content: t.Optional[str],
        *,
        tts: t.Optional[bool] = False,
        embeds: t.Optional[t.List[Embed]] = None,
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

    async def get_text_channel(self, channel_id: int) -> channel.TextChannel:
        """Get the discord text channel for a given id

        Args:
            channel_id (int): The id of the text channel to get

        Returns:
            channel.TextChannel: The channel object that corresponds to the id provided
        """

        channel_json = await self.http.get_channel(channel_id)
        return channel.TextChannel(channel_json, self)  # type: ignore

    async def get_guild(self, guild_id: int) -> Guild:
        guild_json = await self.http.get_guild(guild_id)
        return Guild(self, guild_json)

    def complete_pending_tasks(self):
        loop = asyncio.new_event_loop()

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
        run_main_task = loop.create_task(run_main)
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

    def add_command(
        self,
        *,
        name: t.Optional[str] = None,
        aliases: t.Optional[t.List[str]] = None,
        description: t.Optional[str] = None,
    ):
        def inner(func):
            if inspect.iscoroutinefunction(func):
                command = BotCommand(self, name, aliases, description, callback=func)
                self.commands.append(command)

                return func
            else:
                raise TypeError("Commands must be a coroutine")

        return inner
