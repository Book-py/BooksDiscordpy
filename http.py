import aiohttp
import asyncio
import typing as t
from .embed import Embed as discordEmbed


class DiscordHttpClient:
    def __init__(self, loop: t.Optional[asyncio.AbstractEventLoop] = None) -> None:

        self.loop = loop
        self.__session = aiohttp.ClientSession()

    async def close(self) -> None:
        if not self.__session.closed:
            await self.__session.close()

    def login(self, token):
        self.token = token
        # headers = {
        # "Authorization": f'Bot {token}'
        # }

        # async with self.__session as session:
        # async with session.get(url='https://discord.com/api/v8/users/@me', headers=headers) as data:
        # async with session.request(method="PUT", url='https://discord.com/api/v8/auth/login', headers=headers) as data:
        # return data, await data.json()

    async def send_message(
        self,
        channel_id: int,
        content: t.Optional[str],
        tts: t.Optional[bool] = False,
        embeds: t.Union[
            t.Optional[t.List[t.Dict[str, str]]], t.Optional[t.List[discordEmbed]]
        ] = None,
    ) -> aiohttp.ClientResponse:

        headers = {
            "Authorization": f"Bot {self.token}",
            "Content-Type": "application/json",
        }

        message_data: t.Dict[str, t.Any] = {
            "content": content,
            "tts": tts,
            "embeds": [],
        }

        if type(embeds) == list:
            for embed in embeds:
                if isinstance(embed, discordEmbed):
                    message_data["embeds"].append(embed.to_dict())

                elif type(embed) == dict:
                    message_data["embeds"].append(embed)

        url = f"https://discord.com/api/v9/channels/{channel_id}/messages"

        async with self.__session as session:
            if session.closed:
                session = self.recreate()

            async with session.post(url, headers=headers, json=message_data) as data:

                if data.status != 200:
                    print(f"The discord API returned the http status: {data.status}")
                    print(await data.json())
                    return  # type: ignore

                data_json = await data.json()

                try:
                    if discord_code := data_json["code"]:
                        print(discord_code)
                        return  # type: ignore
                except KeyError:
                    pass

                return data_json

    async def get_channel(self, channel_id: int) -> aiohttp.ClientResponse:

        headers = {"Authorization": f"Bot {self.token}"}

        url = f"https://discord.com/api/v9/channels/{channel_id}"

        async with self.__session as session:
            if session.closed:
                session = self.recreate()

            async with session.get(url, headers=headers) as response:
                return await response.json()

        return  # type: ignore

    async def get_guild(self, guild_id: int) -> aiohttp.ClientResponse:
        headers = {"Authorization": f"Bot {self.token}"}

        url = f"https://discord.com/api/v9/guilds/{guild_id}"

        async with self.__session as session:
            if session.closed:
                session = self.recreate()

            async with session.get(url, headers=headers) as response:
                return await response.json()

    async def edit_channel(
        self,
        channel_id: int,
        name: t.Optional[str],
        type: t.Optional[int],
        position: t.Optional[int],
        topic: t.Optional[str],
        nsfw: t.Optional[bool],
        slow_mode: t.Optional[int],
        parent_id: t.Optional[int],
        reason: t.Optional[str],
    ) -> t.Dict[t.Any, t.Any]:
        headers = {"Authorization": f"Bot {self.token}"}

        if reason:
            headers["X-Audit-Log-Reason"] = reason

        data = {}

        if name:
            data["name"] = name
        if type:
            data["type"] = type  # type: ignore
        if position:
            data["position"] = position  # type: ignore
        if topic:
            data["topic"] = topic
        if nsfw:
            data["nsfw"] = nsfw  # type: ignore
        if slow_mode:
            data["rate_limit_per_user"] = slow_mode  # type: ignore
        if parent_id:
            data["parent_id"] = parent_id  # type: ignore

        url = f"https://discord.com/api/v9/channels/{channel_id}"

        async with self.__session as session:
            if session.closed:
                session = self.recreate()

            async with session.patch(url, headers=headers, json=data) as response:

                if response.status == 400:
                    raise ValueError(f"One or more arguments were invalid")

                return await response.json()

    def recreate(self):
        if self.__session.closed:
            self.__session = aiohttp.ClientSession()

        return self.__session
