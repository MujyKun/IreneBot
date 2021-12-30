import disnake
from disnake.ext import commands
from disnake import ApplicationCommandInteraction as AppCmdInter
from random import choice, randint
from re import findall

class MiscellaneousCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="8ball", description="Ask the 8ball a question.")
    async def _8ball(self, inter: AppCmdInter,
                     question: str = commands.Param(description="Question to ask the 8ball.")):
        await inter.send(f"**Question**: {question}\n" + f"**Answer**: Not implemented yet.")
        # TODO: add 8ball responses from the database

    @commands.slash_command(description="Choose between a selection of options.")
    async def choose(self,
                     inter: AppCmdInter,
                     choices: str = commands.Param(description="List the different options with `|` between choices")):
        random_selection = choice(choices.split("|"))
        possible_choices = choices.split("|")
        possible_choices = str.join(", ", ["`" + my_choice + "`" for my_choice in possible_choices])
        await inter.send(f"**Possible Choices**: {possible_choices}\n" + f"**Selection**: `{random_selection}`")

    @commands.slash_command(description="Display Emoji")
    async def displayemoji(self,
                           inter: AppCmdInter,
                           emoji_content: str = commands.Param(description="Emoji to be displayed")):
        if not emoji_content:
            await inter.send("No emote detected.", ephemeral=True)
            return
        emoji_infos = findall(r"<a?:?\w+:[0-9]{18}>", emoji_content)
        if not emoji_infos:
            await inter.send("No emote content detected. It may be a default system emote.", ephemeral=True)
            return
        emoji_urls = [disnake.PartialEmoji.from_str(emoji_info).url for emoji_info in emoji_infos]
        await inter.send("\n".join(emoji_urls))

    #
    # @message_command(name="Display Emoji")
    # async def displayemoji_app(self, inter: ContextMenuInteraction):
    #     emoji_content = inter.message.system_content
    #     if not emoji_content:
    #         await inter.respond("No emote detected.", ephemeral=True)
    #         return
    #     emoji_info = findall(r"<(a?):?\w+:([0-9]{18})>", emoji_content)
    #     if not emoji_info:
    #         await inter.respond("No emote content detected. It may be a default system emote.", ephemeral=True)
    #         return
    #     emoji_urls = [f"https://cdn.discordapp.com/emojis/{emoji_id}.{'gif' if isAnimated else 'png'}" for
    #                   isAnimated, emoji_id in emoji_info]
    #     await inter.respond("\n".join(emoji_urls))
    #
    # @slash_command(name="displayemoji", description="Display png or gif of the emoji.")
    # async def displayemoji_command(self, inter: SlashInteraction,
    #                                emoji_content: str = OptionParam(desc="Emoji to be displayed")):
    #     if not emoji_content:
    #         await inter.respond("No emote detected.", ephemeral=True)
    #         return
    #     emoji_info = findall(r"<(a?):?\w+:([0-9]{18})>", emoji_content)
    #     if not emoji_info:
    #         await inter.respond("No emote content detected. It may be a default system emote.", ephemeral=True)
    #         return
    #     emoji_urls = [f"https://cdn.discordapp.com/emojis/{emoji_id}.{'gif' if isAnimated else 'png'}" for
    #                   isAnimated, emoji_id in emoji_info]
    #     await inter.respond("\n".join(emoji_urls))
    #
    # @slash_command(description="Flip a coin.")
    # async def flip(self, inter: SlashInteraction):
    #     await inter.respond(f"You flipped **{choice(['Tails', 'Heads'])}**.")
    #
    # @slash_command(description="Pick a random number between start_number and end_number.")
    # async def random(self, inter: SlashInteraction,
    #                  start_number: int = OptionParam(desc="start of range"),
    #                  end_number: int = OptionParam(desc="end of range")):
    #     await inter.respond(randint(start_number, end_number))
    #
    # @slash_command(description="Display server info.")
    # async def serverinfo(self, inter: SlashInteraction):
    #     try:
    #         guild = inter.guild
    #         embed = await create_bot_author_embed(self.bot.keys, title=f"{guild.name} ({guild.id})", url=f"{guild.icon_url}")
    #         embed.set_thumbnail(url=guild.icon_url)
    #         fields = {"Owner": f"{guild.owner} ({guild.owner.id})",
    #                   "Users": guild.member_count,
    #                   "Roles": f"{len(guild.roles)}",
    #                   "Emojis": f"{len(guild.emojis)}",
    #                   "Description": guild.description,
    #                   "Channels": f"{len(guild.channels)}",
    #                   "AFK Timeout": f"{guild.afk_timeout / 60} minutes",
    #                   "Since": guild.created_at
    #                   }
    #         embed = await add_embed_inline_fields(embed, fields)
    #         await inter.respond(embed=embed)
    #     except Exception as e:
    #         pass
    #         # TODO: Add exception handling
    #
    # @slash_command(description="Get bot ping.")
    # async def ping(self, inter: SlashInteraction):
    #     await inter.respond(f"> My ping is currently {int(self.bot.latency*1000)}ms")
    #
    # @slash_command(description="Show information about the bot and its creator.")
    # async def botinfo(self, inter: SlashInteraction):
    #     bot = self.bot
    #     embed = await create_bot_author_embed(bot.keys, title=f"I am {bot.keys.bot_name}!")
    #     inline_fields = {"Servers Connected": f"{botstatus.get_server_count(bot)}",
    #                      "Playing Guessing/Bias/Unscramble/Blackjack": "Not Implemented",
    #                      "Ping": f"{botstatus.get_bot_ping(bot)}ms",
    #                      "Shards": f"{bot.shard_count}",
    #                      "Bot Owner": f"<@{bot.keys.bot_owner_id}>"}
    #     embed = await add_embed_inline_fields(embed, inline_fields)
    #     buttons = await get_bot_info_buttons(bot)
    #     await inter.respond(embed=embed, components=buttons)
    #
    #


def setup(bot: commands.AutoShardedBot):
    bot.add_cog(MiscellaneousCog(bot))
