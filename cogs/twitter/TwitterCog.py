import disnake
from IreneAPIWrapper.models import TwitterAccount, Tweet

from models import Bot
from disnake.ext import commands, tasks
from disnake import ApplicationCommandInteraction as AppCmdInter
from . import helper
from typing import List, Optional


class TwitterCog(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.allowed_mentions = disnake.AllowedMentions(everyone=False, roles=False)
        self._loop_running = False

    def cog_unload(self) -> None:
        self.twitter_updates.stop()

    @commands.group(
        name="twitter", description="Commands related to Twitter Subscriptions."
    )
    @commands.guild_only()
    @commands.has_guild_permissions(**{"manage_messages": True})
    async def regular_twitter(self, ctx):
        ...

    @regular_twitter.command(name="add", description="Subscribe to a Twitter account.")
    async def regular_add(
        self,
        ctx,
        twitter_username: str,
        channel: Optional[disnake.TextChannel],
        role: Optional[disnake.Role] = None,
    ):
        await helper.process_add(
            ctx=ctx,
            channel_to_notify=channel if channel else ctx.channel,
            user_id=ctx.author.id,
            guild=ctx.guild,
            twitter_username=twitter_username,
            role_id=role.id if role else None,
            allowed_mentions=self.allowed_mentions,
        )

    @regular_twitter.command(
        name="list", description="List the Twitter accounts subscribed to."
    )
    async def regular_list(self, ctx: commands.Context):
        await ctx.send(await helper.get_subbed_msg(ctx.guild, ctx.author.id))

    @regular_twitter.command(
        name="remove", description="Unsubscribe from a Twitter account."
    )
    async def regular_remove(
        self,
        ctx: commands.Context,
        twitter_username: str,
        channel: Optional[disnake.TextChannel] = None,
    ):
        await helper.process_remove(
            ctx=ctx,
            channel_to_notify=channel if channel else ctx.channel,
            user_id=ctx.author.id,
            twitter_username=twitter_username,
            allowed_mentions=self.allowed_mentions,
        )

    # ==============
    # SLASH COMMANDS
    # ==============
    @commands.slash_command(
        name="twitter", description="Commands related to Twitter Subscriptions."
    )
    @commands.has_guild_permissions(**{"manage_messages": True})
    @commands.guild_only()
    async def twitter(self, inter: AppCmdInter):
        ...

    @twitter.sub_command(name="add", description="Subscribe to a Twitter account.")
    async def add(
        self,
        inter: AppCmdInter,
        twitter_username: str,
        channel: Optional[disnake.TextChannel],
        role: Optional[disnake.Role] = None,
    ):
        await helper.process_add(
            inter=inter,
            channel_to_notify=channel if channel else inter.channel,
            user_id=inter.user.id,
            guild=inter.guild,
            twitter_username=twitter_username,
            role_id=role.id if role else None,
            allowed_mentions=self.allowed_mentions,
        )

    @twitter.sub_command(
        name="list", description="List the Twitter accounts subscribed to."
    )
    async def list(self, inter: AppCmdInter):
        await inter.send(await helper.get_subbed_msg(inter.guild, inter.user.id))

    @twitter.sub_command(
        name="remove", description="Unsubscribe from a Twitter account."
    )
    async def remove(
        self,
        inter: AppCmdInter,
        twitter_username: str = commands.Param(
            autocomplete=helper.auto_complete_type_subbed_channel
        ),
        channel: Optional[disnake.TextChannel] = None,
    ):
        await helper.process_remove(
            inter=inter,
            channel_to_notify=channel if channel else inter.channel,
            user_id=inter.user.id,
            twitter_username=twitter_username,
            allowed_mentions=self.allowed_mentions,
        )

    @tasks.loop(minutes=1, seconds=45, reconnect=True)
    async def twitter_updates(self):
        """
        Send updates to discord channels when a Twitter account posts.
        """
        try:
            if not self.bot.api.connected or self._loop_running:
                return

            self._loop_running = True

            accounts = list(await TwitterAccount.get_all())
            for account in accounts:
                try:
                    if not account:  # checks if any channels are following the account.
                        continue

                    timeline = await account.fetch_timeline()
                    new_tweets: List[Tweet] = timeline.new_tweets
                    timeline.new_tweets = []  # reset the new tweets.

                    if not new_tweets:
                        continue

                    await helper.send_twitter_notifications(
                        self.bot, account, new_tweets
                    )
                except Exception as e:
                    self.bot.logger.error(f"Twitter Notification (Iter) Error -> {e}")
                    print(f"{e}")

            self._loop_running = False
        except Exception as e:
            self.bot.logger.error(f"Twitter Notification Error -> {e}")
            print(f"{e}")


def setup(bot: Bot):
    cog = TwitterCog(bot)
    bot.add_cog(cog)
    cog.twitter_updates.start()
