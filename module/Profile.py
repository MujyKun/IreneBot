import discord
from discord.ext import commands
from Utility import get_level, shorten_balance, set_level, get_xp, get_balance, DBconn, c
from module import logger as log


class Profile(commands.Cog):
    def __init__(self, client):
        self.client = client
        client.add_listener(self.profile_level, 'on_message')

    async def profile_level(self, msg):
        try:
            xp_per_message = 10
            user_id = msg.author.id
            current_level = await get_level(user_id, "profile")
            current_xp = await get_level(user_id, "profilexp")
            xp_needed_for_level = await get_xp(current_level, "profile")

            if current_xp + xp_per_message < xp_needed_for_level:
                await set_level(user_id, current_xp + xp_per_message, "profilexp")
            else:
                await set_level(user_id, 1, "profilexp")
                await set_level(user_id, current_level+1, "profile")
        except Exception as e:
            log.console(e)

    @commands.command()
    async def profile(self, ctx, user: discord.Member = discord.Member):
        try:
            if user == discord.Member:
                user_id = ctx.author.id
                user = ctx.author
            else:
                user_id = user.id
            if user.bot:
                user_bot = "Yes"
            else:
                user_bot = "No"
            roles_list = user.roles
            count = 0
            roles = ""
            for role in roles_list:
                if count != 0 and count != (len(roles_list) - 1):
                    roles += f"{role.name},"
                if count == (len(roles_list)-1):
                    roles += role.name
                count += 1

            user_level = await get_level(user_id, "profile")
            shortened_money = await shorten_balance(str(await get_balance(user_id)))
            rob_beg_daily_level = f"{await get_level(user_id, 'rob')}/{await get_level(user_id, 'beg')}/{await get_level(user_id, 'daily')}"
            embed = discord.Embed(title=f"{user.name} ({user_id})", color=0x90ee90, url=f"{user.avatar_url}")
            embed.set_author(name="Irene", url='https://www.youtube.com/watch?v=dQw4w9WgXcQ',
                             icon_url='https://cdn.discordapp.com/emojis/693392862611767336.gif?v=1')
            embed.set_footer(text="Thanks for using Irene!", icon_url='https://cdn.discordapp.com/emojis/683932986818822174.gif?v=1')
            embed.set_thumbnail(url=user.avatar_url)
            embed.add_field(name="Profile Level", value=user_level, inline=True)
            embed.add_field(name="Money", value=f"${shortened_money}", inline=True)
            embed.add_field(name="Status", value=f"{user.status}", inline=True)
            embed.add_field(name="Rob/Beg/Daily Level", value=rob_beg_daily_level, inline=True)
            embed.add_field(name="Server Nickname", value=user.nick, inline=True)
            embed.add_field(name="Server Join Date", value=user.joined_at, inline=True)
            embed.add_field(name="Account Join Date", value=user.created_at, inline=True)
            embed.add_field(name="Bot", value=user_bot, inline=True)
            embed.add_field(name="Activity", value=user.activity, inline=True)
            embed.add_field(name="Roles", value=roles, inline=False)
            await ctx.send(embed=embed)

        except Exception as e:
            await ctx.send("> **There was an error. Please %report it**")
            log.console(e)