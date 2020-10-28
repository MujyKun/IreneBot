import discord
from random import *
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from module import keys
from module import logger as log
from Utility import resources as ex
client = keys.client


class Interactions(commands.Cog):
    @commands.command()
    @commands.check(ex.check_interaction_enabled)
    @commands.cooldown(1, 60, BucketType.user)
    async def stepon(self, ctx, user: discord.Member = discord.Member):
        """Step on someone [Format: %stepon @user]"""
        await ex.interact_with_user(ctx, user, "stepped on", "stepon")

    @commands.command()
    @commands.check(ex.check_interaction_enabled)
    @commands.cooldown(1, 60, BucketType.user)
    async def stab(self, ctx, user: discord.Member = discord.Member):
        """Stab someone [Format: %stab @user]"""
        await ex.interact_with_user(ctx, user, "stabbed", "stab")

    @commands.command()
    @commands.check(ex.check_interaction_enabled)
    @commands.cooldown(1, 60, BucketType.user)
    async def choke(self, ctx, user: discord.Member = discord.Member):
        """Choke someone [Format: %choke @user]"""
        await ex.interact_with_user(ctx, user, "choked", "choke")

    @commands.command()
    @commands.check(ex.check_interaction_enabled)
    @commands.cooldown(1, 60, BucketType.user)
    async def pullhair(self, ctx, user: discord.Member = discord.Member):
        """Pull the hair of someone [Format: %pullhair @user]"""
        await ex.interact_with_user(ctx, user, "is pulling the hair of", "pullhair")

    @commands.command()
    @commands.check(ex.check_interaction_enabled)
    @commands.cooldown(1, 60, BucketType.user)
    async def cuddle(self, ctx, user: discord.Member = discord.Member):
        """Cuddle someone [Format: %cuddle @user]"""
        await ex.interact_with_user(ctx, user, "is cuddling with", "cuddle")

    @commands.command()
    @commands.check(ex.check_interaction_enabled)
    @commands.cooldown(1, 60, BucketType.user)
    async def pat(self, ctx, user: discord.Member = discord.Member):
        """Pat someone [Format: %pat @user]"""
        await ex.interact_with_user(ctx, user, "patted", "pat")

    @commands.command()
    @commands.check(ex.check_interaction_enabled)
    @commands.cooldown(1, 60, BucketType.user)
    async def punch(self, ctx, user: discord.Member = discord.Member):
        """Punch someone [Format: %punch @user]"""
        await ex.interact_with_user(ctx, user, "punched", "punch")

    @commands.command()
    @commands.check(ex.check_interaction_enabled)
    @commands.cooldown(1, 60, BucketType.user)
    async def spit(self, ctx, user: discord.Member = discord.Member):
        """Spit on someone [Format: %spit @user]"""
        await ex.interact_with_user(ctx, user, "spit on", "spit")

    @commands.command()
    @commands.check(ex.check_interaction_enabled)
    @commands.cooldown(1, 60, BucketType.user)
    async def lick(self, ctx, user: discord.Member = discord.Member):
        """Lick someone [Format: %lick @user]"""
        await ex.interact_with_user(ctx, user, "licked", "lick")

    @commands.command()
    @commands.check(ex.check_interaction_enabled)
    @commands.cooldown(1, 60, BucketType.user)
    async def hug(self, ctx, user: discord.Member = discord.Member):
        """Hug someone [Format: %hug @user]"""
        await ex.interact_with_user(ctx, user, "hugged", "hug")

    @commands.command()
    @commands.check(ex.check_interaction_enabled)
    @commands.cooldown(1, 60, BucketType.user)
    async def kiss(self, ctx, user: discord.Member = discord.Member):
        """Kiss someone [Format: %kiss @user]"""
        await ex.interact_with_user(ctx, user, "kissed", "kiss")

    @commands.command()
    @commands.check(ex.check_interaction_enabled)
    @commands.cooldown(1, 60, BucketType.user)
    async def slap(self, ctx, user: discord.Member = discord.Member):
        """Slap someone [Format: %slap @user]"""
        # There are two types of slap: in an embed with a url, or with text. 50% chance to get either.
        type_of_slap = randint(0, 1)
        if type_of_slap == 0:
            await ex.interact_with_user(ctx, user, "slapped", "slap")
        if type_of_slap == 1:
            await ex.reset_patreon_cooldown(ctx)
            ctx_name = ctx.author.display_name
            user_name = user.display_name
            random_idol_stage_name = (await ex.get_random_idol()).stage_name
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
