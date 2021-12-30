import disnake
from disnake import ApplicationCommandInteraction as AppCmdInter
from disnake.ext import commands
from models.views import create_embed_paged_view
from util.botembed import create_embeds_from_list

loona_members = ["Haseul", "Vivi", "Yves", "JinSoul", "Kim Lip", "Chuu", "Heejin", "Hyunjin", "Go Won",
                      "Choerry", "Olivia Hye", "Yeojin", "V"]

async def autocomp_loona(inter: AppCmdInter, user_input: str):
    return [member for member in loona_members if user_input.lower() in member.lower()]

class TestCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(description="Test command.")
    async def test(self, inter: AppCmdInter):
        await inter.response.send_message("test")
        await inter.channel.send("test2")
        await inter.channel.send("test3")

    @commands.slash_command(description="Test Loona Autocomplete")
    async def test_autocomplete(self, inter: AppCmdInter, member: str = commands.Param(autocomplete=autocomp_loona)):
        await inter.response.send_message(f"You selected {member}.")

    @commands.slash_command(description="Test pagination")
    async def test_pagination(self, inter: AppCmdInter, num_pages: int):
        # Creates the embeds as a list.
        embeds = [
            disnake.Embed(title=f"Test{i+1}") for i in range(num_pages)
        ]

        pages = await create_embed_paged_view(inter.author, embeds)
        await inter.response.send_message(embed=pages.embeds[0], view=pages)

    @commands.slash_command(description="Test pagination")
    async def test_numbered(self, inter: AppCmdInter, num_users: int):
        # Creates the embeds as a list.
        users = [f"User#{i+1}" for i in range(0, num_users)]

        embeds = await create_embeds_from_list(users, title="Test Users")

        pages = await create_embed_paged_view(inter.author, embeds, timeout=5)
        await inter.response.send_message(embed=pages.embeds[0], view=pages)

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
