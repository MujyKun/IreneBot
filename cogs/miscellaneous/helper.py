import disnake
from disnake.ext import commands
from disnake import ApplicationCommandInteraction as AppCmdInter
from random import choice, randint
from re import findall


async def get_choose_answer(choices: str):
    if "|" in choices:
        possible_choices = choices.split("|")
        possible_choices = [m_choice for m_choice in possible_choices if m_choice != " "]
        possible_choices_string = str.join(", ", ["`" + my_choice + "`" for my_choice in possible_choices])
    elif "," in choices:
        possible_choices = choices.split(",")
        possible_choices = [m_choice for m_choice in possible_choices if m_choice != " "]
        possible_choices = [m_choice[1:] if m_choice.startswith(" ") else m_choice for m_choice in possible_choices]
        possible_choices_string = str.join(", ", ["`" + my_choice + "`" for my_choice in possible_choices])
    else:
        possible_choices = choices.split(" ")
        possible_choices = [m_choice.replace("_", " ") for m_choice in possible_choices if m_choice != ""]
        possible_choices_string = str.join(", ", ["`" + my_choice + "`" for my_choice in possible_choices])
    return f"**Possible Choices**: {possible_choices_string}\n" + f"**Selection**: `{choice(possible_choices)}`"

async def send_emojis_from_string(inter: AppCmdInter, emoji_content: str):
    if not emoji_content:
        await inter.send("No emote detected.", ephemeral=True)
        return
    emoji_infos = findall(r"<a?:?\w+:[0-9]{18}>", emoji_content)
    if not emoji_infos:
        await inter.send("No emote content detected. It may be a default system emote.", ephemeral=True)
        return
    emoji_urls = [disnake.PartialEmoji.from_str(emoji_info).url for emoji_info in emoji_infos]
    await inter.send("\n".join(emoji_urls))