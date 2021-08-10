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

            args = (full_name, stage_name, idol_json.get("Former Full Name"),
                    idol_json.get("Former Stage Name"), birth_date, idol_json.get("Birth Country"),
                    idol_json.get("Birth City"), idol_json.get("Gender"),
                    idol_json.get("Description"), height, idol_json.get("Twitter"),
                    idol_json.get("Youtube"), idol_json.get("Melon"), idol_json.get("Instagram"),
                    idol_json.get("VLive"), idol_json.get("Spotify"), idol_json.get("Fancafe"),
                    idol_json.get("Facebook"), idol_json.get("TikTok"), idol_json.get("Zodiac"),
                    idol_json.get("Avatar"), idol_json.get("Banner"),
                    idol_json.get("BloodType"), idol_json.get("Tags"), idol_json.get("Difficulty"))

            group_ids = idol_json.get("Group IDs")
            if group_ids:
                group_ids = group_ids.split(',')

            idol_obj = await self.ex.u_group_members.add_new_idol(full_name, stage_name, group_ids, *args)

            aliases = idol_json.get("Aliases")
            if aliases:
                aliases = aliases.split(',')
                for alias in aliases:
                    await self.ex.u_group_members.set_global_alias(idol_obj, alias)

            embed = await self.ex.u_group_members.set_embed_card_info(idol_obj,
                                                                      server_id=await self.ex.get_server_id(ctx))
            await ctx.send(embed=embed)
            public_channel = self.ex.client.get_channel(self.ex.keys.datamod_log_channel_id) or await \
                self.ex.client.fetch_channel(self.ex.keys.datamod_log_channel_id)
            return await public_channel.send(embed=embed)

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

            args = (group_name, debut_date,
                    disband_date, group_json.get("Description"), group_json.get("Twitter"),
                    group_json.get("Youtube"), group_json.get("Melon"), group_json.get("Instagram"),
                    group_json.get("VLive"), group_json.get("Spotify"), group_json.get("Fancafe"),
                    group_json.get("Facebook"), group_json.get("TikTok"), group_json.get("Fandom"),
                    group_json.get("Company"), group_json.get("Website"), group_json.get("Avatar"),
                    group_json.get("Banner"), group_json.get("Gender"), group_json.get("Tags"))

            group = await self.ex.u_group_members.add_new_group(group_name, *args)

            aliases = group_json.get("Aliases")
            if aliases:
                aliases = aliases.split(',')
                for alias in aliases:
                    await self.ex.u_group_members.set_global_alias(group, alias)

            embed = await self.ex.u_group_members.set_embed_card_info(
                group, group=True, server_id=await self.ex.get_server_id(ctx))
            await ctx.send(embed=embed)

            public_channel = self.ex.client.get_channel(self.ex.keys.datamod_log_channel_id) or await \
                self.ex.client.fetch_channel(self.ex.keys.datamod_log_channel_id)
            return await public_channel.send(embed=embed)

        except Exception as e:
            log.console(e)
            server_prefix = await self.ex.get_server_prefix(ctx)
            msg = await self.ex.get_msg(ctx, "groupmembers", "add_error", [
                ["e", e], ["server_prefix", server_prefix], ["command_name", "addgroup"]])
            await ctx.send(msg)

    @commands.group()
    async def edit(self, ctx):
        """Edit an Idol or Group's information.

        [Format: %edit (idol/group) (group/idol id) (column) (content)]
        """
        ...

    @edit.command()
    async def idol(self, ctx, idol_id, column, *, content):
        """
        Edit data for an idol.

        [Format: %edit idol (idol id) (column) (content)]
        """
        await self.update_group_idol_info(ctx, idol_id, column, content, False)

    @edit.command()
    async def group(self, ctx, group_id, column, *, content):
        """
        Edit data for a group.

        [Format: %edit group (group id) (column) (content)]
        """
        await self.update_group_idol_info(ctx, group_id, column, content, True)

    async def update_group_idol_info(self, ctx, obj_id, column, content, group=False):
        """
        Method to reduce duplicated code for updating info.

        :param ctx: Context Object
        :param obj_id: Idol/Group ID
        :param column: Column Name
        :param content: Content to be set.
        :param group: Whether it is a group.
        """
        try:
            obj = await self.ex.u_group_members.update_info(obj_id, column, content, group=group)
            embed = await self.ex.u_group_members.set_embed_card_info(
                obj, server_id=await self.ex.get_server_id(ctx), group=group)

            await ctx.send(embed=embed)
            desc = f"{'Group' if group else 'Idol'} ID: {obj_id} had the `{column}` changed to \n{content}."
            public_embed = await self.ex.create_embed(f"Info Change by {ctx.author.display_name} ({ctx.author.id})",
                                                      title_desc=desc)
            public_channel = self.ex.client.get_channel(self.ex.keys.datamod_log_channel_id) or await \
                self.ex.client.fetch_channel(self.ex.keys.datamod_log_channel_id)
            return await public_channel.send(embed=public_embed)
        except NotImplementedError:
            msg = await self.ex.get_msg(ctx, "datamod", "column_not_found")
        except KeyError:
            msg = await self.ex.get_msg(ctx, "groupmembers", "invalid_id")
        except Exception as e:
            msg = await self.ex.get_msg(ctx, "general", "gen_error", ["e", e])
        return await ctx.send(msg)
