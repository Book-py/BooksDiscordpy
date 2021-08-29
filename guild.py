import typing as t
import sys


class Guild:
    def __getitem__(self, key: t.Any):
        pass

    def __init__(self, bot, json):
        self.bot = bot

        self.roles = json["roles"]
        self.id = json["id"]
        self.name = json["name"]
        self.icon = json["icon"]
        self.description = json["description"]
        self.splash = json["splash"]
        self.discovery_splash = json["discovery_splash"]
        self.features = json["features"]
        self.stickers = json["stickers"]
        self.banner = json["banner"]
        self.owner_id = json["owner_id"]
        self.region = json["region"]
        self.afk_channel_id = json["afk_channel_id"]
        self.afk_timeout = json["afk_timeout"]
        self.system_channel_id = json["system_channel_id"]
        self.widget_enabled = json["widget_enabled"]
        self.widget_channel_id = json["widget_channel_id"]
        self.verification_level = json["verification_level"]
        self.roles = json["roles"]

        self.default_message_notifications = json["default_message_notifications"]
        self.mfa_level = json["mfa_level"]
        self.explicit_content_filter = json["explicit_content_filter"]
        self.max_presences = json["max_presences"]
        self.max_members = json["max_members"]
        self.max_video_channel_users = json["max_video_channel_users"]
        self.vanity_url_code = json["vanity_url_code"]
        self.premium_tier = json["premium_tier"]
        self.premium_subscription_count = json["premium_subscription_count"]
        self.system_channel_flags = json["system_channel_flags"]
        self.preferred_locale = json["preferred_locale"]
        self.rules_channel_id = json["rules_channel_id"]
        self.public_updates_channel_id = json["public_updates_channel_id"]
        self.nsfw = json["nsfw"]
        self.nsfw_level = json["nsfw_level"]

        # json.pop("emojis", None)
        # json.pop("roles", None)
        # print(json)
