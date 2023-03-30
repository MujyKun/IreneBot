import disnake
from IreneAPIWrapper.models.tiktokaccount import TikTokAccount

from models import Bot
from disnake.ext import commands, tasks
from disnake import ApplicationCommandInteraction as AppCmdInter
from . import helper
from typing import List, Optional, Dict


class TikTokCog(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.allowed_mentions = disnake.AllowedMentions(everyone=False, roles=False)
        self._loop_running = False

    def cog_unload(self) -> None:
        self.tiktok_updates.stop()

    @commands.group(
        name="tiktok", description="Commands related to TikTok Subscriptions."
    )
    @commands.guild_only()
    @commands.has_guild_permissions(**{"manage_messages": True})
    async def regular_tiktok(self, ctx: commands.Context):
        ...

    @regular_tiktok.command(name="add", description="Subscribe to a TikTok account.")
    async def regular_add(
        self,
        ctx: commands.Context,
        tiktok_username: str,
        channel: Optional[disnake.TextChannel] = None,
        role: Optional[disnake.Role] = None,
    ):
        await helper.process_add(
            ctx=ctx,
            channel_to_notify=channel if channel else ctx.channel,
            guild=ctx.guild,
            user_id=ctx.author.id,
            tiktok_username=tiktok_username,
            role_id=role.id if role else None,
            allowed_mentions=self.allowed_mentions,
        )

    @regular_tiktok.command(
        name="list", description="List the TikTok accounts subscribed to."
    )
    async def regular_list(self, ctx: commands.Context):
        await ctx.send(await helper.get_subbed_msg(ctx.channel.id, ctx.guild, ctx.author.id))

    @regular_tiktok.command(
        name="remove", description="Unsubscribe from a TikTok account."
    )
    async def regular_remove(
        self,
        ctx: commands.Context,
        tiktok_username: str,
        channel: Optional[disnake.TextChannel] = None,
    ):
        await helper.process_remove(
            ctx=ctx,
            channel_id=channel if channel else ctx.channel,
            user_id=ctx.author.id,
            tiktok_username=tiktok_username,
            allowed_mentions=self.allowed_mentions,
        )

    # ==============
    # SLASH COMMANDS
    # ==============

    @commands.slash_command(
        name="tiktok", description="Commands related to TikTok Subscriptions."
    )
    @commands.has_guild_permissions(**{"manage_messages": True})
    @commands.guild_only()
    async def tiktok(self, inter: AppCmdInter):
        ...

    @tiktok.sub_command(name="add", description="Add a TikTok channel to subscribe to.")
    async def add(
        self,
        inter: AppCmdInter,
        tiktok_username: str,
        channel: Optional[disnake.TextChannel] = None,
        role: Optional[disnake.Role] = None,
    ):
        await helper.process_add(
            inter=inter,
            channel_to_notify=channel if channel else inter.channel,
            user_id=inter.user.id,
            guild=inter.guild,
            tiktok_username=tiktok_username,
            role_id=role.id if role else None,
            allowed_mentions=self.allowed_mentions,
        )

    @tiktok.sub_command(name="remove", description="Unsubscribe from a TikTok channel.")
    async def remove(
        self,
        inter: AppCmdInter,
        tiktok_username: str = commands.Param(
            autocomplete=helper.auto_complete_type_subbed_channel
        ),
        channel: Optional[disnake.TextChannel] = None,
    ):
        await helper.process_remove(
            inter=inter,
            channel_id=channel if channel else inter.channel,
            user_id=inter.user.id,
            tiktok_username=tiktok_username,
            allowed_mentions=self.allowed_mentions,
        )

    @tiktok.sub_command(
        name="list",
        description="List all TikTok channels being followed in this channel.",
    )
    async def list(self, inter: AppCmdInter):
        await inter.send(await helper.get_subbed_msg(inter.channel_id, inter.guild, inter.user.id))

    @tasks.loop(minutes=5, reconnect=True)
    async def tiktok_updates(self):
        """
        Send updates to discord channels when a TikTok account gets a new post.
        """
        try:
            if not self.bot.api.connected or self._loop_running:
                return

            self._loop_running = True

            # removes accounts that have no channels following
            accounts = [acc for acc in await TikTokAccount.get_all() if acc]

            if not accounts:
                return

            latest_vid_key = "latest_video_id"
            for account in accounts:
                try:
                    video_id = await account.get_latest_video_id()
                    previous_video_id = getattr(account, latest_vid_key, None)
                    setattr(account, latest_vid_key, video_id or previous_video_id or -1)
                    if not previous_video_id or \
                            video_id == previous_video_id or \
                            video_id is None:
                        continue

                    channels_needing_posts = [channel for channel in account]
                    success_channels = await helper.send_tiktok_notifications(
                        bot=self.bot,
                        channels=channels_needing_posts,
                        tiktok_account=account,
                        video_id=video_id
                    )
                except Exception as e:
                    self.bot.logger.error(f"TikTok Notification (Iter) Error -> {e}")
                    print(f"{e}")

            self._loop_running = False
        except Exception as e:
            self.bot.logger.error(f"TikTok Notification Error -> {e}")
            print(f"{e}")
            self._loop_running = False


def setup(bot: Bot):
    cog = TikTokCog(bot)
    bot.add_cog(cog)
    cog.tiktok_updates.start()
