import random

from disnake.ext import commands
from models import Bot
from IreneAPIWrapper.models import Media, Person, Group
from disnake.ext import commands
from disnake import ApplicationCommandInteraction as AppCmdInter
from . import helper
from typing import Literal


class GroupMembersCog(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.slash_command(description="Display a profile card for either a Person or a Group.")
    async def card(self, inter: AppCmdInter, item_type: Literal["person", "group"],
                   selection: str = commands.Param(autocomplete=helper.auto_complete_type)):
        """Display a profile card for either a Person or a Group."""
        object_id = int(selection.split(')')[0])
        if item_type == "person":
            person = await Person.get(object_id)
            await inter.send(str(person.name))
        elif item_type == "group":
            group = await Group.get(object_id)
            await inter.send(str(group.name))
        else:
            raise RuntimeError("item_type returned something other than 'person' or 'group'")

    @commands.slash_command(name="randomperson", description="Display media for a Person.")
    async def random_person(self, inter: AppCmdInter):
        """Send a photo of a random person."""
        media: Media = random.choice(list(await Media.get_all()))
        await inter.send(media.source.url)
    # # Example of a slash command in a cog
    # @slash_command(description="Says Hello from Gowon")
    # async def hello(self, inter: SlashInteraction):
    #     # await inter.respond("Annyeong")
    #     pass
    #
    # @hello.sub_command()
    # async def goodmorning(self, inter: SlashInteraction):
    #     await inter.respond("good morning!")
    #
    # @hello.sub_command()
    # async def goodnight(self, inter: SlashInteraction):
    #     await inter.respond("good night!")
    #
    # @hello.sub_command()
    # async def test(self, inter: SlashInteraction):
    #     row_of_buttons = ActionRow(
    #         Button(
    #             style=ButtonStyle.green,
    #             label="Green button",
    #             custom_id="green"
    #         ),
    #         Button(
    #             style=ButtonStyle.red,
    #             label="Red button",
    #             custom_id="red"
    #         )
    #     )
    #     await inter.respond("hi", components=[row_of_buttons])
    #
    # # Buttons in cogs (no changes basically)
    # @commands.command()
    # async def test(self, ctx):
    #     row_of_buttons = ActionRow(
    #         Button(
    #             style=ButtonStyle.green,
    #             label="Green button",
    #             custom_id="green"
    #         ),
    #         Button(
    #             style=ButtonStyle.red,
    #             label="Red button",
    #             custom_id="red"
    #         )
    #     )
    #     msg = await ctx.send("This message has buttons", components=[row_of_buttons])
    #
    #     # Wait for a button click
    #     def check(inter):
    #         return inter.author == ctx.author
    #
    #     inter = await msg.wait_for_button_click(check=check)
    #     # Process the button click
    #     await inter.reply(f"Button: {inter.button.label}", type=ResponseType.UpdateMessage)

    ...


def setup(bot: Bot):
    bot.add_cog(GroupMembersCog(bot))
