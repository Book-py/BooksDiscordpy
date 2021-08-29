import typing as t


class Embed:
    def __init__(
        self, title: t.Optional[str] = None, description: t.Optional[str] = None
    ) -> None:
        self.title = title
        self.description = description

        self.fields: t.List[t.Dict[str, str, bool]] = []  # type: ignore

    def add_field(self, *, name: str, value: str, inline: t.Optional[bool] = False):
        field = {"name": name, "value": value, "inline": inline}
        self.fields.append(field)

    def to_dict(self) -> t.Dict[str, t.Any]:
        embed_dict = {}

        if self.title:
            embed_dict["title"] = self.title
        if self.description:
            embed_dict["description"] = self.description
        if self.fields:
            embed_dict["fields"] = self.fields  # type: ignore

        embed_dict["type"] = "rich"

        return embed_dict
