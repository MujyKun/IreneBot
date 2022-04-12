from disnake import ApplicationCommandInteraction as AppCmdInter, OptionType, OptionChoice, Option
from IreneAPIWrapper.models import Person, Group
from typing import List, Literal

"""
type_options = Option(
    name="Type",
    description="The type of object.",
    type=OptionType.string,
    required=True,
    autocomplete=True,
    choices=[
        OptionChoice("Person", 1), OptionChoice("Group", 2)
    ],
    min_value=1,
    max_value=2
)
"""


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