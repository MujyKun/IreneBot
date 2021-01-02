from Utility import resources as ex
import datetime
import discord
from module import logger as log
import asyncio
import json
import os
import random
from module.keys import reload_emoji, dead_emoji, owner_id, mods_list, check_emoji,\
    trash_emoji, next_emoji, translate_private_key, api_port


# noinspection PyBroadException,PyPep8
class GroupMembers:
    @staticmethod
    async def get_if_user_voted(user_id):
        time_stamp = ex.first_result(
            await ex.conn.fetchrow("SELECT votetimestamp FROM general.lastvoted WHERE userid = $1", user_id))
        if time_stamp:
            tz_info = time_stamp.tzinfo
            current_time = datetime.datetime.now(tz_info)
            check = current_time - time_stamp
            if check.seconds <= 43200:
                return True
        return False

    def check_idol_object(self, obj):
        return type(obj) == self.Idol

    @staticmethod
    async def send_vote_message(message):
        """Send the vote message to a user."""
        server_prefix = await ex.get_server_prefix_by_context(message)
        vote_message = f"> **To call more idol photos for the next 12 hours," \
                       f" please support Irene by voting or becoming a patron through the links at " \
                       f"`{server_prefix}vote` or `{server_prefix}patreon`!**"
        return await message.channel.send(vote_message)

    async def set_global_alias(self, obj, alias):
        """Set an idol/group alias for the bot."""
        obj.aliases.append(alias)
        is_group = int(not self.check_idol_object(obj))
        await ex.conn.execute("INSERT INTO groupmembers.aliases(objectid, alias, isgroup) VALUES($1, $2, $3)", obj.id,
                              alias, is_group)

    async def set_local_alias(self, obj, alias, server_id):
        """Set an idol/group alias for a server"""
        local_aliases = obj.local_aliases.get(server_id)
        if local_aliases:
            local_aliases.append(alias)
        else:
            obj.local_aliases[server_id] = [alias]
        is_group = int(not self.check_idol_object(obj))
        await ex.conn.execute(
            "INSERT INTO groupmembers.aliases(objectid, alias, isgroup, serverid) VALUES($1, $2, $3, $4)", obj.id,
            alias, is_group, server_id)

    async def remove_global_alias(self, obj, alias):
        """Remove a global idol/group alias """
        obj.aliases.remove(alias)
        is_group = int(not self.check_idol_object(obj))
        await ex.conn.execute(
            "DELETE FROM groupmembers.aliases WHERE alias = $1 AND isgroup = $2 AND objectid = $3 AND serverid IS NULL",
            alias, is_group, obj.id)

    async def remove_local_alias(self, obj, alias, server_id):
        """Remove a server idol/group alias"""
        is_group = int(not self.check_idol_object(obj))
        local_aliases = obj.local_aliases.get(server_id)
        if local_aliases:
            local_aliases.remove(alias)
        await ex.conn.execute(
            "DELETE FROM groupmembers.aliases WHERE alias = $1 AND isgroup = $2 AND serverid = $3 AND objectid = $4",
            alias, is_group, server_id, obj.id)

    @staticmethod
    async def get_member(idol_id):
        """Get a member by the idol id."""
        try:
            idol_id = int(idol_id)
        except:
            # purposefully create an error if an idol id was not passed in. This is useful to not check for it
            # in other commands.
            return
        for idol in ex.cache.idols:
            if idol.id == idol_id:
                return idol

    @staticmethod
    async def get_group(group_id):
        """Get a group by the group id."""
        try:
            group_id = int(group_id)
        except:
            # purposefully create an error if a group id was not passed in. This is useful to not check for it
            # in other commands.
            return
        for group in ex.cache.groups:
            if group.id == group_id:
                return group

    async def set_embed_card_info(self, obj, group=False, server_id=None):
        """Sets General Information about a Group or Idol."""
        description = ""
        if obj.description:
            description += f"{obj.description}\n\n"
        if obj.id:
            description += f"ID: {obj.id}\n"
        if obj.gender:
            description += f"Gender: {obj.gender}\n"
        if group:
            title = f"{obj.name} [{obj.id}]\n"
            if obj.name:
                description += f"Name: {obj.name}\n"
            if obj.debut_date:
                description += f"Debut Date: {obj.debut_date}\n"
            if obj.disband_date:
                description += f"Disband Date: {obj.disband_date}\n"
            if obj.fandom:
                description += f"Fandom Name: {obj.fandom}\n"
            if obj.company:
                description += f"Company: {obj.company}\n"
            if obj.website:
                description += f"[Official Website]({obj.website})\n"
        else:
            title = f"{obj.full_name} ({obj.stage_name}) [{obj.id}]\n"
            if obj.full_name:
                description += f"Full Name: {obj.full_name}\n"
            if obj.stage_name:
                description += f"Stage Name: {obj.stage_name}\n"
            if obj.former_full_name:
                description += f"Former Full Name: {obj.former_full_name}\n"
            if obj.former_stage_name:
                description += f"Former Stage Name: {obj.former_stage_name}\n"
            if obj.birth_date:
                description += f"Birth Date: {obj.birth_date}\n"
            if obj.birth_country:
                description += f"Birth Country: {obj.birth_country}\n"
            if obj.birth_city:
                description += f"Birth City: {obj.birth_city}\n"
            if obj.height:
                description += f"Height: {obj.height}cm\n"
            if obj.zodiac:
                description += f"Zodiac Sign: {obj.zodiac}\n"
            if obj.blood_type:
                description += f"Blood Type: {obj.blood_type}\n"
            if obj.called:
                description += f"Called: {obj.called} times\n"
        if obj.twitter:
            description += f"[Twitter](https://twitter.com/{obj.twitter})\n"
        if obj.youtube:
            description += f"[Youtube](https://www.youtube.com/channel/{obj.youtube})\n"
        if obj.melon:
            description += f"[Melon](https://www.melon.com/artist/song.htm?artistId={obj.melon})\n"
        if obj.instagram:
            description += f"[Instagram](https://instagram.com/{obj.instagram})\n"
        if obj.vlive:
            description += f"[V Live](https://channels.vlive.tv/{obj.vlive})\n"
        if obj.spotify:
            description += f"[Spotify](https://open.spotify.com/artist/{obj.spotify})\n"
        if obj.fancafe:
            description += f"[FanCafe](https://m.cafe.daum.net/{obj.fancafe})\n"
        if obj.facebook:
            description += f"[Facebook](https://www.facebook.com/{obj.facebook})\n"
        if obj.tiktok:
            description += f"[TikTok](https://www.tiktok.com/{obj.tiktok})\n"
        if obj.photo_count:
            description += f"Photo Count: {obj.photo_count}\n"
        embed = await ex.create_embed(title=title, color=ex.get_random_color(), title_desc=description)
        if obj.tags:
            embed.add_field(name="Tags", value=', '.join(obj.tags), inline=False)
        if obj.aliases:
            embed.add_field(name="Aliases", value=', '.join(obj.aliases), inline=False)
        if obj.local_aliases.get(server_id):
            embed.add_field(name="Server Aliases", value=', '.join(obj.local_aliases.get(server_id)), inline=False)
        if group:
            if obj.members:
                try:
                    value = f"{' | '.join([(await self.get_member(idol_id)).full_name for idol_id in obj.members])}\n"
                except:
                    value = "This group has an Idol that doesn't exist. Please report it.\n"
                embed.add_field(name="Members", value=value, inline=False)

        else:
            if obj.groups:
                value = await self.get_group_names_as_string(obj)
                embed.add_field(name="Groups", value=value)
        if obj.thumbnail:
            embed.set_thumbnail(url=obj.thumbnail)
        if obj.banner:
            embed.set_image(url=obj.banner)
        return embed

    async def get_group_names_as_string(self, idol):
        """Get the group names split by a | ."""
        # note that this used to be simplified to one line, but in the case there are groups that do not exist,
        # a proper check and deletion of fake groups are required
        group_names = []
        for group_id in idol.groups:
            group = await self.get_group(group_id)
            if group:
                group_names.append(group.name)
            else:
                # make sure the cache exists first before deleting.
                if ex.cache.groups:
                    # delete the group connections if it doesn't exist.
                    await ex.conn.execute("DELETE FROM groupmembers.idoltogroup WHERE groupid = $1", group_id)
        return f"{' | '.join(group_names)}\n"

    @staticmethod
    async def check_channel_sending_photos(channel_id):
        """Checks a text channel ID to see if it is restricted from having idol photos sent."""
        channel = ex.cache.restricted_channels.get(channel_id)
        if channel:
            if not channel[1]:
                return False  # returns False if they are restricted.
        return True

    @staticmethod
    async def delete_restricted_channel_from_cache(channel_id, send_all):
        """Deletes restricted channel from cache."""
        r_channel = ex.cache.restricted_channels.get(channel_id)
        if r_channel:
            if r_channel[1] == send_all:
                ex.cache.restricted_channels.pop(channel_id)

    @staticmethod
    async def check_server_sending_photos(server_id):
        """Checks a server to see if it has a specific channel to send idol photos to"""
        for channel in ex.cache.restricted_channels:
            channel_info = ex.cache.restricted_channels.get(channel)
            if channel_info[0] == server_id and channel_info[1] == 1:
                return True  # returns True if they are supposed to send it to a specific channel.

    @staticmethod
    async def get_channel_sending_photos(server_id):
        """Returns a text channel from a server that requires idol photos to be sent to a specific text channel."""
        for channel_id in ex.cache.restricted_channels:
            channel_info = ex.cache.restricted_channels.get(channel_id)
            if channel_info[0] == server_id and channel_info[1] == 1:
                return ex.client.get_channel(channel_id)

    @staticmethod
    def log_idol_command(message):
        """Log an idol photo that was called."""
        log.console(f"IDOL LOG: ChannelID = {message.channel.id} - {message.author} "
                    f"({message.author.id})|| {message.clean_content} ")

    @staticmethod
    async def get_all_images_count():
        """Get the amount of images the bot has."""
        return ex.first_result(await ex.conn.fetchrow("SELECT COUNT(*) FROM groupmembers.imagelinks"))

    @staticmethod
    async def get_db_idol_called(member_id):
        """Get the amount of times an idol has been called from the database."""
        return ex.first_result(
            await ex.conn.fetchrow("SELECT Count FROM groupmembers.Count WHERE MemberID = $1", member_id))

    async def get_random_idol(self):
        """Get a random idol with at least 1 photo."""
        idol = random.choice(ex.cache.idols)
        if not idol.photo_count:
            idol = await self.get_random_idol()
        return idol

    @staticmethod
    async def get_db_all_members():
        """Get all idols from the database."""
        return await ex.conn.fetch("""SELECT id, fullname, stagename, formerfullname, formerstagename, birthdate,
            birthcountry, birthcity, gender, description, height, twitter, youtube, melon, instagram, vlive, spotify,
            fancafe, facebook, tiktok, zodiac, thumbnail, banner, bloodtype, tags, difficulty
             FROM groupmembers.Member ORDER BY id""")

    @staticmethod
    async def get_all_groups():
        """Get all groups."""
        return await ex.conn.fetch("""SELECT groupid, groupname, debutdate, disbanddate, description, twitter, youtube,
                                         melon, instagram, vlive, spotify, fancafe, facebook, tiktok, fandom, company,
                                          website, thumbnail, banner, gender, tags FROM groupmembers.groups ORDER BY groupname""")

    @staticmethod
    async def get_db_members_in_group(group_name=None, group_id=None):
        """Get the members in a specific group from database."""
        if group_id is None:
            group_id = ex.first_result(
                await ex.conn.fetchrow(f"SELECT groupid FROM groupmembers.groups WHERE groupname = $1", group_name))
        members = await ex.conn.fetch("SELECT idolid FROM groupmembers.idoltogroup WHERE groupid = $1", group_id)
        return [member[0] for member in members]

    @staticmethod
    async def get_db_aliases(object_id, group=False):
        """Get the aliases of an idol or group from the database."""
        aliases = await ex.conn.fetch(
            "SELECT alias, serverid FROM groupmembers.aliases WHERE objectid = $1 AND isgroup = $2", object_id,
            int(group))
        global_aliases = []
        local_aliases = {}
        for alias, server_id in aliases:
            if server_id:
                server_list = local_aliases.get(server_id)
                if server_list:
                    server_list.append(alias)
                else:
                    local_aliases[server_id] = [alias]
            else:
                global_aliases.append(alias)
        return global_aliases, local_aliases

    @staticmethod
    async def get_db_groups_from_member(member_id):
        """Return all the group ids an idol is in from the database."""
        groups = await ex.conn.fetch("SELECT groupid FROM groupmembers.idoltogroup WHERE idolid = $1", member_id)
        return [group[0] for group in groups]

    @staticmethod
    async def add_idol_to_group(member_id: int, group_id: int):
        return await ex.conn.execute("INSERT INTO groupmembers.idoltogroup(idolid, groupid) VALUES($1, $2)",
                                     member_id, group_id)

    @staticmethod
    async def remove_idol_from_group(member_id: int, group_id: int):
        return await ex.conn.execute("DELETE FROM groupmembers.idoltogroup WHERE idolid = $1 AND groupid = $2",
                                     member_id, group_id)

    async def send_names(self, ctx, mode, user_page_number=1, group_ids=None):
        """Send the names of all idols in an embed with many pages."""
        server_prefix = await ex.get_server_prefix_by_context(ctx)

        async def check_mode(embed_temp):
            """Check if it is grabbing their full names or stage names."""
            if mode == "fullname":
                embed_temp = await ex.set_embed_author_and_footer(embed_temp,
                                                                  f"Type {server_prefix}members for Stage Names.")
            else:
                embed_temp = await ex.set_embed_author_and_footer(embed_temp,
                                                                  f"Type {server_prefix}fullnames for Full Names.")
            return embed_temp

        is_mod = ex.check_if_mod(ctx)
        embed_lists = []
        page_number = 1
        embed = discord.Embed(title=f"Idol List Page {page_number}", color=0xffb6c1)
        counter = 1
        for group in ex.cache.groups:
            names = []
            if (group.name != "NULL" and group.photo_count != 0) or is_mod:
                if not group_ids or group.id in group_ids:
                    for group_member in group.members:
                        member = await self.get_member(group_member)
                        if member:
                            if member.photo_count or is_mod:
                                if mode == "fullname":
                                    member_name = member.full_name
                                else:
                                    member_name = member.stage_name
                                if is_mod:
                                    names.append(f"{member_name} ({member.id}) | ")
                                else:
                                    names.append(f"{member_name} | ")
                    final_names = "".join(names)
                    if not final_names:
                        final_names = "None"
                    if is_mod:
                        embed.insert_field_at(counter, name=f"{group.name} ({group.id})", value=final_names,
                                              inline=False)
                    else:
                        embed.insert_field_at(counter, name=f"{group.name}", value=final_names, inline=False)
                    if counter == 10:
                        page_number += 1
                        await check_mode(embed)
                        embed_lists.append(embed)
                        embed = discord.Embed(title=f"Idol List Page {page_number}", color=0xffb6c1)
                        counter = 0
                    counter += 1
        # if counter did not reach 10, current embed needs to be saved.
        await check_mode(embed)
        embed_lists.append(embed)
        if user_page_number > len(embed_lists) or user_page_number < 1:
            user_page_number = 1
        msg = await ctx.send(embed=embed_lists[user_page_number - 1])
        # if embeds list only contains 1 embed, do not paginate.
        if len(embed_lists) > 1:
            await ex.check_left_or_right_reaction_embed(msg, embed_lists, user_page_number - 1)

    async def set_embed_with_aliases(self, name, server_id=None):
        """Create an embed with the aliases of the names of groups or idols sent in"""
        members = await self.get_idol_where_member_matches_name(name, mode=1, server_id=server_id)
        groups, group_names = await self.get_group_where_group_matches_name(name, mode=1, server_id=server_id)
        embed_list = []
        count = 0
        page_number = 1
        embed = discord.Embed(title=f"{name} Aliases Page {page_number}", description="", color=ex.get_random_color())
        for member in members:
            aliases = ', '.join(member.aliases)
            local_aliases = member.local_aliases.get(server_id)
            if local_aliases:
                aliases += ", ".join(local_aliases)
            embed.add_field(name=f"{member.full_name} ({member.stage_name}) [Idol {member.id}]",
                            value=aliases or "None", inline=True)
            count += 1
            if count == 24:
                count = 0
                page_number += 1
                embed_list.append(embed)
                embed = discord.Embed(title=f"{name} Aliases Page {page_number}", description="",
                                      color=ex.get_random_color())
        for group in groups:
            aliases = ', '.join(group.aliases)
            embed.add_field(name=f"{group.name} [Group {group.id}]", value=aliases or "None", inline=True)
            count += 1
            if count == 24:
                count = 0
                page_number += 1
                embed_list.append(embed)
                embed = discord.Embed(title=f"{name} Aliases Page {page_number}", description="",
                                      color=ex.get_random_color())
        if count:
            embed_list.append(embed)
        return embed_list

    @staticmethod
    async def set_embed_with_all_aliases(mode, server_id=None):
        """Send the names of all aliases in an embed with many pages."""

        def create_embed():
            return discord.Embed(title=f"{mode} Global/Local Aliases Page {page_number}", color=ex.get_random_color())

        if mode == "Group":
            all_info = ex.cache.groups
            is_group = True
        else:
            all_info = ex.cache.idols
            is_group = False
        embed_list = []
        count = 0
        page_number = 1
        embed = create_embed()
        for info in all_info:
            aliases = ",".join(info.aliases)
            local_aliases = info.local_aliases.get(server_id)
            if local_aliases:
                aliases += ", ".join(local_aliases)
            if aliases:
                if not is_group:
                    embed.add_field(name=f"{info.full_name} ({info.stage_name}) [{info.id}]", value=aliases,
                                    inline=True)
                else:
                    embed.add_field(name=f"{info.name} [{info.id}]", value=aliases, inline=True)
                count += 1
            if count == 10:
                count = 0
                embed_list.append(embed)
                page_number += 1
                embed = create_embed()
        if count != 0:
            embed_list.append(embed)
        return embed_list

    async def check_idol_post_reactions(self, message, user_msg, idol, link, guessing_game=False):
        """Check the reactions on an idol post or guessing game."""
        try:
            if message is not None:
                reload_image_emoji = reload_emoji
                dead_link_emoji = dead_emoji
                if not guessing_game:
                    await message.add_reaction(reload_image_emoji)
                await message.add_reaction(dead_link_emoji)
                message = await message.channel.fetch_message(message.id)

                def image_check(user_reaction, reaction_user):
                    """check the user that reacted to it and which emoji it was."""
                    user_check = (reaction_user == user_msg.author) or (
                                reaction_user.id == owner_id) or reaction_user.id in mods_list
                    dead_link_check = str(user_reaction.emoji) == dead_link_emoji
                    reload_image_check = str(user_reaction.emoji) == reload_image_emoji
                    guessing_game_check = user_check and dead_link_check and user_reaction.message.id == message.id
                    idol_post_check = user_check and (
                                dead_link_check or reload_image_check) and user_reaction.message.id == message.id
                    if guessing_game:
                        return guessing_game_check
                    return idol_post_check

                async def reload_image():
                    """Wait for a user to react, and reload the image if it's the reload emoji."""
                    try:
                        reaction, user = await ex.client.wait_for('reaction_add', check=image_check, timeout=60)
                        if str(reaction) == reload_image_emoji:
                            channel = message.channel
                            await message.delete()
                            # message1 = await channel.send(embed=embed)
                            message1 = await channel.send(link)
                            await self.check_idol_post_reactions(message1, user_msg, idol, link)
                        elif str(reaction) == dead_link_emoji:
                            if await ex.u_patreon.check_if_patreon(user.id):
                                await message.delete()
                            else:
                                await message.clear_reactions()
                                server_prefix = await ex.get_server_prefix_by_context(message)
                                warning_msg = f"Report images as dead links (2nd reaction) ONLY if the image does not load or it's not a photo of the idol.\nYou can have this message removed by becoming a {server_prefix}patreon"
                                if guessing_game:
                                    warning_msg = f"This image has been reported as a dead image, not a photo of the idol, or a photo with several idols.\nYou can have this message removed by becoming a {server_prefix}patreon"
                                await message.edit(content=warning_msg, suppress=True, delete_after=45)
                            await self.get_dead_links()
                            try:
                                channel = ex.cache.dead_image_channel
                                if channel is not None:
                                    await self.send_dead_image(channel, link, user, idol, int(guessing_game))
                            except:
                                pass
                    except asyncio.TimeoutError:
                        await message.clear_reactions()
                    except Exception as err:
                        log.console(err)

                await reload_image()
        except:
            pass

    @staticmethod
    async def get_dead_links():
        return await ex.conn.fetch("SELECT deadlink, messageid, idolid FROM groupmembers.deadlinkfromuser")

    @staticmethod
    async def delete_dead_link(link, idol_id):
        return await ex.conn.execute("DELETE FROM groupmembers.deadlinkfromuser WHERE deadlink = $1 AND idolid = $2",
                                     link, idol_id)

    @staticmethod
    async def set_forbidden_link(link, idol_id):
        return await ex.conn.execute("INSERT INTO groupmembers.forbiddenlinks(link, idolid) VALUES($1, $2)", link,
                                     idol_id)

    async def send_dead_image(self, channel, link, user, idol, is_guessing_game):
        try:
            game = ""
            if is_guessing_game:
                game = "-- Guessing Game"
            special_message = f"""**Dead Image For {idol.full_name} ({idol.stage_name}) ({idol.id}) {game}
    Sent in by {user.name}#{user.discriminator} ({user.id}).**"""
            msg, api_url = await self.idol_post(channel, idol, photo_link=link, special_message=special_message)
            ex.cache.dead_image_cache[msg.id] = [str(link), user.id, idol.id, is_guessing_game]
            await ex.conn.execute(
                "INSERT INTO groupmembers.deadlinkfromuser(deadlink, userid, messageid, idolid, guessinggame) VALUES($1, $2, $3, $4, $5)",
                str(link), user.id, msg.id, idol.id, is_guessing_game)
            await msg.add_reaction(check_emoji)
            await msg.add_reaction(trash_emoji)
            await msg.add_reaction(next_emoji)
        except Exception as e:
            log.console(f"Send Dead Image - {e}")

    async def get_idol_where_member_matches_name(self, name, mode=0, server_id=None):
        """Get idol object if the name matches an idol"""
        idol_list = []
        name = name.lower()
        for idol in ex.cache.idols:
            local_aliases = None
            if server_id:
                local_aliases = idol.local_aliases.get(server_id)
            if not mode:
                if idol.full_name and idol.stage_name:
                    if name == idol.full_name.lower() or name == idol.stage_name.lower():
                        idol_list.append(idol)
            else:
                if idol.full_name and idol.stage_name:
                    if idol.stage_name.lower() in name or idol.full_name.lower() in name:
                        idol_list.append(idol)
            for alias in idol.aliases:
                if not mode:
                    if alias == name:
                        idol_list.append(idol)
                else:
                    if alias in name:
                        idol_list.append(idol)
            if local_aliases:
                for alias in local_aliases:
                    if await self.check_to_add_alias_to_list(alias, name, mode):
                        idol_list.append(idol)

        # remove any duplicates
        idols = list(dict.fromkeys(idol_list))
        return idols

    @staticmethod
    async def check_to_add_alias_to_list(alias, name, mode=0):
        """Check whether to add an alias to a list. Compares a name with an existing alias."""
        if not mode:
            if alias == name:
                return True
        else:
            if alias in name:
                return True
        return False

    async def get_group_where_group_matches_name(self, name, mode=0, server_id=None):
        """Get group ids for a specific name."""
        group_list = []
        name = name.lower()
        for group in ex.cache.groups:
            try:
                aliases = group.aliases
                local_aliases = None
                if server_id:
                    local_aliases = group.local_aliases.get(server_id)
                if not mode:
                    if group.name:
                        if name == group.name.lower():
                            group_list.append(group)
                else:
                    if group.name:
                        if group.name.lower() in name:
                            group_list.append(group)
                            name = (name.lower()).replace(group.name, "")
                for alias in aliases:
                    if await self.check_to_add_alias_to_list(alias, name, mode):
                        group_list.append(group)
                        if mode:
                            name = (name.lower()).replace(alias, "")
                if local_aliases:
                    for alias in local_aliases:
                        if await self.check_to_add_alias_to_list(alias, name, mode):
                            group_list.append(group)
                            if mode:
                                name = (name.lower()).replace(alias, "")

            except Exception as e:
                log.console(e)
        # remove any duplicates
        group_list = list(dict.fromkeys(group_list))
        # print(id_list)
        if not mode:
            return group_list
        else:
            return group_list, name

    async def process_names(self, ctx, page_number_or_group, mode):
        """Structures the input for idol names commands and sends information to transfer the names to the channels."""
        if type(page_number_or_group) == int:
            await self.send_names(ctx, mode, page_number_or_group)
        elif type(page_number_or_group) == str:
            server_id = await ex.get_server_id(ctx)
            groups, name = await self.get_group_where_group_matches_name(page_number_or_group, mode=1,
                                                                         server_id=server_id)
            await self.send_names(ctx, mode, group_ids=[group.id for group in groups])

    async def check_group_and_idol(self, message_content, server_id=None):
        """returns specific idols being called from a reference to a group ex: redvelvet irene"""
        groups, new_message = await self.get_group_where_group_matches_name(message_content, mode=1,
                                                                            server_id=server_id)
        member_list = []
        members = await self.get_idol_where_member_matches_name(new_message, mode=1, server_id=server_id)
        for group in groups:
            for member in members:
                if member.id in group.members:
                    member_list.append(member)
        return member_list or None

    @staticmethod
    async def update_member_count(idol):
        """Update the amount of times an idol has been called."""
        if not idol.called:
            idol.called = 1
            await ex.conn.execute("INSERT INTO groupmembers.count VALUES($1, $2)", idol.id, 1)
        else:
            idol.called += 1
            await ex.conn.execute("UPDATE groupmembers.Count SET Count = $1 WHERE MemberID = $2", idol.called,
                                    idol.id)

    @staticmethod
    async def set_as_group_photo(link):
        await ex.conn.execute("UPDATE groupmembers.imagelinks SET groupphoto = $1 WHERE link = $2", 1, str(link))

    @staticmethod
    async def get_google_drive_link(api_url):
        """Get the google drive link based on the api's image url."""
        return ex.first_result(
            await ex.conn.fetchrow("SELECT driveurl FROM groupmembers.apiurl WHERE apiurl = $1", str(api_url)))

    async def get_image_msg(self, idol, group_id, channel, photo_link, user_id=None, guild_id=None, api_url=None,
                            special_message=None, guessing_game=False, scores=None):
        """Get the image link from the API and return the message containing the image."""

        async def post_msg(m_file=None, m_embed=None, repeated=0):
            """Send the message to the channel and return it."""
            message = None
            try:
                if not special_message:
                    message = await channel.send(embed=m_embed, file=m_file)
                else:
                    message = await channel.send(special_message, embed=m_embed, file=m_file)
            except:
                # cannot access API or API Link -> attempt to post it 5 times.
                # this happens because the image link may not be properly registered.
                if repeated < 5:
                    if not message:
                        await asyncio.sleep(0.5)
                        message = await post_msg(m_file=m_file, m_embed=m_embed, repeated=repeated + 1)
            return message

        file = None
        if not api_url:
            try:
                find_post = True

                data = {
                    'p_key':  translate_private_key,
                    'no_group_photos': int(guessing_game)
                }
                end_point = f"http://127.0.0.1:{ api_port}/photos/{idol.id}"
                if ex.test_bot:
                    end_point = f"https://api.irenebot.com/photos/{idol.id}"
                while find_post:  # guarantee we get a post sent to the user.
                    async with ex.session.post(end_point, data=data) as r:
                        ex.cache.bot_api_idol_calls += 1
                        if r.status == 200 or r.status == 301:
                            api_url = r.url
                            find_post = False
                        elif r.status == 415:
                            # video
                            if guessing_game:
                                # do not allow videos in the guessing game.
                                return self.get_image_msg(idol, group_id, channel, photo_link, user_id, guild_id,
                                                          api_url, special_message, guessing_game, scores)
                            url_data = json.loads(await r.text())
                            api_url = url_data.get('final_image_link')
                            file_location = url_data.get('location')
                            file_name = url_data.get('file_name')
                            file_size = os.path.getsize(file_location)
                            if file_size < 8388608:  # 8 MB
                                file = discord.File(file_location, file_name)
                                find_post = False
                        elif r.status == 403:
                            log.console("API Key Missing or Invalid Key.")
                            find_post = False
                        elif r.status == 404 or r.status == 400:
                            # No photos were found.
                            log.console(f"No photos were found for this idol ({idol.id}).")
                            msg = await channel.send(f"**No photos were found for this idol ({idol.id}).**")
                            return msg, None
                        elif r.status == 502:
                            msg = await channel.send("API is currently being overloaded with requests.")
                            log.console("API is currently being overloaded with requests or is down.")
                            return msg, None
                        else:
                            # error unaccounted for.
                            log.console(f"{r.status} - Status Code from API.")
            except Exception as e:
                log.console(e)

        if guessing_game:
            # sleep for 2 seconds because of bad loading times on discord
            await asyncio.sleep(2)
        try:
            if file:
                # send the video and return the message with the api url.
                msg = await post_msg(m_file=file)
                if not msg:
                    raise Exception
                return msg, api_url

            # an image url should exist at this point, and should not equal None.
            embed = await self.get_idol_post_embed(group_id, idol, str(api_url), user_id=user_id,
                                                   guild_id=channel.guild.id, guessing_game=guessing_game,
                                                   scores=scores)
            embed.set_image(url=api_url)
            msg = await post_msg(m_embed=embed)
            if not msg:
                raise Exception

        except Exception as e:
            ex.api_issues += 1
            if ex.api_issues >= 50:
                await ex.kill_api()
                ex.api_issues = 0
            await channel.send(
                f"> An API issue has occurred. If this is constantly occurring, please join our support server.")
            log.console(
                f" {e} - An API issue has occurred. If this is constantly occurring, please join our support server.")
            return None, None
        return msg, api_url

    async def get_idol_post_embed(self, group_id, idol, photo_link, user_id=None, guild_id=None, guessing_game=False,
                                  scores=None):
        """The embed for an idol post."""
        if not guessing_game:
            if not group_id:
                embed = discord.Embed(title=f"{idol.full_name} ({idol.stage_name})", color=ex.get_random_color(),
                                      url=photo_link)
            else:
                group = await self.get_group(group_id)
                embed = discord.Embed(title=f"{group.name} ({idol.stage_name})",
                                      color=ex.get_random_color(), url=photo_link)
            patron_msg = f"Please consider becoming a {await ex.get_server_prefix(guild_id)}patreon."

            # when user_id is None, the post goes to the dead images channel.
            if user_id:
                if not await ex.u_patreon.check_if_patreon(user_id):
                    embed.set_footer(text=patron_msg)
        else:
            current_scores = ""
            if scores:
                for user_id in scores:
                    current_scores += f"<@{user_id}> -> {scores.get(user_id)}\n"
            embed = discord.Embed(description=current_scores,
                                  color=ex.get_random_color(), url=photo_link)
        return embed

    async def idol_post(self, channel, idol, photo_link=None, group_id=None, special_message=None, user_id=None,
                        guessing_game=False, scores=None):
        """The main process for posting an idol's photo."""
        try:
            try:
                msg, api_url = await self.get_image_msg(idol, group_id, channel, photo_link, user_id=user_id,
                                                        guild_id=channel.guild.id, api_url=photo_link,
                                                        special_message=special_message, guessing_game=guessing_game,
                                                        scores=scores)
                if not msg and not api_url:
                    ex.api_issues += 1
                await self.update_member_count(idol)
            except:
                if guessing_game:
                    return self.idol_post(channel, idol, photo_link, group_id, special_message, user_id, guessing_game,
                                          scores)
                await channel.send(
                    f"> An error has occurred. If you are in DMs, It is not possible to receive Idol Photos.")
                return None, None
            return msg, api_url
        except Exception as e:
            log.console(e)
            return None, None

    class Idol:
        def __init__(self, **kwargs):
            self.id = kwargs.get('id')
            self.full_name = kwargs.get('fullname')
            self.stage_name = kwargs.get('stagename')
            self.former_full_name = kwargs.get('formerfullname')
            self.former_stage_name = kwargs.get('formerstagename')
            self.birth_date = kwargs.get('birthdate')
            self.birth_country = kwargs.get('birthcountry')
            self.birth_city = kwargs.get('birthcity')
            self.gender = kwargs.get('gender')
            self.description = kwargs.get('description')
            self.height = kwargs.get('height')
            self.twitter = kwargs.get('twitter')
            self.youtube = kwargs.get('youtube')
            self.melon = kwargs.get('melon')
            self.instagram = kwargs.get('instagram')
            self.vlive = kwargs.get('vlive')
            self.spotify = kwargs.get('spotify')
            self.fancafe = kwargs.get('fancafe')
            self.facebook = kwargs.get('facebook')
            self.tiktok = kwargs.get('tiktok')
            self.aliases = []
            self.local_aliases = {}  # server_id: [aliases]
            self.groups = []
            self.zodiac = kwargs.get('zodiac')
            self.thumbnail = kwargs.get('thumbnail')
            self.banner = kwargs.get('banner')
            self.blood_type = kwargs.get('bloodtype')
            self.photo_count = 0
            # amount of times the idol has been called.
            self.called = 0
            self.tags = kwargs.get('tags')
            self.difficulty = kwargs.get('difficulty')
            if self.tags:
                self.tags = self.tags.split(',')

    class Group:
        def __init__(self, **kwargs):
            self.id = kwargs.get('groupid')
            self.name = kwargs.get('groupname')
            self.debut_date = kwargs.get('debutdate')
            self.disband_date = kwargs.get('disbanddate')
            self.description = kwargs.get('description')
            self.twitter = kwargs.get('twitter')
            self.youtube = kwargs.get('youtube')
            self.melon = kwargs.get('melon')
            self.instagram = kwargs.get('instagram')
            self.vlive = kwargs.get('vlive')
            self.spotify = kwargs.get('spotify')
            self.fancafe = kwargs.get('fancafe')
            self.facebook = kwargs.get('facebook')
            self.tiktok = kwargs.get('tiktok')
            self.aliases = []
            self.local_aliases = {}  # server_id: [aliases]
            self.members = []
            self.fandom = kwargs.get('fandom')
            self.company = kwargs.get('company')
            self.website = kwargs.get('website')
            self.thumbnail = kwargs.get('thumbnail')
            self.banner = kwargs.get('banner')
            self.gender = kwargs.get('gender')
            self.photo_count = 0
            self.tags = kwargs.get('tags')
            if self.tags:
                self.tags = self.tags.split(',')

