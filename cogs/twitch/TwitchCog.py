import disnake
from IreneAPIWrapper.models.twitchaccount import TwitchAccount

from models import Bot
from disnake.ext import commands, tasks
from disnake import ApplicationCommandInteraction as AppCmdInter
from . import helper
from typing import List, Optional, Dict


class TwitchCog(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.allowed_mentions = disnake.AllowedMentions(everyone=False, roles=False)
        self._loop_running = False

    def cog_unload(self) -> None:
        self.twitch_updates.stop()

    @commands.group(
        name="twitch", description="Commands related to Twitch Subscriptions."
    )
    @commands.guild_only()
    @commands.has_guild_permissions(**{"manage_messages": True})
    async def regular_twitch(self, ctx: commands.Context):
        ...

    @regular_twitch.command(name="add", description="Subscribe to a twitch account.")
    async def regular_add(
        self,
        ctx: commands.Context,
        twitch_username: str,
        channel: Optional[disnake.TextChannel] = None,
        role: Optional[disnake.Role] = None,
    ):
        await helper.process_add(
            ctx=ctx,
            channel_to_notify=channel if channel else ctx.channel,
            guild=ctx.guild,
            user_id=ctx.author.id,
            twitch_username=twitch_username,
            role_id=role.id if role else None,
            allowed_mentions=self.allowed_mentions,
        )

    @regular_twitch.command(
        name="list", description="List the Twitch accounts subscribed to."
    )
    async def regular_list(self, ctx: commands.Context):
        await ctx.send(await helper.get_subbed_msg(ctx.guild, ctx.author.id))

    @regular_twitch.command(
        name="remove", description="Unsubscribe from a twitch account."
    )
    async def regular_remove(
        self,
        ctx: commands.Context,
        twitch_username: str,
        channel: Optional[disnake.TextChannel] = None,
    ):
        await helper.process_remove(
            ctx=ctx,
            channel_to_notify=channel if channel else ctx.channel,
            user_id=ctx.author.id,
            twitch_username=twitch_username,
            allowed_mentions=self.allowed_mentions,
        )

    # ==============
    # SLASH COMMANDS
    # ==============

    @commands.slash_command(
        name="twitch", description="Commands related to Twitch Subscriptions."
    )
    @commands.has_guild_permissions(**{"manage_messages": True})
    @commands.guild_only()
    async def twitch(self, inter: AppCmdInter):
        ...

    @twitch.sub_command(name="add", description="Add a Twitch channel to subscribe to.",
                        extras={"permissions": "Manage Messages",
                                "syntax": "/twitch add (twitch username) [text channel] [role to mention]"})
    async def add(
        self,
        inter: AppCmdInter,
        twitch_username: str,
        channel: Optional[disnake.TextChannel] = None,
        role: Optional[disnake.Role] = None,
    ):
        await helper.process_add(
            inter=inter,
            channel_to_notify=channel if channel else inter.channel,
            user_id=inter.user.id,
            guild=inter.guild,
            twitch_username=twitch_username,
            role_id=role.id if role else None,
            allowed_mentions=self.allowed_mentions,
        )

    @twitch.sub_command(name="remove", description="Unsubscribe from a Twitch channel.",
                        extras={"permissions": "Manage Messages",
                                "syntax": "/twitch remove (twitch username) [text channel]"}
                        )
    async def remove(
        self,
        inter: AppCmdInter,
        twitch_username: str = commands.Param(
            autocomplete=helper.auto_complete_type_subbed_guild
        ),
        channel: Optional[disnake.TextChannel] = None,
    ):
        await helper.process_remove(
            inter=inter,
            channel_to_notify=channel if channel else inter.channel,
            user_id=inter.user.id,
            twitch_username=twitch_username,
            allowed_mentions=self.allowed_mentions,
        )

    @twitch.sub_command(
        name="list",
        description="List all Twitch channels being followed in this guild.",
        extras={"permissions": "Manage Messages",
                "syntax": "/twitch list"}
    )
    async def list(self, inter: AppCmdInter):
        await inter.send(await helper.get_subbed_msg(inter.guild, inter.user.id))

    @tasks.loop(minutes=1, reconnect=True)
    async def twitch_updates(self):
        """
        Send updates to discord channels when a twitch channel goes live.
        """
        try:
            if not self.bot.api.connected or self._loop_running:
                return

            self._loop_running = True

            # removes accounts that have no channels following
            accounts = [acc for acc in await TwitchAccount.get_all() if acc]

            if not accounts:
                return

            _live_statuses: Dict[str, bool] = await TwitchAccount.check_live_bulk(
                accounts=accounts
            )
            twitch_accounts: List[TwitchAccount] = [
                await TwitchAccount.get(username) for username in _live_statuses.keys()
            ]

            for subscription in twitch_accounts:
                try:
                    update_posted_to_true = []
                    update_posted_to_false = []
                    if subscription.is_live:
                        already_posted = await subscription.get_posted()
                        channels_needing_posts = [
                            channel
                            for channel in subscription
                            if channel not in already_posted
                        ]

                        success_channels = await helper.send_twitch_notifications(
                            bot=self.bot,
                            channels=channels_needing_posts,
                            twitch_account=subscription,
                        )
                        update_posted_to_true = [
                            channel.id for channel in success_channels
                        ]
                    else:
                        # set all update posted to False.
                        update_posted_to_false = [
                            channel.id for channel in subscription
                        ]

                    await subscription.update_posted(update_posted_to_false, False)
                    await subscription.update_posted(update_posted_to_true, True)
                except Exception as e:
                    self.bot.logger.error(f"Twitch Notification (Iter) Error -> {e}")
                    print(f"{e}")

            self._loop_running = False
        except Exception as e:
            self.bot.logger.error(f"Twitch Notification Error -> {e}")
            print(f"{e}")
            self._loop_running = False


def setup(bot: Bot):
    cog = TwitchCog(bot)
    bot.add_cog(cog)
    cog.twitch_updates.start()
