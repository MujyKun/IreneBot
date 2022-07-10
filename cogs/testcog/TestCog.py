import disnake
from disnake import ApplicationCommandInteraction as AppCmdInter
from disnake.ext import commands
from views.views import create_embed_paged_view, create_paged_select_dropwdown
from util.botembed import create_embeds_from_list

loona_members = [
    "Haseul",
    "Vivi",
    "Yves",
    "JinSoul",
    "Kim Lip",
    "Chuu",
    "Heejin",
    "Hyunjin",
    "Go Won",
    "Choerry",
    "Olivia Hye",
    "Yeojin",
    "V",
]

loona_members_dict = {member: member for member in loona_members}


async def autocomp_loona(inter: AppCmdInter, user_input: str):
    return [member for member in loona_members if user_input.lower() in member.lower()]


class Dropdown(disnake.ui.Select):
    def __init__(self):

        # Set the options that will be presented inside the dropdown
        options = [
            disnake.SelectOption(label="Red"),
            disnake.SelectOption(label="Green"),
            disnake.SelectOption(label="Blue"),
        ]

        # The placeholder is what will be shown when no option is chosen
        # The min and max values indicate we can only pick one of the three options
        # The options parameter defines the dropdown options. We defined this above
        super().__init__(
            placeholder="Choose your favourite colour...",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: disnake.MessageInteraction):
        # Use the interaction object to send a response message containing
        # the user's favourite colour or choice. The self object refers to the
        # Select object, and the values attribute gets a list of the user's
        # selected options. We only want the first one.
        await interaction.response.send_message(
            f"Your favourite colour is {self.values[0]}"
        )


class DropdownView(disnake.ui.View):
    def __init__(self):
        super().__init__()

        # Adds the dropdown to our view object.
        self.add_item(Dropdown())


class TestCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(description="Test command.")
    async def test(self, inter: AppCmdInter):
        await inter.response.send_message("test")
        await inter.channel.send("test2")
        await inter.channel.send("test3")

    @commands.slash_command(description="Min Max test")
    async def min_max_test(
        self, inter: AppCmdInter, num: int = commands.Param(min_value=1, max_value=10)
    ):
        await inter.response.send_message(f"You chose {num}")

    @commands.slash_command(description="Test Loona Autocomplete")
    async def test_autocomplete(
        self,
        inter: AppCmdInter,
        member: str = commands.Param(autocomplete=autocomp_loona),
    ):
        await inter.response.send_message(f"You selected {member}.")

    @commands.slash_command(description="Test pagination")
    async def test_pagination(self, inter: AppCmdInter, num_pages: int):
        # Creates the embeds as a list.
        embeds = [disnake.Embed(title=f"Test{i+1}") for i in range(num_pages)]

        pages = await create_embed_paged_view(inter.author, embeds)
        await inter.response.send_message(embed=pages.embeds[0], view=pages)

    @commands.slash_command(description="Test pagination")
    async def test_numbered(self, inter: AppCmdInter, num_users: int):
        # Creates the embeds as a list.
        users = [f"User#{i+1}" for i in range(0, num_users)]

        embeds = await create_embeds_from_list(users, title="Test Users")

        pages = await create_embed_paged_view(inter.author, embeds, timeout=5)
        await inter.response.send_message(embed=pages.embeds[0], view=pages)

    @commands.slash_command()
    async def colour(self, inter):
        """Sends a message with our dropdown containing colours"""

        # Create the view containing our dropdown
        view = DropdownView()

        # Sending a message containing our view
        await inter.send("Pick your favourite colour:", view=view)

    @commands.slash_command()
    async def test_select(self, inter: AppCmdInter):
        await inter.response.defer()
        select_view = await create_paged_select_dropwdown(
            inter.author, loona_members_dict
        )
        await inter.followup.send(view=select_view)

    # TODO: remove this since this was for the memes
    @commands.slash_command()
    async def say(self, inter: AppCmdInter, msg):
        await inter.response.send_message("h", ephemeral=True)
        await inter.channel.send(msg)

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
