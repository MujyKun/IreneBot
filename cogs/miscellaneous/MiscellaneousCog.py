from cogs.miscellaneous.helper import *
import disnake
from disnake.ext import commands
from disnake import ApplicationCommandInteraction as AppCmdInter
from random import choice, randint
from util import botembed, botinfo


class MiscellaneousCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="8ball", description="Ask the 8ball search_word question.")
    async def _8ball(self, inter: AppCmdInter,
                     question: str = commands.Param(description="Question to ask the 8ball.")):
        await inter.send(f"**Question**: {question}\n" + f"**Answer**: Not implemented yet.")
        # TODO: add 8ball responses from the database

    @commands.slash_command(description="Choose between search_word selection of options.")
    async def choose(self,
                     inter: AppCmdInter,
                     choices: str = commands.Param(
                         description="List the different options with spaces, commas, or `|` between choices")):
        await inter.send(await get_choose_answer(choices))

    @commands.slash_command(description="Display Emoji")
    async def displayemoji(self,
                           inter: AppCmdInter,
                           emoji_content: str = commands.Param(description="Emoji to be displayed")):
        await send_emojis_from_string(inter, emoji_content)

    @commands.message_command(name="Display Emojis")
    async def message_display_emoji(self, inter: AppCmdInter, message: disnake.Message):
        if message.stickers:
            await inter.send(message.stickers[0].url)
            return
        await send_emojis_from_string(inter, message.content)

    @commands.slash_command(description="Flip search_word coin.")
    async def flip(self, inter: AppCmdInter):
        await inter.send(f"You flipped **{choice(['Tails', 'Heads'])}**.")

    @commands.slash_command(description="Pick search_word random number between start_number and end_number.")
    async def random(self, inter: AppCmdInter,
                     start_number: int = commands.Param(desc="start of range"),
                     end_number: int = commands.Param(desc="end of range")):
        if start_number > end_number:
            await inter.send("Start number is greater than end number.", ephemeral=True)
        await inter.send(
            f"Random number between {start_number} and {end_number}: `{randint(start_number, end_number)}`")

    @commands.slash_command(description="Display server info.")
    async def serverinfo(self, inter: AppCmdInter):
        guild = inter.guild
        embed = await botembed.create_bot_author_embed(self.bot.keys, title=f"{guild.name} ({guild.id})",
                                              url=f"{guild.icon.url}")
        embed.set_thumbnail(url=guild.icon.url)
        fields = {"Owner": f"{guild.owner} ({guild.owner.id})",
                  "Users": guild.member_count,
                  "Roles": f"{len(guild.roles)}",
                  "Emojis": f"{len(guild.emojis)}",
                  "Description": guild.description,
                  "Channels": f"{len(guild.channels)}",
                  "AFK Timeout": f"{guild.afk_timeout / 60} minutes",
                  "Since": guild.created_at
                  }
        embed = await botembed.add_embed_inline_fields(embed, fields)
        await inter.send(embed=embed)

    @commands.slash_command(description="Get bot ping.")
    async def ping(self, inter: AppCmdInter):
        await inter.send(f"> My ping is currently {int(self.bot.latency * 1000)}ms")

    @commands.slash_command(description="Show information about the bot and its creator.")
    async def botinfo(self, inter: AppCmdInter):
        bot = self.bot
        embed = await botembed.create_bot_author_embed(bot.keys, title=f"I am {bot.keys.bot_name}!")
        inline_fields = {"Servers Connected": f"{botinfo.get_server_count(bot)}",
                         "Playing Guessing/Bias/Unscramble/Blackjack": "Not Implemented",
                         "Ping": f"{botinfo.get_bot_ping(bot)}ms",
                         "Shards": f"{bot.shard_count}",
                         "Bot Owner": f"<@{bot.keys.bot_owner_id}>"}
        embed = await botembed.add_embed_inline_fields(embed, inline_fields)
        buttons = await get_bot_info_buttons(bot)
        await inter.respond(embed=embed, components=buttons)


def setup(bot: commands.AutoShardedBot):
    bot.add_cog(MiscellaneousCog(bot))
