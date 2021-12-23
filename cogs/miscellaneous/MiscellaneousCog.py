from discord.ext import commands
from dislash import slash_command, message_command, \
    SlashInteraction, ContextMenuInteraction, OptionParam
from random import choice, randint
from re import findall
from util.BotEmbed import create_bot_author_embed, add_embed_inline_fields


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


def setup(bot: commands.AutoShardedBot):
    bot.add_cog(MiscellaneousCog(bot))
