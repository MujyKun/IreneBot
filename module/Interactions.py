import discord
from random import randint, choice
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from IreneUtility.util import u_logger as log
from IreneUtility.Utility import Utility


class Interactions(commands.Cog):
    def __init__(self, t_ex):
        self.ex: Utility = t_ex

    async def cog_check(self, ctx):
        """A local check for this cog. Checks if the current interaction is enabled in the server."""
        return await self.ex.check_interaction_enabled(ctx)

    @commands.command()
    @commands.cooldown(1, 60, BucketType.user)
    async def stepon(self, ctx, user: discord.Member = None):
        """
        Step on someone

        [Format: %stepon @user]
        """
        await self.ex.u_miscellaneous.interact_with_user(ctx, user, "stepped on", "stepon")

    @commands.command()
    @commands.cooldown(1, 60, BucketType.user)
    async def stab(self, ctx, user: discord.Member = None):
        """
        Stab someone

        [Format: %stab @user]
        """
        await self.ex.u_miscellaneous.interact_with_user(ctx, user, "stabbed", "stab")

    @commands.command()
    @commands.cooldown(1, 60, BucketType.user)
    async def choke(self, ctx, user: discord.Member = None):
        """
        Choke someone

        [Format: %choke @user]
        """
        await self.ex.u_miscellaneous.interact_with_user(ctx, user, "choked", "choke")

    @commands.command()
    @commands.cooldown(1, 60, BucketType.user)
    async def pullhair(self, ctx, user: discord.Member = None):
        """
        Pull the hair of someone

        [Format: %pullhair @user]
        """
        await self.ex.u_miscellaneous.interact_with_user(ctx, user, "is pulling the hair of", "pullhair")

    @commands.command()
    @commands.cooldown(1, 60, BucketType.user)
    async def cuddle(self, ctx, user: discord.Member = None):
        """
        Cuddle someone

        [Format: %cuddle @user]
        """
        await self.ex.u_miscellaneous.interact_with_user(ctx, user, "is cuddling with", "cuddle")

    @commands.command()
    @commands.cooldown(1, 60, BucketType.user)
    async def pat(self, ctx, user: discord.Member = None):
        """
        Pat someone

        [Format: %pat @user]
        """
        await self.ex.u_miscellaneous.interact_with_user(ctx, user, "patted", "pat")

    @commands.command()
    @commands.cooldown(1, 60, BucketType.user)
    async def punch(self, ctx, user: discord.Member = None):
        """
        Punch someone

        [Format: %punch @user]
        """
        await self.ex.u_miscellaneous.interact_with_user(ctx, user, "punched", "punch")

    @commands.command()
    @commands.cooldown(1, 60, BucketType.user)
    async def spit(self, ctx, user: discord.Member = None):
        """
        Spit on someone

        [Format: %spit @user]
        """
        await self.ex.u_miscellaneous.interact_with_user(ctx, user, "spit on", "spit")

    @commands.command()
    @commands.cooldown(1, 60, BucketType.user)
    async def lick(self, ctx, user: discord.Member = None):
        """
        Lick someone

        [Format: %lick @user]
        """
        await self.ex.u_miscellaneous.interact_with_user(ctx, user, "licked", "lick")

    @commands.command()
    @commands.cooldown(1, 60, BucketType.user)
    async def hug(self, ctx, user: discord.Member = None):
        """
        Hug someone

        [Format: %hug @user]
        """
        await self.ex.u_miscellaneous.interact_with_user(ctx, user, "hugged", "hug")

    @commands.command()
    @commands.cooldown(1, 60, BucketType.user)
    async def kiss(self, ctx, user: discord.Member = None):
        """
        Kiss someone

        [Format: %kiss @user]
        """
        await self.ex.u_miscellaneous.interact_with_user(ctx, user, "kissed", "kiss")

    @commands.command()
    @commands.cooldown(1, 60, BucketType.user)
    async def slap(self, ctx, user: discord.Member = None):
        """
        Slap someone

        [Format: %slap @user]
        """
        # There are two types of slap: in an embed with a url, or with text. 50% chance to get either.
        type_of_slap = randint(0, 1)
        if not type_of_slap:
            return await self.ex.u_miscellaneous.interact_with_user(ctx, user, "slapped", "slap")
        else:
            await self.ex.u_patreon.reset_patreon_cooldown(ctx)
            ctx_name = ctx.author.display_name
            user_name = user.display_name
            random_idol_stage_name = (await self.ex.u_group_members.get_random_idol()).stage_name
            harm_phrases = [
                f"Shame on you {user_name}!! You are not allowed to harm yourself.",
                f"Did you really think you could hurt yourself {user_name}?",
                f"{random_idol_stage_name} advises you not to hurt yourself {user_name}.",
                f"Uh.... I wouldn't do that if I were you {user_name}.",
                f"{random_idol_stage_name} slapped you instead {user_name}.",
            ]
            slap_phrases = [
                f"> {ctx_name} has slapped {user_name} right across the face.",
                f"> {ctx_name} slapped {user_name}'s forehead.",
                f"> {ctx_name} slapped {user_name} on the back of the head.",
                f"> {ctx_name} slapped {user_name} with the help of {random_idol_stage_name}.",
                f"> {ctx_name} slapped {user_name} with {random_idol_stage_name} holding them down.",
                f"> {ctx_name} and {random_idol_stage_name} brutally slap {user_name}.",
                f"> {user_name} was knocked unconscious from a powerful slap by {ctx_name}.",
                f"> {ctx_name} slapped {user_name} on the thigh.",
                f"> {ctx_name} gave {user_name} a high five to the face.",
            ]
            try:
                if user.id == ctx.author.id:
                    await ctx.send(f"> **{choice(harm_phrases)}**")
                    ctx.command.reset_cooldown(ctx)
                elif user == discord.Member:
                    await ctx.send("> **Please choose someone to slap.**")
                    ctx.command.reset_cooldown(ctx)
                else:
                    await ctx.send(f"**{choice(slap_phrases)}**")

            except Exception as e:
                log.console(e)
