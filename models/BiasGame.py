import asyncio
from typing import List, Optional

import disnake.ext.commands
from IreneAPIWrapper.models import (
    User,
    Person,
    BiasGame as BiasGameModel,
)
from . import Game, Bracket, PvP


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
        self.gender = gender
        self._input_size = bracket_size
        self.bracket: Optional[Bracket] = None
        self._images_generated: List[PvP] = []

        self._pool = None

    async def start(self):
        await self._generate_pool()
        if await self._generate_bracket() is False:
            return

        while not self.is_complete:
            await self._generate_images()
            await self._process_rounds()

    async def _generate_images(self):
        for pvp in await self.bracket.get_known_pvps():
            asyncio.create_task(self._generate_image(pvp))

    async def _generate_image(self, pvp):
        if pvp in self._images_generated:
            return
        if pvp.img_url:
            self._images_generated.append(pvp)
            return

        pvp.img_url = await BiasGameModel.generate_pvp(
            first_image_url=pvp.player_one.display.avatar.url,
            second_image_url=pvp.player_two.display.avatar.url,
        )

        self._images_generated.append(pvp)

    async def _generate_bracket(self):
        self.bracket = Bracket(self._input_size)
        if not await self.bracket.select_from_pool(self._pool):
            await self.send_message(key="biasgame_not_enough")
            return False  # necessary

    async def _generate_pool(self):
        self._pool = []

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
                await asyncio.sleep(2)

        if await self.bracket.next_round():  # game ends
            await self._add_final_winner()
            return await self.send_results()

    async def _add_final_winner(self):
        if self.bracket.final_winner:
            await BiasGameModel.upsert_win(
                self.host_user.id, self.bracket.final_winner.id
            )

    async def generate_question(self, pvp: PvP):
        while not pvp.img_url:
            await asyncio.sleep(1.5)
        await self.send_message(msg=pvp.img_url, view=PersonViews(pvp, self.host_user))

    async def send_results(self):
        bracket_img_url = await BiasGameModel.generate_bracket(self.bracket.get_dict())
        await self.send_message(msg=bracket_img_url)
        self._complete = True


class PersonViews(disnake.ui.View):
    def __init__(self, pvp, host_user):
        super(PersonViews, self).__init__(timeout=None)
        self.pvp = pvp
        self.first_person: Person = pvp.player_one
        self.second_person: Person = pvp.player_two

        self.host_user = host_user

        # default labels
        fp_label = str(self.first_person.name)
        sp_label = str(self.second_person.name)

        if self.first_person.affiliations:
            fp_aff = self.first_person.affiliations[0]
            fp_label = f"{fp_aff.stage_name} from {fp_aff.group.name}"
        if self.second_person.affiliations:
            sp_aff = self.second_person.affiliations[0]
            sp_label = f"{sp_aff.stage_name} from {sp_aff.group.name}"

        left_button = Button(
            label=fp_label, person=self.first_person, pvp=pvp, host_user=self.host_user
        )
        right_button = Button(
            label=sp_label, person=self.second_person, pvp=pvp, host_user=self.host_user
        )
        self.add_item(left_button)
        self.add_item(right_button)


class Button(disnake.ui.Button):
    def __init__(self, label, person, pvp, host_user):
        self.done = False
        self.pvp = pvp
        self.person = person
        self.host_user = host_user
        super(Button, self).__init__(label=label, style=disnake.ButtonStyle.blurple)

    async def callback(self, interaction: disnake.MessageInteraction, /):
        if interaction.user.id != self.host_user.id:
            return

        self.done = True
        self.pvp.winner = self.person
        await interaction.message.delete()
