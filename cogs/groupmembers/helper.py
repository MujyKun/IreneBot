import datetime
import random

import IreneAPIWrapper.exceptions
import disnake
from disnake import ApplicationCommandInteraction as AppCmdInter
from IreneAPIWrapper.models import Person, Group, Media, User
from typing import List, Union, Optional, Tuple, Dict
from util import logger
from keys import get_keys
from ..helper import send_message

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


async def idol_send_on_message(bot, message: disnake.Message, prefixes: List):
    """Detect an idol call and send media."""
    if not hasattr(message, "guild"):
        return

    content_replaced = False
    content = message.content  # we do not want to overwrite the message content.

    if not content:
        return

    for prefix in prefixes:
        if message.content.startswith(prefix):
            content = content.replace(prefix, "", 1)
            content_replaced = True
            break

    if not content_replaced:
        return

    person_comparisons: List[Comparison] = await search_for_obj(content, persons=True, split_name=True,
                                                                return_similarity=True)
    group_comparisons: List[Comparison] = await search_for_obj(content, persons=False, split_name=True,
                                                               return_similarity=True)

    obj_pool: List[Union[Person, Group]] = []
    if not (person_comparisons or group_comparisons):
        return  # no results
    elif len(person_comparisons) >= 1 and not group_comparisons:
        # people with no group. -> Add them all to pool instead of only highest similarity.
        obj_pool.append(person_comparisons[0].obj)
    elif len(person_comparisons) > 1 and not group_comparisons:
        obj_pool += [comp.obj for comp in person_comparisons]
    elif len(person_comparisons) == 1 and len(group_comparisons) == 1:
        # only a person and a group
        person = person_comparisons[0].obj
        group = group_comparisons[0].obj
        obj_pool.append(person)
        if not await person_in_group(person, group):
            # person is not in group.
            obj_pool.append(group)
    elif len(person_comparisons) >= 1 and len(group_comparisons) >= 1:
        # several persons and groups found in a message.
        for group_comp in group_comparisons:
            has_person = False
            group = group_comp.obj
            for person_comp in person_comparisons:
                person = person_comp.obj
                in_group = await person_in_group(person, group)
                if in_group:
                    has_person = True
                    obj_pool.append(person)
            if not has_person:
                # add the group to the pool. if there is no person found for the group.
                obj_pool.append(group)
    elif len(group_comparisons) >= 1:
        # groups with no people
        obj_pool += [group_comp.obj for group_comp in group_comparisons]
    else:
        raise NotImplementedError()

    obj_pool = list(dict.fromkeys(obj_pool))  # remove duplicates
    if not obj_pool:
        return

    random_obj_choice = random.choice(obj_pool)

    user = await User.get(message.author.id)
    if not user:
        await User.insert(message.author.id)
        user = await User.get(message.author.id)
    # if not user.is_patron:
    #     user_request = _user_requests.get(user.id)
    #     if user_request and user_request > get_keys().post_limit:
    #         return await send_message(key="become_a_patron_limited", channel=message.channel, user=user,
    #                                   delete_after=60)

    try:
        media = await Media.get_random(random_obj_choice.id,
                                       person=isinstance(random_obj_choice, Person),
                                       group=isinstance(random_obj_choice, Group))
        if media:
            media_url = await media.fetch_image_host_url()
        else:
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


async def person_in_group(person, group):
    return any([person_aff == group_aff for person_aff in person.affiliations for group_aff in group.affiliations])


async def auto_complete_type(inter: AppCmdInter, user_input: str) -> List[str]:
    item_type = inter.filled_options["item_type"]
    if item_type == "person":
        return await auto_complete_person(inter, user_input)
    elif item_type == "group":
        return await auto_complete_group(inter, user_input)
    else:
        raise RuntimeError(
            "item_type returned something other than 'person' or 'group'"
        )


async def auto_complete_person(inter: AppCmdInter, user_input: str) -> List[str]:
    return [
        f"{person.id}) {str(person.name)}"
        for person in await Person.get_all()
        if user_input.lower() in str(person.name).lower()
    ]


async def auto_complete_group(inter: AppCmdInter, user_input: str) -> List[str]:
    return [
        f"{group.id}) {group.name}"
        for group in await Group.get_all()
        if user_input.lower() in group.name.lower()
    ]


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


class Comparison:
    """
    Comparison a source object's search word with its target word using levenshtein distance.
    """
    def __init__(self, obj: Union[Person, Group], search_word: str, target_word: str):
        self.obj = obj
        self.search_word = search_word
        self.target_word = target_word
        self.similarity: float = self.calculate()

    def calculate(self):
        """Calculate the levenshtein distance."""
        return levenshtein_distance(self.search_word, self.target_word)

    def __float__(self):
        """Returns similarity."""
        return self.similarity

    def __eq__(self, other):
        return (self.obj == other.obj) and (self.search_word == other.search_word) and \
               (self.target_word == other.target_word)

    def __lt__(self, other):
        """Check if the similarity is less than another comparison object."""
        return self.__float__() < other.__float__()

    def __hash__(self):
        return hash(('obj', self.obj, 'search_word', self.search_word, 'target_word', self.target_word))


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
    objects: Union[List[Person], List[Group]] = await Person.get_all() if persons else await Group.get_all()
    if not return_similarity:
        filtered = [
            item for item in objects if await _filter_by_name(item, search_name, split_name=split_name,
                                                              return_similarity=return_similarity)
        ]
        return filtered
    else:
        filtered = [await _filter_by_name(item, search_name, split_name=split_name,
                                          return_similarity=return_similarity) for item in objects]
        return [comp for list_of_comps in filtered for comp in list_of_comps]


async def _filter_by_name(obj: Union[Person, Group], name: str, similarity_required=0.75, split_name=False,
                          return_similarity=True):
    """
    Uses levenshtein distance against person/group aliases.
    Any aliases/names with a default 75% or greater similarity will count as a result.

    :returns: bool
        Whether the Person or Group object is included in the filter.

    """
    if not name:
        return False

    if similarity_required < 0 or similarity_required > 100:
        similarity_required = 0.75
    elif 1 < similarity_required <= 100:
        similarity_required = similarity_required / 100  # putting as decimal between 0 and 1.

    final_results: List[Comparison] = []
    aliases = await obj.get_aliases_as_strings()
    name = name.lower()
    names = [name] if not split_name else name.split(' ') + [name]

    # check for matching aliases
    if not return_similarity:
        if any(
            [
                levenshtein_distance(sub_name, alias.lower()) >= similarity_required
                for sub_name in names for alias in aliases
            ]
        ):
            return True
    else:
        alias_comparisons = [Comparison(obj, sub_name, alias.lower()) for sub_name in names for alias in aliases]
        final_results += [comp for comp in alias_comparisons if comp.similarity >= similarity_required]

    # check for matching group names or person full names.
    if not return_similarity:
        if any([levenshtein_distance(sub_name, str(obj).lower()) >= similarity_required for sub_name in names]):
            return True
    else:
        name_comparisons = [Comparison(obj, sub_name, str(obj).lower()) for sub_name in names]
        final_results += [comp for comp in name_comparisons if comp.similarity >= similarity_required]

    # check for matching stage names
    if isinstance(obj, Person):
        for aff in obj.affiliations:
            if not return_similarity:
                if any([
                    levenshtein_distance(sub_name, aff.stage_name.lower())
                    >= similarity_required for sub_name in names]
                ):
                    return True
            else:
                aff_comparisons = [Comparison(obj, sub_name, aff.stage_name.lower()) for sub_name in names]
                final_results += [comp for comp in aff_comparisons if comp.similarity >= similarity_required]

    if return_similarity:
        # check if the object's name is in the name and do a comparison check. Only works if returning similarity.
        if str(obj).lower() in name:
            final_results.append(Comparison(obj, name, str(obj).lower()))

        final_results.sort(reverse=True)
        return list(dict.fromkeys(final_results))  # remove duplicates

    return False


def get_random_color():
    """Retrieves a random hex color."""
    r = lambda: random.randint(0, 255)
    return int(
        ("%02X%02X%02X" % (r(), r(), r())), 16
    )  # must be specified to base 16 since 0x is not present


def levenshtein_distance(search_word: str, target_word: str) -> float:
    """
    Compute levenshtein's distance and get the percentage back.

    :param search_word: str
        The word being searched for.
    :param target_word: str
        The target word to compare to.

    :returns: float
        How similar the words are to each other (Ratio from 0 to 1 where 1 is 100% similarity)
    """
    edits: Dict[Tuple[int, int], int] = {}
    max_i = len(search_word)
    max_j = len(target_word)

    if not max_i or not max_j:  # if any of the words are blank strings
        return 0

    for j in range(0, max_j + 1):
        edits[(0, j)] = j

    for i in range(0, max_i + 1):
        edits[(i, 0)] = i

    for i, i_char in enumerate(search_word, start=1):
        for j, j_char in enumerate(target_word, start=1):
            if i_char == j_char:
                edit_cost = 0

            else:
                edit_cost = 1
            edits[(i, j)] = min(
                edits[(i - 1, j)] + 1,
                edits[(i, j - 1)] + 1,
                edits[(i - 1, j - 1)] + edit_cost,
            )

    min_edits_needed = edits[(max_i, max_j)]
    return 1 - min_edits_needed / max(max_i, max_j)
