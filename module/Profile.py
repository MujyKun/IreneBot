import asyncio

import discord
import datetime
import pytz
from discord.ext import commands
from IreneUtility.util import u_logger as log
from IreneUtility.Utility import Utility


# noinspection PyBroadException,PyPep8
class Profile(commands.Cog):
    def __init__(self, ex):
        """

        :param ex: Utility object.
        """
        self.ex: Utility = ex

    @commands.command()
    async def avatar(self, ctx, user: discord.Member = None):
        try:
            if not user:
                user_id = ctx.author.id
                user = ctx.author
            else:
                user_id = user.id
            embed = await self.ex.create_embed(title=f"{user.display_name}'s Avatar   ({user_id})")
            embed.set_image(url=user.avatar_url)
            await ctx.send(embed=embed)
        except Exception as e:
            log.console(e)

    @commands.command()
    async def profile(self, ctx, user: discord.Member = None):
        try:
            if not user:
                user_id = ctx.author.id
                user = ctx.author
                roles_list = []
            else:
                user_id = user.id
                roles_list = user.roles
            if user.bot:
                user_bot = "Yes"
            else:
                user_bot = "No"

            irene_user = await self.ex.get_user(user_id)

            count = 0
            roles = ""
            for role in roles_list:
                await asyncio.sleep(0)
                if count and count != (len(roles_list) - 1):
                    roles += f"{role.name}, "
                if count == (len(roles_list)-1):
                    roles += role.name
                count += 1

            if len(roles) > 500:
                roles = f"{roles[0:498]}...."

            user_level = irene_user.profile_level
            shortened_money = await irene_user.get_shortened_balance()
            rob_beg_daily_level = f"{irene_user.rob_level}/{irene_user.beg_level}/{irene_user.daily_level}"

            user_scores = f"{await self.ex.u_guessinggame.get_user_score('easy', user_id)}/" \
                f"{await self.ex.u_guessinggame.get_user_score('medium', user_id)}/" \
                f"{await self.ex.u_guessinggame.get_user_score('hard', user_id)}"
            user_timezone = await self.ex.u_reminder.get_user_timezone(user_id)

            try:
                timezone_utc = datetime.datetime.now(pytz.timezone(user_timezone)).strftime('%Z, UTC%z')
            except:
                timezone_utc = None

            if await self.ex.u_patreon.check_if_patreon(user_id):
                embed = discord.Embed(title=f"{user.name} ({user_id})", color=0x90ee90, url=f"{user.avatar_url}",
                                      description=f"**{user.name} is supporting Irene on Patreon!**")
            else:
                embed = discord.Embed(title=f"{user.name} ({user_id})", color=0x90ee90, url=f"{user.avatar_url}")
            embed = await self.ex.set_embed_author_and_footer(embed, "Thanks for using Irene!")

            try:
                user_activity = user.activity.name
            except:
                user_activity = None

            embed.set_thumbnail(url=user.avatar_url)
            embed.add_field(name="Profile Level", value=user_level, inline=True)
            embed.add_field(name="Money", value=f"${shortened_money}", inline=True)

            if type(user) == discord.Member:
                embed.add_field(name="Status", value=f"{user.status}", inline=True)
                embed.add_field(name="Server Nickname", value=user.nick, inline=True)
                embed.add_field(name="Server Join Date", value=user.joined_at, inline=True)
                if roles:
                    embed.add_field(name="Roles", value=roles, inline=False)

            embed.add_field(name="Rob/Beg/Daily Level", value=rob_beg_daily_level, inline=True)
            embed.add_field(name="Account Join Date", value=user.created_at, inline=True)
            embed.add_field(name="Bot", value=user_bot, inline=True)

            if user_activity:
                embed.add_field(name="Activity", value=user_activity, inline=True)

            if user_timezone:
                embed.add_field(name="Timezone", value=f"{user_timezone} ({timezone_utc})", inline=True)

            embed.add_field(name="GuessingGame [Easy/Medium/Hard]", value=user_scores, inline=True)

            await ctx.send(embed=embed)

        except Exception as e:
            server_prefix = await self.ex.get_server_prefix(ctx)
            await ctx.send(f"> **There was an error. Please {server_prefix}report it**")
            log.console(e)

    async def increase_profile_level(self, msg):
        """Increase the profile level appropriately after every message."""
        # do not attempt to increase level if cache is not loaded
        # this is very dangerous as it can reset all the profile levels for the users sent here
        # if it takes too long for cache to load.
        if not self.ex.irene_cache_loaded:
            return

        user = await self.ex.get_user(msg.author.id)
        try:
            xp_per_message = 10
            current_level = user.profile_level
            current_xp = await user.get_profile_xp()
            xp_needed_for_level = await user.get_needed_for_level(current_level, "profile")

            if current_xp + xp_per_message < xp_needed_for_level:
                return await user.set_profile_xp(current_xp + xp_per_message)
            await user.set_profile_xp(1)
            await user.set_level(current_level + 1, "profile")
        except Exception as e:
            log.useless(f"{e} (Exception) - {user.id} failed to increase profile level",
                        method=self.increase_profile_level)
