import disnake
from disnake.ext import commands
from typing import Union, List


class SingleEmbedPages(disnake.ui.View):
    def __init__(
        self, author: Union[disnake.User, disnake.Member], embeds: List[disnake.Embed]
    ):
        super().__init__(timeout=None)
        self.embeds = embeds
        self.embeds[0].set_author(name=author.display_name, icon_url=author.avatar.url)
        self.embeds[0].set_footer(text=f"Page 1 of 1")


class ShortEmbedPages(disnake.ui.View):
    def __init__(
        self,
        author: Union[disnake.User, disnake.Member],
        embeds: List[disnake.Embed],
        timeout: int = 60,
        only_author: bool = True,
    ):
        super().__init__(timeout=timeout)
        self.author = author
        self.embeds = embeds
        self.only_author = only_author
        self.current_embed_idx = 0
        self.prev_page.disabled = True

        for i, embed in enumerate(self.embeds):
            embed.set_author(
                name=self.author.display_name, icon_url=self.author.avatar.url
            )
            embed.set_footer(text=f"Page {i + 1} of {len(self.embeds)}")

    async def interaction_check(self, interaction: disnake.MessageInteraction) -> bool:
        if not self.only_author:
            return True
        if interaction.author.id != self.author.id:
            await interaction.response.send_message(
                "You cannot press the buttons on this embed since you are not the author",
                ephemeral=True,
            )
        return interaction.author.id == self.author.id

    async def on_timeout(self) -> None:
        print("Timed out")
        self.prev_page.disabled = True
        self.next_page.disabled = True

    @disnake.ui.button(label="Prev", style=disnake.ButtonStyle.grey)
    async def prev_page(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        self.current_embed_idx -= 1
        embed = self.embeds[self.current_embed_idx]

        self.next_page.disabled = False
        if self.current_embed_idx == 0:
            self.prev_page.disabled = True

        await interaction.response.edit_message(embed=embed, view=self)

    @disnake.ui.button(label="Next", style=disnake.ButtonStyle.grey)
    async def next_page(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        self.current_embed_idx += 1
        embed = self.embeds[self.current_embed_idx]

        self.prev_page.disabled = False
        if self.current_embed_idx == len(self.embeds) - 1:
            self.next_page.disabled = True

        await interaction.response.edit_message(embed=embed, view=self)


class LongEmbedPages(disnake.ui.View):
    def __init__(
        self,
        author: Union[disnake.User, disnake.Member],
        embeds: List[disnake.Embed],
        timeout: int = 60,
        only_author: bool = True,
    ):
        super().__init__(timeout=timeout)
        self.author = author
        self.embeds = embeds
        self.only_author = only_author
        self.current_embed_idx = 0
        self.prev_page.disabled = True
        self.first_page.disabled = True

        for i, embed in enumerate(self.embeds):
            embed.set_author(
                name=self.author.display_name, icon_url=self.author.avatar.url
            )
            embed.set_footer(text=f"Page {i + 1} of {len(self.embeds)}")

    async def interaction_check(self, interaction: disnake.MessageInteraction) -> bool:
        if not self.only_author:
            return True
        if interaction.author.id != self.author.id:
            await interaction.response.send_message(
                "You cannot press the buttons on this embed since you are not the author",
                ephemeral=True,
            )
        return interaction.author.id == self.author.id

    async def on_timeout(self) -> None:
        print("Timed Out.")
        self.first_page.disabled = True
        self.prev_page.disabled = True
        self.next_page.disabled = True
        self.last_page.disabled = True

    @disnake.ui.button(label="First", style=disnake.ButtonStyle.grey)
    async def first_page(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        self.current_embed_idx = 0
        embed = self.embeds[self.current_embed_idx]

        self.last_page.disabled = False
        self.next_page.disabled = False
        if self.current_embed_idx == 0:
            self.prev_page.disabled = True
            self.first_page.disabled = True

        await interaction.response.edit_message(embed=embed, view=self)

    @disnake.ui.button(label="Prev", style=disnake.ButtonStyle.grey)
    async def prev_page(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        self.current_embed_idx -= 1
        embed = self.embeds[self.current_embed_idx]

        self.last_page.disabled = False
        self.next_page.disabled = False
        if self.current_embed_idx == 0:
            self.prev_page.disabled = True
            self.first_page.disabled = True

        await interaction.response.edit_message(embed=embed, view=self)

    @disnake.ui.button(label="Next", style=disnake.ButtonStyle.grey)
    async def next_page(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        self.current_embed_idx += 1
        embed = self.embeds[self.current_embed_idx]

        self.first_page.disabled = False
        self.prev_page.disabled = False
        if self.current_embed_idx == len(self.embeds) - 1:
            self.next_page.disabled = True
            self.last_page.disabled = True

        await interaction.response.edit_message(embed=embed, view=self)

    @disnake.ui.button(label="Last", style=disnake.ButtonStyle.grey)
    async def last_page(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        self.current_embed_idx = len(self.embeds) - 1
        embed = self.embeds[self.current_embed_idx]

        self.first_page.disabled = False
        self.prev_page.disabled = False
        if self.current_embed_idx == len(self.embeds) - 1:
            self.next_page.disabled = True
            self.last_page.disabled = True

        await interaction.response.edit_message(embed=embed, view=self)


async def create_embed_paged_view(
    author: Union[disnake.User, disnake.Member],
    embeds: List[disnake.Embed],
    timeout: int = 60,
    only_author: bool = True,
) -> Union[SingleEmbedPages, ShortEmbedPages, LongEmbedPages]:
    if len(embeds) == 1:
        return SingleEmbedPages(author, embeds)
    elif len(embeds) < 5:
        return ShortEmbedPages(author, embeds, timeout, only_author)
    else:
        return LongEmbedPages(author, embeds, timeout, only_author)
