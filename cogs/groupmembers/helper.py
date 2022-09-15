import datetime
import random

import IreneAPIWrapper.exceptions
import asyncio
import disnake
from disnake import ApplicationCommandInteraction as AppCmdInter
from IreneAPIWrapper.models import Person, Group, Media, User
from typing import List, Union, Optional, Tuple, Dict
from util import logger
from ..helper import send_message
from disnake.ext import commands
from keys import get_keys
from difflib import SequenceMatcher
from dataclasses import dataclass

_requests_today = 0
_user_requests: Dict[int, int] = {}
_current_day = datetime.datetime.now().day


async def check_user_requests():
    """Check the user requests and execute day resets"""
    global _current_day
    current_day = datetime.datetime.now().day
    if _current_day != current_day:
        _current_day = current_day
        global _user_requests
        global _requests_today
        _user_requests = {}
        _requests_today = 0


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


async def process_message_idol_call(bot, message, content):
    """Complex operations for calling an idol."""
    person_comparisons: List[Comparison] = await search_for_obj(
        content, persons=True, split_name=True, return_similarity=True
    )
    group_comparisons: List[Comparison] = await search_for_obj(
        content, persons=False, split_name=True, return_similarity=True
    )

    person_comparisons.sort(key=lambda comp: comp.similarity, reverse=True)
    group_comparisons.sort(key=lambda comp: comp.similarity, reverse=True)

    obj_pool: List[Union[Person, Group]] = []
    if not (person_comparisons or group_comparisons):
        return  # no results
    elif person_comparisons and not group_comparisons:
        # add comps based on highest similarity
        _max_comps: Optional[List[Comparison]] = []
        for person_comp in person_comparisons:
            if not _max_comps or person_comp.similarity == _max_comps[0].similarity:
                _max_comps.append(person_comp)
                continue

        obj_pool += [comp.obj for comp in _max_comps]
    elif len(person_comparisons) > 1 and not group_comparisons:
        obj_pool += [comp.obj for comp in person_comparisons]
    elif person_comparisons and group_comparisons:
        # both persons and groups found in a message.
        for group_comp, person_comp in zip(group_comparisons, person_comparisons):
            group = group_comp.obj
            person = person_comp.obj
            if await person_in_group(person, group):
                obj_pool.append(person)
    elif len(group_comparisons) >= 1:
        # groups with no specified persons.
        obj_pool += [group_comp.obj for group_comp in group_comparisons]
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
        user_request = _user_requests.get(user.id)
        if user_request and user_request > get_keys().post_limit:
            return await send_message(
                key="become_a_patron_limited",
                channel=message.channel,
                user=user,
                delete_after=60,
            )

    try:
        media_url = await get_media_from_pool(obj_pool)
        if not media_url:
            return
    except IreneAPIWrapper.exceptions.APIError as e:
        return await bot.handle_api_error(message, e)
    try:
        await message.channel.send(media_url)

        current_score = _user_requests.get(user.id)
        _user_requests[user.id] = 1 if not current_score else current_score + 1

        global _requests_today
        if _requests_today % 5 == 0:
            await check_user_requests()
        _requests_today += 1

    except Exception as e:
        logger.error(f"Failed to send photo to channel ID: {message.channel.id} - {e}")


async def idol_send_on_message(bot, message: disnake.Message, prefixes: List):
    """Detect an idol call and send media."""
    content = await validate_message_idol_call(bot, message, prefixes)
    if not content:
        return
    loop = asyncio.get_event_loop()
    coro = process_message_idol_call(bot, message, content)
    future = asyncio.run_coroutine_threadsafe(coro, loop)


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
    item_type = inter.filled_options["item_type"]
    if item_type == "person":
        persons = await auto_complete_person(inter, user_input)
        return persons[:24]
    elif item_type == "group":
        groups = await auto_complete_group(inter, user_input)
        return groups[:24]
    else:
        raise RuntimeError(
            "item_type returned something other than 'person' or 'group'"
        )


async def auto_complete_person(inter: AppCmdInter, user_input: str) -> List[str]:
    return [
        f"{person.id}) {str(person.name)}"
        for person in await Person.get_all()
        if user_input.lower() in str(person.name).lower()
    ][:24]


async def auto_complete_group(inter: AppCmdInter, user_input: str) -> List[str]:
    return [
        f"{group.id}) {group.name}"
        for group in await Group.get_all()
        if user_input.lower() in group.name.lower()
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


async def search_for_obj(
    search_name, persons=True, split_name=False, return_similarity=False
) -> Union[List[Person], List[Group], List[Comparison]]:
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

    :returns: Union[List[:ref:`Person`], List[:ref:`Group`]]
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
                await search_distance(sub_name, alias.lower())
                >= similarity_required
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
                await search_distance(sub_name, str(obj).lower())
                >= similarity_required
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
                        await search_distance(
                            sub_name, aff.stage_name.lower()
                        )
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
        _search_distance_dict(_distance_cache, search_word, target_word)
        or _search_distance_dict(_distance_cache, target_word, search_word)
        or await _get_string_distance(search_word, target_word)
    )


def _search_distance_dict(dictionary, key_word, compared_word):
    """Search the distance dictionary for saved ratios."""
    cache = dictionary.get(key_word)
    if cache:
        similarity = cache.get(compared_word)
        if similarity:
            return similarity


async def _get_string_distance(search_word: str, target_word: str):
    """Get the similarity of one string to another string."""
    similarity = SequenceMatcher(a=search_word, b=target_word).ratio()
    if _distance_cache.get(search_word):
        _distance_cache[search_word][target_word] = similarity
    else:
        _distance_cache[search_word] = {target_word: similarity}
    return similarity


async def process_call(
    item_type, item_id, user_id, ctx=None, inter=None, allowed_mentions=None
):
    user = await User.get(user_id)
    if item_type == "group":
        group = await Group.get(item_id)
        medias: List[Media] = await Media.get_all(group.affiliations)
    else:
        person = await Person.get(item_id)
        medias: List[Media] = await Media.get_all(person.affiliations)

    if not medias:
        return await send_message(
            key="no_results",
            user=user,
            ctx=ctx,
            inter=inter,
            allowed_mentions=allowed_mentions,
        )

    await send_message(
        msg=(random.choice(medias)).source.url,
        user=user,
        ctx=ctx,
        inter=inter,
        allowed_mentions=allowed_mentions,
    )


async def process_card(
    item_type, item_id, user_id, ctx=None, inter=None, allowed_mentions=None
):
    """Process a person/group card."""
    user = await User.get(user_id)
    obj: Optional[Union[Person, Group]] = (
        await Group.get(item_id)
        if item_type.lower() == "group"
        else await Person.get(item_id)
    )
    if not obj:
        return await send_message(user=user, key="no_results", ctx=ctx, inter=inter)

    card_data = await obj.get_card(markdown=True, extra=True)
    avatar = None if not obj.display else obj.display.avatar
    banner = None if not obj.display else obj.display.banner
    embed = await get_card_embed(
        card_info=card_data, avatar=avatar, banner=banner, title=str(obj)
    )
    await send_message(user=user, ctx=ctx, inter=inter, embed=embed)


async def get_card_embed(card_info, avatar, banner, title):
    avatar = None if not avatar else avatar.url
    banner = None if not banner else banner.url
    embed = disnake.Embed(
        color=disnake.Color.brand_green(), title=title, description="\n".join(card_info)
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
    user = await User.get(user_id=user_id)
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
    )


_distance_cache: Dict[str, Dict[str, float]] = dict()
