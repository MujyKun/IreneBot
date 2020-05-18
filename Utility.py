import discord
import random
import asyncio
from module import logger as log
from module import keys


def get_db_connection():
    return [keys.DBconn, keys.DBconn.cursor()]


DBconn = get_db_connection()[0]
c = get_db_connection()[1]
DBconn.autocommit = False


async def get_random_color():
    r = lambda: random.randint(0, 255)
    return int(('%02X%02X%02X' % (r(), r(), r())), 16)  # must be specified to base 16 since 0x is not present


async def check_in_game(user_id):
    c.execute("SELECT COUNT(*) From currency.Games WHERE Player1 = %s OR Player2 = %s", (user_id, user_id))
    check = fetch_one()
    return check == 0


def fetch_one():
    try:
        results = c.fetchone()[0]
    except Exception as e:
        results = []
        pass
    return results


def fetch_all():
    try:
        results = c.fetchall()
    except Exception as e:
        log.console(e)
        results = []
        pass
    return results


async def register_user(user_id):
    c.execute("SELECT COUNT(*) FROM currency.Currency WHERE UserID = %s", (user_id,))
    count = fetch_one()
    if count == 0:
        c.execute("INSERT INTO currency.Currency (UserID, Money) VALUES (%s, %s)", (user_id, "100"))
        DBconn.commit()
        return True
    elif count == 1:
        return False


async def get_user_has_money(user_id):
    c.execute("SELECT COUNT(*) FROM currency.Currency WHERE UserID = %s", (user_id,))
    return not fetch_one() == 0


async def get_balance(user_id):
    if not (await register_user(user_id)):
        c.execute("SELECT money FROM currency.currency WHERE userid = %s", (user_id,))
        return int(fetch_one())
    else:
        return 100


async def shorten_balance(money):  # money must be passed in as a string.
    if int(money) < 1000000:
        return money
    money_length = len(money)
    c.execute("SELECT COUNT(*) FROM currency.valueplaces WHERE Length = %s", (money_length,))
    length = fetch_one()
    c.execute("SELECT COUNT(*) FROM currency.valueplaces WHERE Length2 = %s", (money_length,))
    length2 = fetch_one()
    c.execute("SELECT COUNT(*) FROM currency.valueplaces WHERE Length3 = %s", (money_length,))
    length3 = fetch_one()
    if length == 1:
        first_numbers = money[0]
        c.execute("SELECT Name FROM currency.valueplaces WHERE Length = %s", (money_length,))
        value_place = fetch_one()
    elif length2 == 1:
        first_numbers = money[0:2]
        c.execute("SELECT Name FROM currency.valueplaces WHERE Length2 = %s", (money_length,))
        value_place = fetch_one()
    elif length3 == 1:
        first_numbers = money[0:3]
        c.execute("SELECT Name FROM currency.valueplaces WHERE Length3 = %s", (money_length,))
        value_place = fetch_one()
    else:
        return "0"
    return f"{first_numbers} {value_place}"


async def update_balance(user_id, new_balance):
    c.execute("UPDATE currency.Currency SET Money = %s::text WHERE UserID = %s", (str(new_balance), user_id))
    DBconn.commit()


async def get_level(user_id, command):
    c.execute(f"SELECT COUNT(*) FROM currency.Levels WHERE UserID = %s AND {command} > %s", (user_id, 1))
    if fetch_one() == 0:
        level = 1
    else:
        c.execute(f"SELECT {command} FROM currency.Levels WHERE UserID = %s", (user_id,))
        level = fetch_one()
    return int(level)


async def set_level(user_id, level, command):
    def update_level():
        c.execute(f"UPDATE currency.Levels SET {command} = %s WHERE UserID = %s", (level, user_id))
        DBconn.commit()

    c.execute(f"SELECT COUNT(*) FROM currency.Levels WHERE UserID = %s", (user_id,))
    if fetch_one() == 0:
        c.execute("INSERT INTO currency.Levels VALUES(%s, NULL, NULL, NULL, NULL, 1)", (user_id,))
        DBconn.commit()
        update_level()
    else:
        update_level()


async def create_embed(title="Irene", color=0xffb6c1, title_desc="", footer_desc="Thanks for using Irene!"):
    if title_desc == "":
        embed = discord.Embed(title=title, color=color)
    else:
        embed = discord.Embed(title=title, color=color, description=title_desc)
    embed.set_author(name="Irene", url='https://www.youtube.com/watch?v=dQw4w9WgXcQ',
                     icon_url='https://cdn.discordapp.com/emojis/693392862611767336.gif?v=1')
    embed.set_footer(text=footer_desc, icon_url='https://cdn.discordapp.com/emojis/683932986818822174.gif?v=1')
    return embed


async def get_xp(level, command):
    """Returns money/experience needed for a certain level."""
    if command == "profile":
        return 250 * level
    return int((2 * 350) * (2 ** (level - 2)))  # 350 is base value (level 1)


async def check_reaction(msg, user_id, reaction_needed, client):
    def react_check(reaction_used, user_reacted):
        return (user_reacted.id == user_id) and (reaction_used.emoji == reaction_needed)

    try:
        reaction, user = await client.wait_for('reaction_add', timeout=60, check=react_check)
        return True
    except asyncio.TimeoutError:
        await msg.delete()
        return False


async def get_rob_percentage(level):
    chance = int(6 + (level // 10))  # first 10 levels is 6 for 30% chance
    if chance > 16:
        chance = 16
    return chance


async def get_robbed_amount(author_money, user_money, level):
    max_amount = int(user_money // 100)  # b value
    if max_amount > int(author_money // 2):
        max_amount = int(author_money // 2)
    min_amount = int(max_amount * (level // 100))
    if min_amount > max_amount:  # kind of ironic, but it is possible for min to surpass max in this case
        robbed_amount = random.randint(max_amount, min_amount)
    else:
        robbed_amount = random.randint(min_amount, max_amount)
    return robbed_amount


async def get_cooldown_time(time):
    time = round(time)
    time_returned = ""
    if time % 3600 != time:
        hours = int(time//3600)
        if hours != 0:
            time_returned += f"{int(time//3600)}h "
    if time % 3600 != 0:
        minutes = int((time % 3600) // 60)
        if minutes != 0:
            time_returned += f"{int((time% 3600) // 60)}m "
    if (time % 3600) % 60 < 60:
        seconds = (time % 3600) % 60
        if seconds != 0:
            time_returned += f"{int((time% 3600) % 60)}s"
    return time_returned


def check_embed_exists(message):
    try:
        for embed_check in message.embeds:
            if len(embed_check) > 0:
                return True
    except Exception as e:
        pass
    return False


def check_message_not_empty(message):
    try:
        if len(message.clean_content) >= 1:
            return True
    except Exception as e:
        pass
    return False


def get_message_prefix(message):
    try:
        if check_message_not_empty(message):
            return message.clean_content[0]
    except Exception as e:
        pass
    return '|'


async def get_all_members():
    c.execute("SELECT id, fullname, stagename, ingroups, aliases FROM groupmembers.Member")
    return fetch_all()


async def get_all_groups():
    c.execute("SELECT groupid, groupname, aliases FROM groupmembers.groups ORDER BY groupname")
    return fetch_all()


async def get_members_in_group(group_name):
    c.execute(f"SELECT groupid FROM groupmembers.groups WHERE groupname = %s", (group_name,))
    group_id = fetch_one()
    all_members = await get_all_members()
    members_in_group = []
    for member in all_members:
        member_info = [member[0], member[2]]
        in_groups = member[3].split(',')
        if str(group_id) in in_groups:
            members_in_group.append(member_info)
    return members_in_group


async def get_member(member_id):
    c.execute("SELECT id, fullname, stagename, ingroups, aliases FROM groupmembers.member WHERE id = %s", (member_id,))
    return c.fetchone()


async def get_group_name(group_id):
    c.execute("SELECT groupname FROM groupmembers.groups WHERE groupid = %s", (group_id,))
    return fetch_one()


async def get_group_id_from_member(member_id):
    member_info = await get_member(member_id)
    return ((member_info[3]).split(','))[0]


async def check_left_or_right_reaction_embed(msg, client, embed_lists, reaction1="\U00002b05", reaction2="\U000027a1"):
    await msg.add_reaction(reaction1)  # left arrow by default
    await msg.add_reaction(reaction2)  # right arrow by default

    def reaction_check(user_reaction, reaction_user):
        return ((user_reaction.emoji == '➡') or (
                    user_reaction.emoji == '⬅')) and reaction_user != msg.author and user_reaction.message.id == msg.id

    async def change_page(c_page):
        try:
            reaction, user = await client.wait_for('reaction_add', check=reaction_check)
            if reaction.emoji == '➡':
                c_page += 1
                if c_page < len(embed_lists):
                    embed = embed_lists[c_page]
                    await msg.edit(embed=embed)
                else:
                    c_page -= 1
            elif reaction.emoji == '⬅':
                c_page -= 1
                if c_page >= 0:
                    embed = embed_lists[c_page]
                    await msg.edit(embed=embed)
                else:
                    c_page += 1
            await msg.clear_reactions()
            await msg.add_reaction(reaction1)
            await msg.add_reaction(reaction2)
            await change_page(c_page)
        except Exception as e:
            log.console(f"check_left_or_right_reaction_embed - {e}")
            await change_page(c_page)
    await change_page(0)


async def set_embed_author_and_footer(embed, footer_message):
    embed.set_author(name="Irene", url='https://www.youtube.com/watch?v=dQw4w9WgXcQ',
                     icon_url='https://cdn.discordapp.com/emojis/693392862611767336.gif?v=1')
    embed.set_footer(text=footer_message,
                     icon_url='https://cdn.discordapp.com/emojis/683932986818822174.gif?v=1')
    return embed


async def send_names(ctx, mode, client):
    async def check_mode(embed_temp):
        if mode == "fullname":
            embed_temp = await set_embed_author_and_footer(embed_temp, "Type %members for Stage Names.")
        else:
            embed_temp = await set_embed_author_and_footer(embed_temp, "Type %fullnames for Full Names.")
        return embed_temp

    embed_lists = []
    all_members = await get_all_members()
    all_groups = await get_all_groups()
    embed = discord.Embed(title="Idol List", color=0xffb6c1)
    counter = 1
    for group in all_groups:
        names = []
        group_id = group[0]
        group_name = group[1]
        if group_name != "NULL":
            for member in all_members:
                if mode == "fullname":
                    member_name = member[1]
                else:
                    member_name = member[2]
                member_in_group_ids = (member[3]).split(',')
                for member_in_group_id in member_in_group_ids:
                    if int(member_in_group_id) == group_id:
                        names.append(f"{member_name} | ")
            final_names = "".join(names)
            if len(final_names) == 0:
                final_names = "None"
            embed.insert_field_at(counter, name=f"{group_name} ({group_id})", value=final_names, inline=False)
            if counter == 10:
                await check_mode(embed)
                embed_lists.append(embed)
                embed = discord.Embed(title="Idol List", color=0xffb6c1)
                counter = 0
            counter += 1
    # if counter did not reach 10, current embed needs to be saved.
    await check_mode(embed)
    embed_lists.append(embed)
    msg = await ctx.send(embed=embed_lists[0])
    await check_left_or_right_reaction_embed(msg, client, embed_lists)


async def set_embed_with_all_aliases(mode):
    check = False
    if mode == "Group":
        all_info = await get_all_groups()
    else:
        all_info = await get_all_members()
    embed = discord.Embed(title=f"{mode} Aliases", description="", color=0xffb6c1)
    for info in all_info:
        id = info[0]
        name = info[1]
        aliases = info[2]
        if mode != "Group":
            stage_name = info[2]
            aliases = info[4]
            check = True
        if aliases != "NULL" and aliases is not None:
            if check:
                embed.add_field(name=f"{name} ({stage_name} [{id}])", value=aliases, inline=True)
            else:
                embed.add_field(name=f"{name} [{id}]", value=aliases, inline=True)
    return embed


async def check_idol_post_reactions(message, client, user_msg):
    try:
        if message is not None:
            reload_image_emoji = "<:ReloadImage:694109526491922463>"
            dead_link_emoji = "<:DeadLink:695787733460844645>"
            await message.add_reaction(reload_image_emoji)
            await message.add_reaction(dead_link_emoji)
            message = await message.channel.fetch_message(message.id)

            def image_check(user_reaction, reaction_user):
                return reaction_user == user_msg.author and (
                        str(user_reaction.emoji) == dead_link_emoji or str(user_reaction.emoji)
                        == reload_image_emoji) and user_reaction.message.id == message.id

            async def reload_image(message1):
                try:
                    reaction, user = await client.wait_for('reaction_add', check=image_check)
                    if str(reaction) == reload_image_emoji:
                        channel = message1.channel
                        try:
                            link = message1.embeds[0].url
                        except:
                            link = message1.content
                        await message1.delete()
                        # message1 = await channel.send(embed=embed)
                        count = 0
                        keep_going = True
                        while keep_going:
                            message1 = await channel.send(link)
                            await message1.delete()
                            count += 1
                            # how many times to resend the message.
                            if count == 3:
                                keep_going = False
                        message1 = await channel.send(link)
                        await check_idol_post_reactions(message1, client, user_msg)
                    elif str(reaction) == dead_link_emoji:
                        try:
                            link = message1.embeds[0].url
                        except:
                            link = message1.content
                        c.execute("INSERT INTO groupmembers.DeadLinkFromUser VALUES(%s,%s)", (link, user.id))
                        DBconn.commit()
                        await message1.delete()

                except Exception as e:
                    log.console(e)
                    pass
            await reload_image(message)
    except Exception as e:
        pass


async def get_id_where_member_matches_name(name):
    all_members = await get_all_members()
    id_list = []
    for member in all_members:
        member_id = member[0]
        full_name = member[1].lower()
        stage_name = member[2].lower()
        aliases = member[4]
        if name.lower() == full_name or name.lower() == stage_name:
            id_list.append(member_id)
        if aliases != "NULL":
            for alias in aliases.split(','):
                if alias == name.lower():
                    id_list.append(member_id)
    # remove any duplicates
    id_list = list(dict.fromkeys(id_list))
    return id_list


async def get_id_where_group_matches_name(name):
    all_groups = await get_all_groups()
    id_list = []
    for group in all_groups:
        group_id = group[0]
        group_name = group[1].lower()
        aliases = group[2]
        if name.lower() == group_name.lower():
            id_list.append(group_id)
        if aliases is not None:
            for alias in aliases.split(','):
                if alias == name.lower():
                    id_list.append(group_id)
    # remove any duplicates
    id_list = list(dict.fromkeys(id_list))
    return id_list


async def get_random_photo_from_member(member_id):
    c.execute("SELECT link FROM groupmembers.imagelinks WHERE memberid = %s", (member_id,))
    return (random.choice(fetch_all()))[0]


async def update_member_count(member_id):
    c.execute("SELECT COUNT(*) FROM groupmembers.Count WHERE MemberID = %s", (member_id,))
    count = fetch_one()
    if count == 0:
        c.execute("INSERT INTO groupmembers.Count VALUES(%s, %s)", (member_id, 1))
    else:
        c.execute("SELECT Count FROM groupmembers.Count WHERE MemberID = %s", (member_id,))
        count = fetch_one()
        count += 1
        c.execute("UPDATE groupmembers.Count SET Count = %s WHERE MemberID = %s", (count, member_id))
    DBconn.commit()


async def idol_post(channel, member_id, photo_link, group_id=None):
    try:
        member_info = await get_member(member_id)
        check = photo_link.find("tenor.com", 0)
        if check == -1:
            if group_id is None:
                embed = discord.Embed(title=f"{member_info[1]} ({member_info[2]})", color=await get_random_color(), url=photo_link)
            else:
                embed = discord.Embed(title=f"{await get_group_name(group_id)} ({member_info[2]})", color=await get_random_color(), url=photo_link)
            embed.set_image(url=photo_link)
            msg = await channel.send(embed=embed)
            await update_member_count(member_id)
            return msg
        elif check != -1:
            msg = await channel.send(photo_link)
            return msg
    except Exception as e:
        log.console(e)


async def add_to_logging(server_id, channel_id):  # return true if status is on
        c.execute("SELECT COUNT(*) FROM logging.servers WHERE serverid = %s", (server_id,))
        if fetch_one() == 0:
            c.execute("INSERT INTO logging.servers (serverid, channelid, status, sendall) VALUES (%s, %s, %s, %s)", (server_id, channel_id, 1, 1))
            DBconn.commit()
        else:
            await set_logging_status(server_id, 1)
            c.execute("SELECT channelid FROM logging.servers WHERE serverid = %s", (server_id,))
            if fetch_one() != channel_id:
                c.execute("UPDATE logging.servers SET channelid = %s WHERE serverid = %s", (channel_id, server_id))
        return True


async def check_if_logged(server_id=None, channel_id=None):  # only one parameter should be passed in
    if channel_id is not None:
        c.execute("SELECT COUNT(*) FROM logging.channels WHERE channelid = %s", (channel_id,))
        if fetch_one() == 1:
            return True
        else:
            return False
    elif server_id is not None:
        try:
            c.execute("SELECT status FROM logging.servers WHERE serverid = %s", (server_id,))
            if fetch_one() == 1:
                return True
            else:
                return False
        except Exception as e:
            return False


async def set_logging_status(server_id, status):  # status can only be 0 or 1
    c.execute("UPDATE logging.servers SET status = %s WHERE serverid = %s", (status, server_id))
    DBconn.commit()


async def get_logging_id(server_id):
    c.execute("SELECT id FROM logging.servers WHERE serverid = %s", (server_id,))
    return fetch_one()


async def check_logging_requirements(message):
    if not message.author.bot:
        if await check_if_logged(server_id=message.guild.id):
            if await check_if_logged(channel_id=message.channel.id):
                return True
    return False


async def get_attachments(message):
    files = None
    if len(message.attachments) != 0:
        files = []
        for attachment in message.attachments:
            files.append(await attachment.to_file())
    return files


async def get_log_channel_id(message, client):
    c.execute("SELECT channelid FROM logging.servers WHERE serverid = %s", (message.guild.id,))
    return client.get_channel(fetch_one())
