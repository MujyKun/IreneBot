from disnake.ext.commands import InvokableMessageCommand, InvokableSlashCommand, \
    InvokableUserCommand, slash_core, HelpCommand
from keys import get_keys


class Command:
    def __init__(self, cog_name="None", name="None", description="None", syntax="None", permissions="None", notes="None", children=None):
        self.cog_name = cog_name
        self.name = name
        self.description = description
        self.syntax = syntax
        self.permissions = permissions
        self.notes = notes
        self.children = children or []

    def to_dict(self):
        return {
            "name": self.name,
            "description": self.description,
            "syntax": self.syntax,
            "permissions": self.permissions,
            "notes": self.notes
        }


class MessageCommand(Command):
    def __init__(self, command: InvokableMessageCommand):
        name = command.body.name or "None"
        description = command.extras.get("description", "None")
        syntax = command.extras.get("syntax", "Right click a message -> Apps -> Click Command")
        permissions = command.extras.get("permissions", "None")
        notes = command.extras.get("notes", "None")
        cog_name = command.cog_name or "None"
        super().__init__(cog_name=cog_name, name=name, description=description, syntax=syntax, permissions=permissions, notes=notes)


class SubCommand(Command):
    def __init__(self, command: slash_core.SubCommand):
        name = command.qualified_name

        description = None
        if hasattr(command, "body"):
            description = command.body.description
        elif hasattr(command, "description"):
            description = command.description

        if not description or description == "-":
            description = command.extras.get("description", "None")

        syntax = command.extras.get("syntax", "None")
        permissions = command.extras.get("permissions", "None")
        notes = command.extras.get("notes", "This is a sub-command.")
        cog_name = command.cog_name or "None"
        super().__init__(cog_name=cog_name, name=name, description=description, syntax=syntax, permissions=permissions, notes=notes)


class SlashCommand(Command):
    def __init__(self, command: InvokableSlashCommand):
        name = command.body.name or "None"
        description = command.description or command.extras.get("description", "None")
        syntax = command.extras.get("syntax", f"Type /{name} in chat to see the syntax.")
        permissions = command.extras.get("permissions", "None")
        notes = command.extras.get("notes", "None")
        cog_name = command.cog_name or "None"
        children = [SubCommand(_command) for _command in command.children.values()]
        super().__init__(cog_name=cog_name, name=name, description=description, syntax=syntax, permissions=permissions, notes=notes, children=children)


class RegularCommand(Command):
    def __init__(self, command):
        cog_name = f"{command.cog_name}" if command.cog_name else "None"
        name = f"{get_keys().bot_prefix}{command.name}"
        description = command.description
        syntax = self.get_signature(command) or "None"
        permissions = command.extras.get("permissions", "None")
        notes = command.extras.get("notes", "None")
        children = [SubCommand(_command) for _command in getattr(command, "all_commands", {}).values()]
        super().__init__(cog_name=cog_name, name=name, description=description, syntax=syntax, permissions=permissions, notes=notes, children=children)

    @staticmethod
    def get_signature(command):
        parent = command.parent
        entries = []
        while parent is not None:
            if not parent.signature or parent.invoke_without_command:
                entries.append(parent.name)
            else:
                entries.append(f"{parent.name} {parent.signature}")
            parent = parent.parent
        parent_sig = " ".join(reversed(entries))

        if len(command.aliases) > 0:
            aliases = "|".join(command.aliases)
            fmt = f"[{command.name}|{aliases}]"
            if parent_sig:
                fmt = f"{parent_sig} {fmt}"
            alias = fmt
        else:
            alias = command.name if not parent_sig else f"{parent_sig} {command.name}"

        return f"{get_keys().bot_prefix}{alias} {command.signature}"


class UserCommand(Command):
    def __init__(self, command: InvokableUserCommand):
        cog_name = command.cog_name
        name = command.qualified_name
        description = command.extras.get("description", "None")
        syntax = command.extras.get("syntax", "Right click a User -> Apps -> Click Command")
        permissions = command.extras.get("permissions", "None")
        notes = command.extras.get("notes", "None")
        super(UserCommand, self).__init__(cog_name, name, description, syntax, permissions, notes)


def get_cog_dicts(commands, command_class):
    cog_dicts = []
    for command in commands:
        command_obj = command_class(command)
        command_as_dict = command_obj.to_dict()
        cog = next((cog for cog in cog_dicts if cog.get('name') == command.cog_name), None)
        if cog is None:
            cog = {"name": command.cog_name, "commands": []}
            cog_dicts.append(cog)
        cog["commands"].append(command_as_dict)
        for child in command_obj.children:
            cog["commands"].append(child.to_dict())
    return cog_dicts
