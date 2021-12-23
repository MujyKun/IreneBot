from discord.ext import commands
from dislash import slash_command, message_command, \
    SlashInteraction, ContextMenuInteraction, OptionParam, SelectMenu, SelectOption, user_command
from random import choice, randint
from re import findall
from util.BotEmbed import create_bot_author_embed, add_embed_inline_fields, create_paginated_embed, get_bot_info_buttons
import util.BotStatus as botstatus

class MiscellaneousCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(name="8ball", description="Asks the 8ball a question.")
    async def _8ball(self, inter: SlashInteraction,
                     question: str = OptionParam(desc="Question for 8ball")):
        await inter.respond(f"**Question**: {question}\n" + f"**Answer**: hi")
        # TODO: add 8ball responses from the database

    @slash_command(description="Choose between a selection of options.")
    async def choose(self, inter: SlashInteraction,
                     choices: str = OptionParam(desc="List the different options with spaces between choices")):
        random_selection = choice(choices.split(" "))
        possible_choices = choices.split(" ")
        possible_choices = str.join(", ", ["`" + my_choice + "`" for my_choice in possible_choices])
        await inter.respond(f"**Possible Choices**: {possible_choices}\n" + f"**Selection**: `{random_selection}`")

    @message_command(name="Display Emoji")
    async def displayemoji_app(self, inter: ContextMenuInteraction):
        emoji_content = inter.message.system_content
        if not emoji_content:
            await inter.respond("No emote detected.", ephemeral=True)
            return
        emoji_info = findall(r"<(a?):?\w+:([0-9]{18})>", emoji_content)
        if not emoji_info:
            await inter.respond("No emote content detected. It may be a default system emote.", ephemeral=True)
            return
        emoji_urls = [f"https://cdn.discordapp.com/emojis/{emoji_id}.{'gif' if isAnimated else 'png'}" for
                      isAnimated, emoji_id in emoji_info]
        await inter.respond("\n".join(emoji_urls))

    @slash_command(name="displayemoji", description="Display png or gif of the emoji.")
    async def displayemoji_command(self, inter: SlashInteraction,
                                   emoji_content: str = OptionParam(desc="Emoji to be displayed")):
        if not emoji_content:
            await inter.respond("No emote detected.", ephemeral=True)
            return
        emoji_info = findall(r"<(a?):?\w+:([0-9]{18})>", emoji_content)
        if not emoji_info:
            await inter.respond("No emote content detected. It may be a default system emote.", ephemeral=True)
            return
        emoji_urls = [f"https://cdn.discordapp.com/emojis/{emoji_id}.{'gif' if isAnimated else 'png'}" for
                      isAnimated, emoji_id in emoji_info]
        await inter.respond("\n".join(emoji_urls))

    @slash_command(description="Flip a coin.")
    async def flip(self, inter: SlashInteraction):
        await inter.respond(f"You flipped **{choice(['Tails', 'Heads'])}**.")

    @slash_command(description="Pick a random number between start_number and end_number.")
    async def random(self, inter: SlashInteraction,
                     start_number: int = OptionParam(desc="start of range"),
                     end_number: int = OptionParam(desc="end of range")):
        await inter.respond(randint(start_number, end_number))

    @slash_command(description="Display server info.")
    async def serverinfo(self, inter: SlashInteraction):
        try:
            guild = inter.guild
            embed = await create_bot_author_embed(self.bot.keys, title=f"{guild.name} ({guild.id})", url=f"{guild.icon_url}")
            embed.set_thumbnail(url=guild.icon_url)
            fields = {"Owner": f"{guild.owner} ({guild.owner.id})",
                      "Users": guild.member_count,
                      "Roles": f"{len(guild.roles)}",
                      "Emojis": f"{len(guild.emojis)}",
                      "Description": guild.description,
                      "Channels": f"{len(guild.channels)}",
                      "AFK Timeout": f"{guild.afk_timeout / 60} minutes",
                      "Since": guild.created_at
                      }
            embed = await add_embed_inline_fields(embed, fields)
            await inter.respond(embed=embed)
        except Exception as e:
            pass
            # TODO: Add exception handling

    @slash_command(description="Get bot ping.")
    async def ping(self, inter: SlashInteraction):
        await inter.respond(f"> My ping is currently {int(self.bot.latency*1000)}ms")

    @slash_command(description="Show information about the bot and its creator.")
    async def botinfo(self, inter: SlashInteraction):
        bot = self.bot
        embed = await create_bot_author_embed(bot.keys, title=f"I am {bot.keys.bot_name}!")
        inline_fields = {"Servers Connected": f"{botstatus.get_server_count(bot)}",
                         "Playing Guessing/Bias/Unscramble/Blackjack": "Not Implemented",
                         "Ping": f"{botstatus.get_bot_ping(bot)}ms",
                         "Shards": f"{bot.shard_count}",
                         "Bot Owner": f"<@{bot.keys.bot_owner_id}>"}
        embed = await add_embed_inline_fields(embed, inline_fields)
        buttons = await get_bot_info_buttons(bot)
        await inter.respond(embed=embed, components=buttons)

    @slash_command(description="Test command")
    async def test_pages(self, inter: SlashInteraction, num_pages: int):
        embeds = []
        for i in range(0, num_pages):
            embeds.append(await create_bot_author_embed(self.bot.keys, title=f"test{i + 1}"))

        await create_paginated_embed(inter, embeds)

    @slash_command(description="Test command")
    async def test_menu(self, inter: SlashInteraction):
        menu = [
            SelectMenu(
                custom_id="test",
                placeholder="Choose up to 2 options",
                max_values=2,
                options=[
                    SelectOption("Option 1", "value 1"),
                    SelectOption("Option 2", "value 2"),
                    SelectOption("Option 3", "value 3")
                ]
            )
        ]
        msg = await inter.reply("This message has a select menu!", components=menu)

        def check(menu_inter):
            nonlocal inter
            return menu_inter.author == inter.author

        menu_inter = await msg.wait_for_dropdown(check)
        labels = [option.label for option in menu_inter.select_menu.selected_options]
        await menu_inter.reply(f"Your choices: {', '.join(labels)}")

    @user_command(name="Created at")
    async def created_at(self, inter: ContextMenuInteraction):
        # User commands always have only this ^ argument
        await inter.respond(
            f"{inter.user} was created at {inter.user.created_at}",
            ephemeral=True # Make the message visible only to the author
        )

def setup(bot: commands.AutoShardedBot):
    bot.add_cog(MiscellaneousCog(bot))
