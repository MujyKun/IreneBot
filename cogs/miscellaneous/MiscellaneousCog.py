from . import helper
import disnake
from disnake.ext import commands
from disnake import ApplicationCommandInteraction as AppCmdInter
from random import choice, randint
from util import botembed, botinfo


class MiscellaneousCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.allowed_mentions = disnake.AllowedMentions(everyone=False, roles=False)

    ##################
    # REGULAR COMMANDS
    ##################
    @commands.command(name="serverinfo", description="Display server info.")
    async def regular_server_info(self, ctx):
        await helper.process_server_info(guild=ctx.guild, ctx=ctx)

    @commands.command(
        name="botinfo", description="Show information about the bot and its creator."
    )
    async def regular_bot_info(self, ctx):
        await helper.process_bot_info(self.bot, ctx=ctx)

    @commands.command(name="invite", description="Get an invite link for the bot.")
    async def regular_invite(self, ctx: commands.Context):
        await helper.send_bot_invite(
            user_id=ctx.author.id, ctx=ctx, allowed_mentions=self.allowed_mentions
        )

    @commands.command(name="stopgames", description="Stop all games you are hosting.")
    async def regular_stop_games(self, ctx: commands.Context):
        await helper.process_stop_games(
            user_id=ctx.author.id, ctx=ctx, allowed_mentions=self.allowed_mentions
        )

    @commands.command(
        name="choose", description="Choose between a selection of options."
    )
    async def regular_choose(self, ctx: commands.Context, *, choices: str):
        await helper.process_choose(
            choices=choices,
            user_id=ctx.author.id,
            ctx=ctx,
            allowed_mentions=self.allowed_mentions,
        )

    @commands.command(name="8ball", description="Ask the 8ball a question.")
    async def regular_eightball(self, ctx: commands.Context, *, question: str):
        await helper.process_8ball(
            prompt=question,
            ctx=ctx,
            user_id=ctx.author.id,
            allowed_mentions=self.allowed_mentions,
        )

    @commands.command(name="ping", description="Get the ping of the bot.")
    async def regular_ping(self, ctx: commands.Context):
        await helper.process_ping(
            latency=botinfo.get_bot_ping(self.bot),
            user_id=ctx.author.id,
            ctx=ctx,
            allowed_mentions=self.allowed_mentions,
        )

    @commands.command(name="random", description="Pick a random number between a start and end number.")
    async def regular_random(
        self,
        ctx,
        start_number: int,
        end_number: int
    ):
        await helper.process_random(start_number=start_number, end_number=end_number,
                                    invoker_user_id=ctx.author.id, ctx=ctx)

    ################
    # SLASH COMMANDS
    ################

    @commands.slash_command(
        name="invite", description="Get an invite link for the bot."
    )
    async def invite(self, inter: AppCmdInter):
        await helper.send_bot_invite(
            user_id=inter.author.id, inter=inter, allowed_mentions=self.allowed_mentions
        )

    @commands.slash_command(
        name="stopgames", description="Stop all games you are hosting."
    )
    async def stop_games(self, inter: AppCmdInter):
        await helper.process_stop_games(
            user_id=inter.user.id, inter=inter, allowed_mentions=self.allowed_mentions
        )

    @commands.slash_command(name="8ball", description="Ask the 8ball a question.")
    async def eight_ball(
        self,
        inter: AppCmdInter,
        question: str = commands.Param(description="Question to ask the 8ball."),
    ):
        await helper.process_8ball(
            prompt=question,
            inter=inter,
            user_id=inter.author.id,
            allowed_mentions=self.allowed_mentions,
        )

    @commands.slash_command(description="Choose between a selection of options.")
    async def choose(
        self,
        inter: AppCmdInter,
        choices: str = commands.Param(
            description="List the different options with commas, or '|' between choices."
        ),
    ):
        await helper.process_choose(
            choices=choices,
            user_id=inter.author.id,
            inter=inter,
            allowed_mentions=self.allowed_mentions,
        )

    @commands.slash_command(name="displayemoji", description="Display Emoji")
    async def slash_display_emoji(
        self,
        inter: AppCmdInter,
        emoji_content: str = commands.Param(description="Emoji to be displayed"),
    ):
        await helper.process_display_emoji(
            message=emoji_content, invoker_user_id=inter.user.id, inter=inter
        )

    @commands.slash_command(description="Flip a coin.")
    async def flip(self, inter: AppCmdInter):
        await inter.send(f"You flipped **{choice(['Tails', 'Heads'])}**.")

    @commands.slash_command(
        description="Pick a random number between start_number and end_number."
    )
    async def random(
        self,
        inter: AppCmdInter,
        start_number: int = commands.Param(desc="start of range"),
        end_number: int = commands.Param(desc="end of range"),
    ):
        await helper.process_random(start_number=start_number, end_number=end_number, invoker_user_id=inter.author.id,
                                    inter=inter)

    @commands.slash_command(name="serverinfo", description="Display server info.")
    async def server_info(self, inter: AppCmdInter):
        await helper.process_server_info(guild=inter.guild, inter=inter)

    @commands.slash_command(name="ping", description="Get the ping of the bot.")
    async def ping(self, inter: AppCmdInter):
        await helper.process_ping(
            latency=botinfo.get_bot_ping(self.bot),
            user_id=inter.author.id,
            inter=inter,
            allowed_mentions=self.allowed_mentions,
        )

    @commands.slash_command(
        name="botinfo", description="Show information about the bot and its creator."
    )
    async def slash_bot_info(self, inter: AppCmdInter):
        await helper.process_bot_info(self.bot, inter=inter)

    @commands.slash_command(name="urban", description="Search Urban Dictionary")
    async def slash_urban_dictionary(self, inter: AppCmdInter, phrase: str, definition_number: int = 1):
        await helper.process_urban(phrase=phrase, definition_number=definition_number, invoker_user_id=inter.author.id,
                                   inter=inter,  allowed_mentions=self.allowed_mentions)

    @commands.command(name="urban", description="")
    async def regular_urban_dictionary(self, ctx, phrase: str, definition_number=1):
        """Search Urban Dictionary (Underscores are spaces)"""
        await helper.process_urban(phrase=phrase.replace("_", " "), definition_number=definition_number,
                                   invoker_user_id=ctx.author.id, ctx=ctx, allowed_mentions=self.allowed_mentions)

    ##################
    # MESSAGE COMMANDS
    ##################
    @commands.message_command(
        name="Display Emojis", extras={"description": "Display Emojis in a Message."}
    )
    async def message_display_emoji(self, inter: AppCmdInter, message: disnake.Message):
        await helper.process_display_emoji(
            message, invoker_user_id=inter.user.id, inter=inter
        )

    @commands.message_command(
        name="8ball", extras={"description": "Make this message an 8ball question."}
    )
    async def message_eight_ball(self, inter: AppCmdInter, message: disnake.Message):
        await helper.process_8ball(
            prompt=message.content or "None",
            inter=inter,
            user_id=inter.author.id,
            allowed_mentions=self.allowed_mentions,
        )


def setup(bot: commands.AutoShardedBot):
    bot.add_cog(MiscellaneousCog(bot))
