from discord.ext import commands
from dislash import slash_command, message_command, ActionRow, Button, ButtonStyle, ResponseType, SlashInteraction, ContextMenuInteraction

class GroupMembersCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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


def setup(bot: commands.AutoShardedBot):
    bot.add_cog(GroupMembersCog(bot))
