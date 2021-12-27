import disnake
from disnake import ApplicationCommandInteraction as AppCmdInter
from disnake.ext import commands


class TestCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(description="Test command.")
    async def test(self, inter: AppCmdInter):
        await inter.response.send_message("test")

    # @slash_command(description="Test command")
    # async def test_pages(self, inter: SlashInteraction, num_pages: int):
    #     embeds = []
    #     for i in range(0, num_pages):
    #         embeds.append(
    #             await create_bot_author_embed(self.bot.keys, title=f"testcog{i + 1}")
    #         )
    #
    #     await create_paginated_embed(inter, embeds)
    #
    # @slash_command(description="Test command")
    # async def test_menu(self, inter: SlashInteraction):
    #     menu = [
    #         SelectMenu(
    #             custom_id="testcog",
    #             placeholder="Choose up to 2 options",
    #             max_values=2,
    #             options=[
    #                 SelectOption("Option 1", "value 1"),
    #                 SelectOption("Option 2", "value 2"),
    #                 SelectOption("Option 3", "value 3"),
    #             ],
    #         )
    #     ]
    #     msg = await inter.reply("This message has a select menu!", components=menu)
    #
    #     def check(menu_inter):
    #         nonlocal inter
    #         return menu_inter.author == inter.author
    #
    #     menu_inter = await msg.wait_for_dropdown(check)
    #     labels = [option.label for option in menu_inter.select_menu.selected_options]
    #     await menu_inter.reply(f"Your choices: {', '.join(labels)}")
    #
    # @user_command(name="Created at")
    # async def created_at(self, inter: ContextMenuInteraction):
    #     # User commands always have only this ^ argument
    #     await inter.respond(
    #         f"{inter.user} was created at {inter.user.created_at}",
    #         ephemeral=True,  # Make the message visible only to the author
    #     )


def setup(bot: commands.AutoShardedBot):
    bot.add_cog(TestCog(bot))
