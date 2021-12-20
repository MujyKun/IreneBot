from discord.ext import commands
from discord import Embed
from dislash import slash_command, message_command, \
    SlashInteraction, ContextMenuInteraction, OptionParam
from random import choice, randint
from re import findall


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
        possible_choices = ", ".join(["`" + my_choice + "`" for my_choice in possible_choices])
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

    @slash_command(name="displayemoji", desc="Display png or gif of the emoji.")
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

    @slash_command(desc="Flip a coin.")
    async def flip(self, inter: SlashInteraction):
        await inter.respond(f"You flipped **{choice(['Tails', 'Heads'])}**.")

    @slash_command(desc="Pick a random number between start_number and end_number.")
    async def random(self, inter: SlashInteraction,
                     start_number: int = OptionParam(desc="start of range"),
                     end_number: int = OptionParam(desc="end of range")):
        await inter.respond(randint(start_number, end_number))

    @slash_command(desc="Display server info.")
    async def serverinfo(self, inter: SlashInteraction):
        try:
            guild = inter.guild
            embed = Embed(title=f"{guild.name} ({guild.id})", color=0xffb6c1, url=f"{guild.icon_url}")
            embed.set_author(name="Irene", url=self.bot.keys.bot_website_url,
                             icon_url='https://cdn.discordapp.com/emojis/693392862611767336.gif?v=1')
            embed.set_footer(text="Thanks for using Irene.",
                             icon_url='https://cdn.discordapp.com/emojis/683932986818822174.gif?v=1')
            embed.set_thumbnail(url=guild.icon_url)
            embed.add_field(name="Owner", value=f"{guild.owner} ({guild.owner.id})", inline=True)
            embed.add_field(name="Region", value=guild.region, inline=True)
            embed.add_field(name="Users", value=guild.member_count, inline=True)
            embed.add_field(name="Roles", value=f"{len(guild.roles)}", inline=True)
            embed.add_field(name="Emojis", value=f"{len(guild.emojis)}", inline=True)
            embed.add_field(name="Description", value=guild.description, inline=True)
            embed.add_field(name="Channels", value=f"{len(guild.channels)}", inline=True)
            embed.add_field(name="AFK Timeout", value=f"{guild.afk_timeout / 60} minutes", inline=True)
            embed.add_field(name="Since", value=guild.created_at, inline=True)

            await inter.respond(embed=embed)
        except Exception as e:
            pass
            # TODO: Add exception handling


def setup(bot: commands.AutoShardedBot):
    bot.add_cog(MiscellaneousCog(bot))
