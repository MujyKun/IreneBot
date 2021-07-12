from discord.ext import commands
from IreneUtility.util import u_logger as log
from IreneUtility.Utility import Utility
import asyncio
import json
import datetime


# noinspection PyBroadException,PyPep8
class DataMod(commands.Cog):
    def __init__(self, t_ex):
        """

        :param t_ex: Utility object
        """
        self.ex: Utility = t_ex

    async def cog_check(self, ctx):
        """A local check for this cog. Checks if the user is a data mod."""
        return self.ex.check_if_mod(ctx, data_mod=True)

    @commands.command()
    async def addidol(self, ctx, *, idol_json):
        """Adds an idol using the syntax from https://irenebot.com/addidol.html

        [Format: %addidol (json)]

        VERY IMPORTANT:
        THIS COMMAND SHOULD ONLY BE USED IF A %CARD DOES NOT EXIST FOR THE IDOL.
        """
        try:
            # load string to json
            idol_json = json.loads(idol_json)

            # set empty strings to NoneType
            for key in idol_json:
                await asyncio.sleep(0)
                if not idol_json.get(key):
                    idol_json[key] = None

            # create variables for values used more than once or that need to be adjusted.
            birth_date = idol_json.get("Birth Date")
            if birth_date:
                birth_date = (datetime.datetime.strptime(birth_date, "%Y-%m-%d")).date()
            height = idol_json.get("Height")
            full_name = idol_json.get("Full Name")
            stage_name = idol_json.get("Stage Name")
            if height:
                height = int(height)

            # for security purposes, do not simplify the structure.
            await self.ex.conn.execute("INSERT INTO groupmembers.unregisteredmembers(fullname, stagename, "
                                       "formerfullname, formerstagename, birthdate, birthcountry, birthcity, gender, "
                                       "description, height, twitter, youtube, melon, instagram, vlive, spotify, "
                                       "fancafe, facebook, tiktok, zodiac, thumbnail, banner, bloodtype, tags,"
                                       " groupids, notes) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, "
                                       "$12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22, $23, $24, $25, "
                                       "$26)", full_name, stage_name, idol_json.get("Former Full Name"),
                                       idol_json.get("Former Stage Name"), birth_date, idol_json.get("Birth Country"),
                                       idol_json.get("Birth City"), idol_json.get("Gender"),
                                       idol_json.get("Description"), height, idol_json.get("Twitter"),
                                       idol_json.get("Youtube"), idol_json.get("Melon"), idol_json.get("Instagram"),
                                       idol_json.get("VLive"), idol_json.get("Spotify"), idol_json.get("Fancafe"),
                                       idol_json.get("Facebook"), idol_json.get("TikTok"), idol_json.get("Zodiac"),
                                       idol_json.get("Avatar"), idol_json.get("Banner"),
                                       idol_json.get("BloodType"), idol_json.get("Tags"),
                                       idol_json.get("Group IDs"), idol_json.get("Approver Notes"))

            # get the id of the data that was just added to db.
            query_id = self.ex.first_result(await self.ex.conn.fetchrow(
                "SELECT id FROM groupmembers.unregisteredmembers WHERE fullname = $1 AND stagename = $2 ORDER BY "
                "id DESC", full_name, stage_name))

            # get the channel to send idol information to.
            channel = self.ex.client.get_channel(self.ex.keys.add_idol_channel_id)
            # fetch if discord.py cache is not loaded.
            if not channel:
                channel = await self.ex.client.fetch_channel(self.ex.keys.add_idol_channel_id)
            title_description = f"""
==================
Query ID: {query_id} 
Requester: {ctx.author.display_name} ({ctx.author.id})
==================
"""
            # Add all the key values to the title description
            for key in idol_json:
                await asyncio.sleep(0)
                title_description += f"\n{key}: {idol_json.get(key)}"

            # send embed to approval/deny channel
            embed = await self.ex.create_embed(title="New Unregistered Idol", title_desc=title_description)
            msg = await channel.send(embed=embed)
            await msg.add_reaction(self.ex.keys.check_emoji)
            await msg.add_reaction(self.ex.keys.trash_emoji)
            msg = await self.ex.get_msg(ctx, "groupmembers", "add_idol_sent",
                                        [["name", ctx.author.display_name], ['query_id', query_id]])
            await ctx.send(msg)
        except Exception as e:
            log.console(e)
            server_prefix = await self.ex.get_server_prefix(ctx)
            msg = await self.ex.get_msg(ctx, "groupmembers", "add_error", [
                ["e", e], ["server_prefix", server_prefix], ["command_name", "addidol"]])
            await ctx.send(msg)

    @commands.command()
    async def addgroup(self, ctx, *, group_json):
        """Adds a group using the syntax from https://irenebot.com/addgroup.html

        [Format: %addgroup (json)]

        VERY IMPORTANT:
        THIS COMMAND SHOULD ONLY BE USED IF A %CARD DOES NOT EXIST FOR THE GROUP.
        """
        try:
            # load string to json
            group_json = json.loads(group_json)

            # set empty strings to NoneType
            for key in group_json:
                await asyncio.sleep(0)
                if not group_json.get(key):
                    group_json[key] = None

            # create variables for values used more than once or that need to be adjusted.
            debut_date = group_json.get("Debut Date")
            disband_date = group_json.get("Disband Date")
            if debut_date:
                debut_date = (datetime.datetime.strptime(debut_date, "%Y-%m-%d")).date()
            if disband_date:
                disband_date = (datetime.datetime.strptime(disband_date, "%Y-%m-%d")).date()

            group_name = group_json.get("Group Name")

            # for security purposes, do not simplify the structure as any json field can be entered.
            await self.ex.conn.execute("INSERT INTO groupmembers.unregisteredgroups(groupname, debutdate, disbanddate,"
                                       " description, twitter, youtube, melon, instagram, vlive, spotify, "
                                       "fancafe, facebook, tiktok, fandom, company, website, thumbnail, banner, "
                                       "gender, tags, notes) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12,"
                                       " $13, $14, $15, $16, $17, $18, $19, $20, $21)", group_name, debut_date,
                                       disband_date, group_json.get("Description"), group_json.get("Twitter"),
                                       group_json.get("Youtube"), group_json.get("Melon"), group_json.get("Instagram"),
                                       group_json.get("VLive"), group_json.get("Spotify"), group_json.get("Fancafe"),
                                       group_json.get("Facebook"), group_json.get("TikTok"), group_json.get("Fandom"),
                                       group_json.get("Company"), group_json.get("Website"), group_json.get("Avatar"),
                                       group_json.get("Banner"), group_json.get("Gender"), group_json.get("Tags"),
                                       group_json.get("Approver Notes"))

            # get the id of the data that was just added to db.
            query_id = self.ex.first_result(await self.ex.conn.fetchrow(
                "SELECT id FROM groupmembers.unregisteredgroups WHERE groupname = $1 ORDER BY id DESC", group_name))

            # get the channel to send idol information to.
            channel = self.ex.client.get_channel(self.ex.keys.add_group_channel_id)
            # fetch if discord.py cache is not loaded.
            if not channel:
                channel = await self.ex.client.fetch_channel(self.ex.keys.add_group_channel_id)
            title_description = f"""
==================
Query ID: {query_id} 
Requester: {ctx.author.display_name} ({ctx.author.id})
==================
"""
            # Add all the key values to the title description
            for key in group_json:
                await asyncio.sleep(0)
                title_description += f"\n{key}: {group_json.get(key)}"

            # send embed to approval/deny channel
            embed = await self.ex.create_embed(title="New Unregistered Group", title_desc=title_description)
            msg = await channel.send(embed=embed)
            await msg.add_reaction(self.ex.keys.check_emoji)
            await msg.add_reaction(self.ex.keys.trash_emoji)
            msg = await self.ex.get_msg(ctx, "groupmembers", "add_group_sent",
                                        [["name", ctx.author.display_name], ['query_id', query_id]])
            await ctx.send(msg)
        except Exception as e:
            log.console(e)
            server_prefix = await self.ex.get_server_prefix(ctx)
            msg = await self.ex.get_msg(ctx, "groupmembers", "add_error", [
                ["e", e], ["server_prefix", server_prefix], ["command_name", "addgroup"]])
            await ctx.send(msg)
