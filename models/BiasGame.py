import asyncio
from typing import List, Optional

import disnake.ext.commands
from IreneAPIWrapper.models import (
    User,
    Person,
    BiasGame as BiasGameModel,
)
from . import Game, add_to_cache, Bracket, PvP


class BiasGame(Game):
    def __init__(
        self,
        bot,
        bracket_size,
        gender,
        user: User,
        ctx=None,
        inter=None,
    ):
        super(BiasGame, self).__init__(bot, user, ctx=ctx, inter=inter)
        add_to_cache(self)
        self.gender = gender
        self._input_size = bracket_size
        self.bracket: Optional[Bracket] = None

        self._pool = None

    async def start(self):
        await self._generate_pool()
        if await self._generate_bracket() is False:
            return

        await self._process_rounds()

    async def _generate_bracket(self):
        bracket = Bracket(self._input_size)
        if not await bracket.select_from_pool(self._pool):
            await self.send_message(key="biasgame_not_enough")
            return False  # necessary
        self.bracket = bracket

    async def _generate_pool(self):
        self._pool = []

        test_person = await Person.get(1)
        self._pool = [test_person for i in range(1, 16)]
        return

        persons: List[Person] = list(await Person.get_all())
        for person in persons:
            if self.gender != "mixed":
                if person.gender.lower() != self.gender[0]:
                    continue

            if not person.display:
                continue

            if not person.display.avatar:
                continue

            if not person.display.avatar.url:
                continue

            self._pool.append(person)

    async def _process_rounds(self):
        for pvp in self.bracket.rounds[self.bracket.max_round]:
            if pvp.is_complete:
                continue

            await self.generate_question(pvp)
            while not pvp.winner:
                await asyncio.sleep(1)

        if await self.bracket.next_round():  # game ends
            await self._add_final_winner()
            return await self.send_results()
        await self._process_rounds()  # recursive func

    async def _add_final_winner(self):
        if self.bracket.final_winner:
            await BiasGameModel.upsert_win(
                self.host_user.id, self.bracket.final_winner.id
            )

    async def generate_question(self, pvp: PvP):
        person_one: Person = pvp.player_one
        person_two: Person = pvp.player_two
        first_file_name = person_one.display.avatar.url[
            person_one.display.avatar.url.find(str(pvp.player_one.id)) : :
        ]
        second_file_name = person_two.display.avatar.url[
            person_two.display.avatar.url.find(str(pvp.player_two.id)) : :
        ]
        img_url = await BiasGameModel.generate_pvp(
            first_file_name=first_file_name, second_file_name=second_file_name
        )
        await self.send_message(msg=img_url, view=PersonViews(pvp))

    async def send_results(self):
        bracket_img_url = await BiasGameModel.generate_bracket(self.bracket.get_dict())
        await self.send_message(msg=bracket_img_url)


class PersonViews(disnake.ui.View):
    def __init__(self, pvp):
        super(PersonViews, self).__init__(timeout=None)
        self.pvp = pvp
        self.first_person: Person = pvp.player_one
        self.second_person: Person = pvp.player_two

        fp_label = str(self.first_person.name)
        sp_label = str(self.second_person.name)
        left_button = Button(label=fp_label, person=self.first_person, pvp=pvp)
        right_button = Button(label=sp_label, person=self.second_person, pvp=pvp)
        self.add_item(left_button)
        self.add_item(right_button)


class Button(disnake.ui.Button):
    def __init__(self, label, person, pvp):
        self.done = False
        self.pvp = pvp
        self.person = person
        super(Button, self).__init__(label=label, style=disnake.ButtonStyle.blurple)

    async def callback(self, interaction: disnake.MessageInteraction, /):
        self.done = True
        self.pvp.winner = self.person
        await interaction.message.delete()
