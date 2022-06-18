import random

from disnake import ApplicationCommandInteraction as AppCmdInter
from IreneAPIWrapper.models import Person, Group
from typing import List, Union, Optional, Tuple, Dict


async def auto_complete_type(inter: AppCmdInter, user_input: str) -> List[str]:
    item_type = inter.filled_options['item_type']
    if item_type == "person":
        return [f"{person.id}) {str(person.name)}" for person in await Person.get_all()
                if user_input.lower() in str(person.name).lower()]
    elif item_type == "group":
        return [f"{group.id}) {group.name}" for group in await Group.get_all()
                if user_input.lower() in group.name.lower()]
    else:
        raise RuntimeError("item_type returned something other than 'person' or 'group'")


async def get_call_count_leaderboard(objects: Union[List[Person], List[Group]]) -> Optional[List[Tuple[Union[Person, Group], int]]]:
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
        group_called_amounts_sorted = sorted(group_called_amounts, key=lambda x: group_called_amounts[x],
                                             reverse=True)
        for obj in group_called_amounts_sorted:
            group_called_amounts_final.append((obj, group_called_amounts[obj]))
        return group_called_amounts_final
    else:
        raise NotImplementedError(f"An entity aside from a person or object has not been implemented.")


async def search_for_obj_by_alias(search_name, persons=True) -> Union[List[Person], List[Group]]:
    """
    Check if a name matches with an alias or a Person/Group's full name.

    :param search_name: str
        The name to search for.
    :param persons: bool
        Whether to search for Persons [Otherwise will search for Groups]

    :returns: Union[List[:ref:`Person`], List[:ref:`Group`]]
        A list of persons or groups that match the search filter.
    """
    if persons:
        persons: List[Person] = await Person.get_all()
        filtered = [item for item in persons if await _filter_by_name(item, search_name)]
    else:
        groups: List[Group] = await Group.get_all()
        filtered = [item for item in groups if await _filter_by_name(item, search_name)]
    return filtered


async def _filter_by_name(obj: Union[Person, Group], name: str):
    """
    Uses levenshtein distance against person/group aliases.
    Any aliases/names with an 75% or greater similarity will count as a result.

    :returns: bool
        Whether the Person or Group object is included in the filter.

    """
    aliases = await obj.get_aliases_as_strings()
    name = name.lower()
    similarity_required = 0.75

    # check for matching aliases
    if any([levenshtein_distance(name, alias.lower()) >= similarity_required for alias in aliases]):
        return True

    # check for matching group names or person full names.
    if levenshtein_distance(name, str(obj).lower()) >= similarity_required:
        return True

    # check for matching stage names
    if isinstance(obj, Person):
        for aff in obj.affiliations:
            if levenshtein_distance(name, aff.stage_name.lower()) >= similarity_required:
                return True

    return False


def get_random_color():
    """Retrieves a random hex color."""
    r = lambda: random.randint(0, 255)
    return int(('%02X%02X%02X' % (r(), r(), r())), 16)  # must be specified to base 16 since 0x is not present


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
            edits[(i, j)] = min(edits[(i - 1, j)] + 1,
                                edits[(i, j - 1)] + 1,
                                edits[(i - 1, j - 1)] + edit_cost)

    min_edits_needed = edits[(max_i, max_j)]
    return 1 - min_edits_needed / max(max_i, max_j)
