from datetime import timedelta, datetime
import random

import IreneAPIWrapper.exceptions
import asyncio
import disnake
import models
from disnake import ApplicationCommandInteraction as AppCmdInter
from IreneAPIWrapper.models import (
    Person,
    Group,
    Media,
    User,
    Affiliation,
    AutoMedia,
)
from typing import List, Union, Optional, Tuple
from util import logger, botembed
from ..helper import (
    send_message,
    in_game,
    defer_inter,
    get_channel_model,
    increment_trackable,
)
from disnake.ext import commands
from keys import get_keys
from dataclasses import dataclass
import Levenshtein
from difflib import SequenceMatcher


NEXT_POST_KEYWORD = "next_post"


@dataclass(frozen=False, order=True)
class Comparison:
    obj: Union[Person, Group] = None
    search_word: str = None
    target_word: str = None
    similarity: Optional[float] = None

    @staticmethod
    async def create(obj: Union[Person, Group], search_word: str, target_word: str):
        obj = Comparison(obj, search_word, target_word)
        obj.similarity = await obj.calculate()
        return obj

    async def calculate(self):
        """Calculate the distance."""
        return await search_distance(self.search_word, self.target_word)

    def __float__(self):
        """Returns similarity."""
        return self.similarity

    def __int__(self):
        """Returns similarity."""
        return self.similarity

    def __hash__(self):
        return hash(
            (
                "obj",
                self.obj,
                "search_word",
                self.search_word,
                "target_word",
                self.target_word,
            )
        )


async def check_user_requests():
    """Check the user requests and execute day resets"""
    current_day = datetime.now().day
    if models.current_day != current_day:
        models.current_day = current_day
        models.user_requests = {}
        models.requests_today = 0


async def validate_message_idol_call(bot, message: disnake.Message, prefixes: List):
    """Validate the environment in which the message was sent."""
    if not hasattr(message, "guild"):
        return False

    if not message.guild:
        return False

    content_replaced = False
    content = message.content  # we do not want to overwrite the message content.

    if not content:
        return False

    for prefix in prefixes:
        if message.content.startswith(prefix):
            content = content.replace(prefix, "", 1)
            content_replaced = True
            break

    if not content_replaced:
        return False
    return content


async def get_max_similarities(comparisons: List[Comparison]):
    """Get the similarities that match the highest similarity."""
    # add comps based on highest similarity
    _max_comps: Optional[List[Comparison]] = []
    for comp in comparisons:
        if not _max_comps or comp.similarity == _max_comps[0].similarity:
            _max_comps.append(comp)
            continue
    return _max_comps


async def process_message_idol_call(bot, message, content):
    """Complex operations for calling an idol."""
    person_comparisons: List[Comparison] = [
        comp
        for comp in await search_for_obj(
            content, persons=True, split_name=True, return_similarity=True
        )
        if comp.obj.media_count
    ]
    group_comparisons: List[Comparison] = [
        comp
        for comp in await search_for_obj(
            content, persons=False, split_name=True, return_similarity=True
        )
        if comp.obj.media_count
    ]

    person_comparisons.sort(key=lambda comp: comp.similarity, reverse=True)
    group_comparisons.sort(key=lambda comp: comp.similarity, reverse=True)

    obj_pool: List[Union[Person, Group]] = []
    if not (person_comparisons or group_comparisons):
        return  # no results
    elif person_comparisons and not group_comparisons:
        # add comps based on highest similarity
        obj_pool += [
            comp.obj for comp in await get_max_similarities(person_comparisons)
        ]
    elif person_comparisons and group_comparisons:
        # both persons and groups found in a message.

        # a group can be falsely triggered if the person's name is close to the group name.
        # and a person can be falsely triggered if it's close to a person's name.
        # counter this by:
        #    1) Getting the max similarities of both persons and groups.
        #    2) Zip the max group and max person similarities.
        #    3) If there are no matches, then we get the max similarities of the person and group comparisons
        #       and add them to the object pool.

        max_person_similarities = await get_max_similarities(person_comparisons)
        max_group_similarities = await get_max_similarities(group_comparisons)

        for group_comp, person_comp in zip(
            max_group_similarities, max_person_similarities
        ):
            group = group_comp.obj
            person = person_comp.obj
            if await person_in_group(person, group):
                obj_pool.append(person)

        if not obj_pool:
            all_max_similarities = max_person_similarities + max_group_similarities
            obj_pool += [
                comp.obj for comp in await get_max_similarities(all_max_similarities)
            ]
    elif len(group_comparisons) >= 1:
        # groups with no specified persons.
        obj_pool += [comp.obj for comp in await get_max_similarities(group_comparisons)]
    else:
        raise NotImplementedError()

    obj_pool = list(dict.fromkeys(obj_pool))  # remove duplicates
    if not obj_pool:
        return

    user = await User.get(message.author.id)
    if not user:
        await User.insert(message.author.id)
        user = await User.get(message.author.id)
    if not user.is_considered_patron:
        if not await handle_non_patron_media_usage(user, channel=message.channel):
            return
    try:
        media_url = await get_media_from_pool(obj_pool)
        if not media_url:
            return
    except IreneAPIWrapper.exceptions.APIError as e:
        return await bot.handle_api_error(message, e)
    try:
        await message.channel.send(media_url)
        await handle_user_media_usage(user)
    except Exception as e:
        logger.error(f"Failed to send photo to channel ID: {message.channel.id} - {e}")


async def handle_user_media_usage(user):
    """Increment the user's usage and handle the reset for a new day."""
    current_score = models.user_requests.get(user.id)
    models.user_requests[user.id] = 1 if not current_score else current_score + 1

    if models.requests_today % 10 == 0:
        await check_user_requests()
    models.requests_today += 1


async def handle_non_patron_media_usage(
    user, ctx=None, inter=None, channel=None, response_deferred=False
):
    """Handle non patron media usage.

    Returns True if it passes all checks."""
    user_request = models.user_requests.get(user.id)
    if user_request and user_request > get_keys().post_limit:
        await send_message(
            key="become_a_patron_limited",
            channel=channel,
            user=user,
            delete_after=60,
            ctx=ctx,
            inter=inter,
            ephemeral=True,
            response_deferred=response_deferred,
        )
        return False
    return True


async def idol_send_on_message(bot, message: disnake.Message, prefixes: List):
    """Detect an idol call and send media."""
    content = await validate_message_idol_call(bot, message, prefixes)
    if not content:
        return
    loop = asyncio.get_event_loop()
    coro = process_message_idol_call(bot, message, content)
    future = asyncio.run_coroutine_threadsafe(coro, loop)

    await increment_trackable("idol_commands_used")


async def get_media_from_pool(object_pool: List[Union[Person, Group]]):
    random_obj_choice = random.choice(object_pool)
    media = await Media.get_random(
        random_obj_choice.id,
        person=isinstance(random_obj_choice, Person),
        group=isinstance(random_obj_choice, Group),
    )
    if media:
        return await media.fetch_image_host_url()
    else:
        object_pool.remove(random_obj_choice)
        if object_pool:
            return await get_media_from_pool(object_pool)


async def person_in_group(person, group):
    return any(
        [
            person_aff == group_aff and len(group.affiliations) > 1
            for person_aff in person.affiliations
            for group_aff in group.affiliations
        ]
    )


async def auto_complete_type(inter: AppCmdInter, user_input: str) -> List[str]:
    """Autocomplete the search for a person or group."""
    item_type = inter.filled_options["item_type"]
    if item_type == "person":
        persons = await auto_complete_person(inter, user_input)
        return persons[:24]
    elif item_type == "group":
        groups = await auto_complete_group(inter, user_input)
        return groups[:24]
    elif item_type == "affiliation":
        affs = await auto_complete_affiliation(inter, user_input)
        return affs[:24]
    else:
        raise RuntimeError(
            "item_type returned something other than 'person', 'group', or 'affiliation'"
        )


async def auto_complete_file_type(inter: AppCmdInter, user_input: str) -> List[str]:
    """Autocomplete the file types for media."""
    return ["gif", "jfif", "mp4", "png", "jpg", "webm", "webp", "jpeg"]


async def auto_complete_call_count(inter: AppCmdInter, user_input: str) -> List[int]:
    """Autocomplete the counts for calling media."""
    if (await User.get(inter.user.id)).is_considered_patron:
        return [1, 2, 3, 4, 5]
    else:
        return [1]


async def auto_complete_person(inter: AppCmdInter, user_input: str) -> List[str]:
    """Autocomplete person search."""
    if user_input.isnumeric():
        return [
            f"{person.id}) {str(person.name)}"
            for person in await Person.get_all()
            if str(person.id).startswith(user_input)
        ][:24]
    else:
        return [
            f"{person.id}) {str(person.name)}"
            for person in await Person.get_all()
            if user_input.lower() in str(person.name).lower()
        ][:24]


async def auto_complete_group(inter: AppCmdInter, user_input: str) -> List[str]:
    """Autocomplete group search."""
    if user_input.isnumeric():
        return [
            f"{group.id}) {group.name}"
            for group in await Group.get_all()
            if str(group.id).startswith(user_input)
        ][:24]
    else:
        return [
            f"{group.id}) {group.name}"
            for group in await Group.get_all()
            if user_input.lower() in group.name.lower()
        ][:24]


async def auto_complete_affiliation(inter: AppCmdInter, user_input: str) -> List[str]:
    """Autocomplete affiliation search."""
    if user_input.isnumeric():
        return [
            f"{aff.id}) {aff.group.name} {aff.stage_name}"
            for aff in await Affiliation.get_all()
            if str(aff.id).startswith(user_input)
        ][:24]
    else:
        return [
            f"{aff.id}) {aff.group.name} {aff.stage_name}"
            for aff in await Affiliation.get_all()
            if user_input.lower() in str(aff).lower()
        ][:24]


async def get_call_count_leaderboard(
    objects: Union[List[Person], List[Group]]
) -> Optional[List[Tuple[Union[Person, Group], int]]]:
    """
    Get a list of sorted (descending) values for the call count of a Person or Group.

    :param objects: Union[List[:ref:`Person`], List[:ref:`Group`]]
        A list of Persons or Groups.

    :returns: Optional[List[Tuple[Union[Person, Group], int]]]
        A list of tuples containing a Person/Group and their call count (in descending order).
    """
    if not objects:
        return None
    objects = list(objects)

    if isinstance(objects[0], Person):
        objects.sort(key=lambda x: x.call_count, reverse=True)
        person_called_amounts_final = []
        for obj in objects:
            person_called_amounts_final.append((obj, obj.call_count))
        return person_called_amounts_final

    elif isinstance(objects[0], Group):
        group_called_amounts = {}
        group_called_amounts_final = []
        for obj in objects:
            persons = [affiliation.person for affiliation in obj.affiliations]
            group_called_amounts[obj] = sum(person.call_count for person in persons)
        group_called_amounts_sorted = sorted(
            group_called_amounts, key=lambda x: group_called_amounts[x], reverse=True
        )
        for obj in group_called_amounts_sorted:
            group_called_amounts_final.append((obj, group_called_amounts[obj]))
        return group_called_amounts_final
    else:
        raise NotImplementedError(
            f"An entity aside from a person or object has not been implemented."
        )


async def search_for_obj(
    search_name, persons=True, split_name=False, return_similarity=False
) -> List[Union[Person, Comparison, Group]]:
    """
    Check if a name matches with an alias or a Person/Group's full name.

    :param search_name: str
        The name to search for.
    :param persons: bool
        Whether to search for Persons [Otherwise will search for Groups]
    :param split_name: bool
        Whether to split the name by spaces when doing searches.
    :param return_similarity: bool
        Return the similarity of the searched objects.

    :returns: Union[List[:ref:`Person`], List[:ref:`Group`], List[:ref:`Comparison`]]
        A list of persons or groups that match the search filter.
    """
    objects: Union[List[Person], List[Group]] = (
        await Person.get_all() if persons else await Group.get_all()
    )
    if not return_similarity:
        filtered = [
            item
            for item in objects
            if await _filter_by_name(
                item,
                search_name,
                split_name=split_name,
                return_similarity=return_similarity,
            )
        ]
        return filtered
    else:
        filtered = [
            await _filter_by_name(
                item,
                search_name,
                split_name=split_name,
                return_similarity=return_similarity,
            )
            for item in objects
        ]
        return [comp for list_of_comps in filtered for comp in list_of_comps]


async def _filter_by_name(
    obj: Union[Person, Group],
    name: str,
    similarity_required=0.75,
    split_name=False,
    return_similarity=True,
):
    """
    Compares distance against person/group aliases.
    Any aliases/names with a default 75% or greater similarity will count as a result.

    :returns: bool
        Whether the Person or Group object is included in the filter.

    """
    if not name:
        return False

    if similarity_required < 0 or similarity_required > 100:
        similarity_required = 0.75
    elif 1 < similarity_required <= 100:
        similarity_required = (
            similarity_required / 100
        )  # putting as decimal between 0 and 1.

    final_results: List[Comparison] = []
    aliases = await obj.get_aliases_as_strings()
    name = name.lower()
    names = [name] if not split_name else name.split(" ") + [name]

    # check for matching aliases
    if not return_similarity:
        if any(
            [
                await search_distance(sub_name, alias.lower()) >= similarity_required
                for sub_name in names
                for alias in aliases
            ]
        ):
            return True
    else:
        alias_comparisons = [
            await Comparison.create(obj, sub_name, alias.lower())
            for sub_name in names
            for alias in aliases
        ]
        final_results += [
            comp for comp in alias_comparisons if comp.similarity >= similarity_required
        ]

    # check for matching group names or person full names.
    if not return_similarity:
        if any(
            [
                await search_distance(sub_name, str(obj).lower()) >= similarity_required
                for sub_name in names
            ]
        ):
            return True
    else:
        name_comparisons = [
            await Comparison.create(obj, sub_name, str(obj).lower())
            for sub_name in names
        ]
        final_results += [
            comp for comp in name_comparisons if comp.similarity >= similarity_required
        ]

    # check for matching stage names
    if isinstance(obj, Person):
        for aff in obj.affiliations:
            if not return_similarity:
                if any(
                    [
                        await search_distance(sub_name, aff.stage_name.lower())
                        >= similarity_required
                        for sub_name in names
                    ]
                ):
                    return True
            else:
                aff_comparisons = [
                    await Comparison.create(obj, sub_name, aff.stage_name.lower())
                    for sub_name in names
                ]
                final_results += [
                    comp
                    for comp in aff_comparisons
                    if comp.similarity >= similarity_required
                ]

    if not return_similarity:
        return False

    # check if the object's name is in the name and do a comparison check. Only works if returning similarity.
    if str(obj).lower() in name:
        final_results.append(await Comparison.create(obj, name, str(obj).lower()))

    final_results.sort(reverse=True)
    return list(dict.fromkeys(final_results))  # remove duplicates


def get_random_color():
    """Retrieves a random hex color."""
    r = lambda: random.randint(0, 255)
    return int(
        ("%02X%02X%02X" % (r(), r(), r())), 16
    )  # must be specified to base 16 since 0x is not present


async def search_distance(search_word: str, target_word: str) -> Optional[float]:
    """Get the distance of two words/phrases with cache considered."""
    return (
        _search_distance_dict(models.distance_between_words, search_word, target_word)
        or _search_distance_dict(
            models.distance_between_words, target_word, search_word
        )
        or await _get_string_distance(search_word, target_word)
    )


def _search_distance_dict(dictionary, key_word, compared_word):
    """Search the distance dictionary for saved ratios."""
    cache = dictionary.get(key_word)
    if cache:
        return cache.get(compared_word)  # similarity


async def _get_string_distance(search_word: str, target_word: str):
    """Get the similarity of one string to another string."""
    similarity = Levenshtein.ratio(search_word, target_word)
    if models.distance_between_words.get(search_word):
        models.distance_between_words[search_word][target_word] = similarity
    else:
        models.distance_between_words[search_word] = {target_word: similarity}
    return similarity


async def process_call(
    item_type,
    item_id,
    user_id,
    ctx=None,
    inter=None,
    allowed_mentions=None,
    file_type=None,
    count=1,
):
    response_deferred = await defer_inter(inter)
    user = await User.get(user_id)

    if not user.is_considered_patron:
        if not await handle_non_patron_media_usage(
            user, inter=inter, ctx=ctx, response_deferred=response_deferred
        ):
            return

    for i in range(count):
        media: Media = await Media.get_random(
            object_id=item_id,
            group=item_type == "group",
            person=item_type == "person",
            affiliation=item_type == "affiliation",
            file_type=file_type,
        )

        if not media:
            return await send_message(
                key="no_results",
                user=user,
                ctx=ctx,
                inter=inter,
                allowed_mentions=allowed_mentions,
                response_deferred=response_deferred,
            )

        if await send_message(
            msg=await media.fetch_image_host_url(),
            user=user,
            ctx=ctx,
            inter=inter,
            allowed_mentions=allowed_mentions,
            response_deferred=response_deferred,
        ):
            await handle_user_media_usage(user)


async def process_card(
    item_type, item_id, user_id, ctx=None, inter=None, allowed_mentions=None
):
    """Process a person/group/affiliation card."""
    user = await User.get(user_id)
    item_type = item_type.lower()
    obj: Optional[Union[Person, Group, Affiliation]]
    if item_type == "group":
        obj = await Group.get(item_id)
    elif item_type == "affiliation":
        obj = await Affiliation.get(item_id)
    else:
        obj = await Person.get(item_id)

    if not obj:
        return await send_message(user=user, key="no_results", ctx=ctx, inter=inter)

    card_data = await obj.get_card(markdown=True, extra=True)
    avatar, banner = None, None
    if isinstance(obj, (Group, Person)):
        avatar = None if not obj.display else obj.display.avatar
        banner = None if not obj.display else obj.display.banner

    embed = await get_card_embed(
        card_info=card_data, avatar=avatar, banner=banner, title=str(obj)
    )
    await send_message(user=user, ctx=ctx, inter=inter, embed=embed)


async def get_card_embed_desc(card_info):
    """Get an embedded card's description."""
    if not card_info:
        return ""

    desc = ""
    for item in card_info:
        if isinstance(item, list):
            desc += await get_card_embed_desc(item)
        else:
            desc += f"{item}\n"
    return desc


async def get_card_embed(card_info, avatar, banner, title):
    avatar = None if not avatar else avatar.url
    banner = None if not banner else banner.url

    desc = await get_card_embed_desc(card_info)

    embed = disnake.Embed(
        color=disnake.Color.brand_green(), title=title, description=desc
    )
    if avatar:
        embed.set_thumbnail(avatar)
    if banner:
        embed.set_image(banner)
    return embed


async def process_who_is(
    media_id: int,
    user_id: int,
    ctx: commands.Context = None,
    inter: AppCmdInter = None,
    allowed_mentions=None,
):
    """
    Process the whois command.
    """
    response_deferred = await defer_inter(inter)
    user = await User.get(user_id=user_id)

    if await in_game(user, must_be_host=False):
        return await send_message(
            key="nice_try_cheater",
            ctx=ctx,
            inter=inter,
            allowed_mentions=allowed_mentions,
            user=user,
            response_deferred=response_deferred,
        )

    try:
        media = await Media.get(media_id)  # refresh objs
    except IreneAPIWrapper.exceptions.APIError as e:  # over int64
        media = None
    if not media:
        return await send_message(
            media_id,
            key="media_not_found",
            ctx=ctx,
            inter=inter,
            allowed_mentions=allowed_mentions,
            user=user,
            response_deferred=response_deferred,
        )

    aff = media.affiliation
    person = aff.person
    group = aff.group

    result = (
        f":\nAffiliation: {aff.id} - {aff.stage_name}\n"
        f"Person: {person.id} - {str(person.name)}\n"
        f"Group: {group.id} - {str(group)}"
    )

    await send_message(
        media_id,
        result,
        key="media_who_is",
        ctx=ctx,
        inter=inter,
        allowed_mentions=allowed_mentions,
        user=user,
        response_deferred=response_deferred,
    )


async def process_random_person(
    user_id,
    ctx=None,
    inter=None,
):
    response_deferred = await defer_inter(inter)
    user = await User.get(user_id)
    if not user.is_considered_patron:
        if not await handle_non_patron_media_usage(
            user, inter=inter, ctx=ctx, response_deferred=response_deferred
        ):
            return

    all_persons = list(await Person.get_all())

    person: Person = random.choice(all_persons)
    while not person.media_count:  # ensure media exists.
        person: Person = random.choice(all_persons)

    media = await Media.get_random(person.id, person=True)

    if await send_message(
        msg=await media.fetch_image_host_url(),
        user=user,
        inter=inter,
        ctx=ctx,
        response_deferred=response_deferred,
    ):
        await handle_user_media_usage(user)


async def process_count(
    item_type,
    item_id,
    user_id,
    ctx=None,
    inter=None,
):
    """Process the count of media a person/group/affiliation has."""
    response_deferred = await defer_inter(inter)
    user = await User.get(user_id)

    if item_type == "group":
        group = await Group.get(item_id)
        medias: List[Media] = await Media.get_all(group.affiliations, count_only=True)
    elif item_type == "affiliation":
        affiliation = await Affiliation.get(item_id)
        medias: List[Media] = await Media.get_all([affiliation], count_only=True)
    else:
        person = await Person.get(item_id)
        medias: List[Media] = await Media.get_all(person.affiliations, count_only=True)

    await send_message(
        medias,
        item_type,
        key="media_count",
        user=user,
        ctx=ctx,
        inter=inter,
        response_deferred=response_deferred,
    )


async def process_distance(search_phrase, target_phrase, user_id, inter=None, ctx=None):
    """Process the distance search of two phrases."""
    response_deferred = await defer_inter(inter)
    user = await User.get(user_id)

    if len(search_phrase) * len(target_phrase) > 2000000:
        return await send_message(
            key="distance_too_long",
            user=user,
            inter=inter,
            ctx=ctx,
            response_deferred=response_deferred,
        )
    distance_str = (
        f"**{await search_distance(search_phrase, target_phrase) * 100:.2f}%**"
    )
    await send_message(
        distance_str,
        key="distance_measured",
        user=user,
        inter=inter,
        ctx=ctx,
        response_deferred=response_deferred,
    )


async def process_aliases(
    item_type,
    item_id,
    user_id,
    ctx=None,
    inter=None,
):
    """Process the aliases of a person/group."""
    response_deferred = await defer_inter(inter)
    user = await User.get(user_id)

    if item_type == "group":
        obj = await Group.get(item_id)
    else:
        obj = await Person.get(item_id)

    embed = await botembed.create_bot_author_embed(
        title=f"Aliases for {str(obj)}",
        color=disnake.Color.blurple(),
        description=", ".join(await obj.get_aliases_as_strings() or []) or "None",
    )

    await send_message(
        embed=embed,
        user=user,
        ctx=ctx,
        inter=inter,
        response_deferred=response_deferred,
    )


async def process_auto_aff(
    channel_id,
    aff_id,
    user_id: int,
    ctx=None,
    inter=None,
    allowed_mentions=None,
    hours_to_send_after=12,
    remove=False,
    guild_id=None,
):
    """Process Auto Affiliation"""
    response_deferred = await defer_inter(inter)
    user = await User.get(user_id)

    if guild_id:
        await get_channel_model(channel_id, guild_id)  # works as an insert.

    aff = await Affiliation.get(affiliation_id=aff_id)
    if not aff:
        return await send_message(
            aff_id,
            key="affiliation_does_not_exist",
            user=user,
            ctx=ctx,
            inter=inter,
            allowed_mentions=allowed_mentions,
            response_deferred=response_deferred,
        )

    auto_media = await AutoMedia.get(channel_id)
    if not remove:
        if (
            not user.is_considered_patron
            and len(auto_media.aff_times) >= get_keys().auto_send_limit
        ):
            return await send_message(
                key="become_a_patron_limited",
                ctx=ctx,
                user=user,
                delete_after=60,
                inter=inter,
                ephemeral=True,
                response_deferred=response_deferred,
            )
        await AutoMedia.insert(
            channel_id=channel_id,
            affiliation_id=aff_id,
            hours_after=hours_to_send_after,
        )

        await send_message(
            aff_id,
            channel_id,
            key="auto_media_added",
            user=user,
            ctx=ctx,
            inter=inter,
            allowed_mentions=allowed_mentions,
            response_deferred=response_deferred,
        )
    else:
        for aff_time in auto_media.aff_times:
            if aff_time.affiliation_id == aff_id:
                await auto_media.delete_aff_time(aff_time)

        await send_message(
            aff_id,
            channel_id,
            key="auto_media_removed",
            user=user,
            ctx=ctx,
            inter=inter,
            allowed_mentions=allowed_mentions,
            response_deferred=response_deferred,
        )


async def process_list_auto_aff(
    channel_id, user_id: int, ctx=None, inter=None, allowed_mentions=None
):
    """List the auto affiliations."""
    response_deferred = await defer_inter(inter)
    user = await User.get(user_id)
    auto_media = await AutoMedia.get(channel_id)
    results = "\n".join(
        [
            f"{aff_time.affiliation_id} | {aff_time.hours_after} hours"
            for aff_time in auto_media.aff_times
        ]
    )
    await send_message(
        channel_id,
        results,
        key="auto_media_list",
        user=user,
        ctx=ctx,
        inter=inter,
        allowed_mentions=allowed_mentions,
        response_deferred=response_deferred,
    )


async def process_loop_auto_aff(bot):
    """Process the loop for automatically sending affiliation media."""
    for auto_media in await AutoMedia.get_all():
        for aff_time in auto_media.aff_times:
            if hasattr(aff_time, NEXT_POST_KEYWORD) and datetime.now() < getattr(
                aff_time, NEXT_POST_KEYWORD
            ):
                continue
            try:
                media = await Media.get_random(
                    object_id=aff_time.affiliation_id, affiliation=True
                )
                if not media:
                    continue

                url = await media.fetch_image_host_url()

                text_channel = bot.get_channel(auto_media.id)
                if not text_channel:
                    try:
                        text_channel = await bot.fetch_channel(auto_media.id)
                    except disnake.Forbidden:
                        # Permanently remove the aff time. We don't want to keep making requests.
                        await auto_media.delete_aff_time(aff_time=aff_time)
                    except disnake.NotFound:
                        # Permanently remove the media.
                        await auto_media.delete_aff_time(aff_time=aff_time)

                if not text_channel:
                    continue

                try:
                    await send_message(msg=f"{url}", channel=text_channel)
                except disnake.Forbidden:
                    # Permanently remove the aff time. We don't want to keep making requests.
                    await auto_media.delete_aff_time(aff_time=aff_time)
                except Exception as e:
                    bot.logger.error(f"Auto Affiliation (Inner) Loop Error -> {e}")

                setattr(
                    aff_time,
                    NEXT_POST_KEYWORD,
                    datetime.now() + timedelta(hours=aff_time.hours_after),
                )
            except Exception as e:
                bot.logger.error(f"Auto Affiliation (Outer) Loop Error -> {e}")
