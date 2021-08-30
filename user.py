import typing as t


class User:
    def __init__(self, json: dict, bot):
        # print(json.keys())

        self.verified = json.get("verified", False)
        self.username = json.get("username", None)
        self.mfa_enabled = json.get("mfa_enabled", False)
        self.id = json.get("id")
        self.flags = json.get("flags", None)
        self.email = json.get("email", None)
        self.discriminator = json.get("discriminator", None)
        self.bot = json.get("bot", False)
        self.avatar = json.get("avatar", None)

        self._bot = bot
