import disnake
from models import Bot
from disnake.ext import commands, tasks
from disnake import ApplicationCommandInteraction as AppCmdInter
from . import helper


class InteractionsCog(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.allowed_mentions = disnake.AllowedMentions(everyone=False, roles=False)

    @commands.command(name="hug", description="Hug someone.")
    async def regular_hug(self, ctx: commands.Context, member: disnake.Member):
        await helper.process_interaction(
            interaction_type="hug",
            past_tense_interaction="hugged",
            attacker=ctx.author,
            victim=member,
            ctx=ctx,
            allowed_mentions=self.allowed_mentions,
        )

    @commands.command(name="lick", description="Lick someone.")
    async def regular_lick(self, ctx: commands.Context, member: disnake.Member):
        await helper.process_interaction(
            interaction_type="lick",
            past_tense_interaction="licked",
            attacker=ctx.author,
            victim=member,
            ctx=ctx,
            allowed_mentions=self.allowed_mentions,
        )

    @commands.command(name="slap", description="Slap someone.")
    async def regular_slap(self, ctx: commands.Context, member: disnake.Member):
        await helper.process_interaction(
            interaction_type="slap",
            past_tense_interaction="slapped",
            attacker=ctx.author,
            victim=member,
            ctx=ctx,
            allowed_mentions=self.allowed_mentions,
        )

    @commands.command(name="kiss", description="Kiss someone.")
    async def regular_kiss(self, ctx: commands.Context, member: disnake.Member):
        await helper.process_interaction(
            interaction_type="kiss",
            past_tense_interaction="kissed",
            attacker=ctx.author,
            victim=member,
            ctx=ctx,
            allowed_mentions=self.allowed_mentions,
        )

    @commands.command(name="pat", description="Pat someone.")
    async def regular_pat(self, ctx: commands.Context, member: disnake.Member):
        await helper.process_interaction(
            interaction_type="pat",
            past_tense_interaction="patted",
            attacker=ctx.author,
            victim=member,
            ctx=ctx,
            allowed_mentions=self.allowed_mentions,
        )

    @commands.command(name="punch", description="Punch someone.")
    async def regular_punch(self, ctx: commands.Context, member: disnake.Member):
        await helper.process_interaction(
            interaction_type="punch",
            past_tense_interaction="punched",
            attacker=ctx.author,
            victim=member,
            ctx=ctx,
            allowed_mentions=self.allowed_mentions,
        )

    @commands.command(name="spit", description="Spit on someone.")
    async def regular_spit(self, ctx: commands.Context, member: disnake.Member):
        await helper.process_interaction(
            interaction_type="spit",
            past_tense_interaction="spit on",
            attacker=ctx.author,
            victim=member,
            ctx=ctx,
            allowed_mentions=self.allowed_mentions,
        )

    @commands.command(name="choke", description="Choke someone.")
    async def regular_choke(self, ctx: commands.Context, member: disnake.Member):
        await helper.process_interaction(
            interaction_type="choke",
            past_tense_interaction="choked",
            attacker=ctx.author,
            victim=member,
            ctx=ctx,
            allowed_mentions=self.allowed_mentions,
        )

    @commands.command(name="cuddle", description="Cuddle someone.")
    async def regular_cuddle(self, ctx: commands.Context, member: disnake.Member):
        await helper.process_interaction(
            interaction_type="cuddle",
            past_tense_interaction="cuddled",
            attacker=ctx.author,
            victim=member,
            ctx=ctx,
            allowed_mentions=self.allowed_mentions,
        )

    @commands.command(name="stab", description="Stab someone.")
    async def regular_stab(self, ctx: commands.Context, member: disnake.Member):
        await helper.process_interaction(
            interaction_type="stab",
            past_tense_interaction="stabbed",
            attacker=ctx.author,
            victim=member,
            ctx=ctx,
            allowed_mentions=self.allowed_mentions,
        )

    @commands.command(name="stepon", description="Step on someone.")
    async def regular_stepon(self, ctx: commands.Context, member: disnake.Member):
        await helper.process_interaction(
            interaction_type="stepon",
            past_tense_interaction="stepped on",
            attacker=ctx.author,
            victim=member,
            ctx=ctx,
            allowed_mentions=self.allowed_mentions,
        )

    @commands.command(name="pullhair", description="Pull the hair of someone.")
    async def regular_pullhair(self, ctx: commands.Context, member: disnake.Member):
        await helper.process_interaction(
            interaction_type="pullhair",
            past_tense_interaction="pulled the hair of",
            attacker=ctx.author,
            victim=member,
            ctx=ctx,
            allowed_mentions=self.allowed_mentions,
        )

    # ==============
    # SLASH COMMANDS
    # ==============
    @commands.slash_command(name="hug", description="Hug someone.")
    async def hug(self, inter: AppCmdInter, member: disnake.Member):
        await helper.process_interaction(
            interaction_type="hug",
            past_tense_interaction="hugged",
            attacker=inter.author,
            victim=member,
            inter=inter,
            allowed_mentions=self.allowed_mentions,
        )

    @commands.slash_command(name="lick", description="Lick someone.")
    async def lick(self, inter: AppCmdInter, member: disnake.Member):
        await helper.process_interaction(
            interaction_type="lick",
            past_tense_interaction="licked",
            attacker=inter.author,
            victim=member,
            inter=inter,
            allowed_mentions=self.allowed_mentions,
        )

    @commands.slash_command(name="slap", description="Slap someone.")
    async def slap(self, inter: AppCmdInter, member: disnake.Member):
        await helper.process_interaction(
            interaction_type="slap",
            past_tense_interaction="slapped",
            attacker=inter.author,
            victim=member,
            inter=inter,
            allowed_mentions=self.allowed_mentions,
        )

    @commands.slash_command(name="kiss", description="Kiss someone.")
    async def kiss(self, inter: AppCmdInter, member: disnake.Member):
        await helper.process_interaction(
            interaction_type="kiss",
            past_tense_interaction="kissed",
            attacker=inter.author,
            victim=member,
            inter=inter,
            allowed_mentions=self.allowed_mentions,
        )

    @commands.slash_command(name="pat", description="Pat someone.")
    async def pat(self, inter: AppCmdInter, member: disnake.Member):
        await helper.process_interaction(
            interaction_type="pat",
            past_tense_interaction="patted",
            attacker=inter.author,
            victim=member,
            inter=inter,
            allowed_mentions=self.allowed_mentions,
        )

    @commands.slash_command(name="punch", description="Punch someone.")
    async def punch(self, inter: AppCmdInter, member: disnake.Member):
        await helper.process_interaction(
            interaction_type="punch",
            past_tense_interaction="punched",
            attacker=inter.author,
            victim=member,
            inter=inter,
            allowed_mentions=self.allowed_mentions,
        )

    @commands.slash_command(name="spit", description="Spit on someone.")
    async def spit(self, inter: AppCmdInter, member: disnake.Member):
        await helper.process_interaction(
            interaction_type="spit",
            past_tense_interaction="spit on",
            attacker=inter.author,
            victim=member,
            inter=inter,
            allowed_mentions=self.allowed_mentions,
        )

    @commands.slash_command(name="choke", description="Choke someone.")
    async def choke(self, inter: AppCmdInter, member: disnake.Member):
        await helper.process_interaction(
            interaction_type="choke",
            past_tense_interaction="choked",
            attacker=inter.author,
            victim=member,
            inter=inter,
            allowed_mentions=self.allowed_mentions,
        )

    @commands.slash_command(name="cuddle", description="Cuddle someone.")
    async def cuddle(self, inter: AppCmdInter, member: disnake.Member):
        await helper.process_interaction(
            interaction_type="cuddle",
            past_tense_interaction="cuddled",
            attacker=inter.author,
            victim=member,
            inter=inter,
            allowed_mentions=self.allowed_mentions,
        )

    @commands.slash_command(name="stab", description="Stab someone.")
    async def stab(self, inter: AppCmdInter, member: disnake.Member):
        await helper.process_interaction(
            interaction_type="stab",
            past_tense_interaction="stabbed",
            attacker=inter.author,
            victim=member,
            inter=inter,
            allowed_mentions=self.allowed_mentions,
        )

    @commands.slash_command(name="stepon", description="Step on someone.")
    async def stepon(self, inter: AppCmdInter, member: disnake.Member):
        await helper.process_interaction(
            interaction_type="stepon",
            past_tense_interaction="stepped on",
            attacker=inter.author,
            victim=member,
            inter=inter,
            allowed_mentions=self.allowed_mentions,
        )

    @commands.slash_command(name="pullhair", description="Pull the hair of someone.")
    async def pullhair(self, inter: AppCmdInter, member: disnake.Member):
        await helper.process_interaction(
            interaction_type="pullhair",
            past_tense_interaction="pulled the hair of",
            attacker=inter.author,
            victim=member,
            inter=inter,
            allowed_mentions=self.allowed_mentions,
        )


def setup(bot: Bot):
    cog = InteractionsCog(bot)
    bot.add_cog(cog)
