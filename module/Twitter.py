import discord
from discord.ext import commands, tasks
from IreneUtility.Utility import Utility
from IreneUtility.util import u_logger as log
from IreneUtility.models import TwitterChannel
import asyncio


class Twitter(commands.Cog):
    def __init__(self, ex):
        self.ex: Utility = ex
        self._update_loop_busy = False

    async def cog_check(self, ctx):
        """A local check for this cog."""
        return True

    @commands.is_owner()
    @commands.command()
    async def tweet(self, ctx, *, tweet):
        """
        Tweets a status update on Twitter

        [Format: %tweet (status)]
        """
        tweet_url = await self.ex.u_twitter.update_status(tweet)
        msg = await self.ex.get_msg(ctx.author.id, "twitter", "tweet_success", ['tweet_url', tweet_url])
        await ctx.send(msg)

    @commands.is_owner()
    @commands.command()
    async def deletetweet(self, ctx, *, tweet_id):
        """
        Delete a Tweet by it's ID

        [Format: %deletetweet (id)]
        """
        await self.ex.u_twitter.delete_status(tweet_id)
        msg = await self.ex.get_msg(ctx.author.id, "twitter", "delete_success", ['tweet_id', tweet_id])
        await ctx.send(msg)

    @commands.is_owner()
    @commands.command()
    async def recenttweets(self, ctx, *, amount_of_tweets=20):
        """
        Show Most Recents Tweets

        [Format: %recenttweets (amount)]
        """
        tweets = await self.ex.u_twitter.recent_tweets(amount_of_tweets)
        msg = await self.ex.get_msg(ctx.author.id, "twitter", "recent_tweets",
                                    [['tweet_amount', amount_of_tweets], ['tweets', tweets]])
        await ctx.send(msg)

    @tasks.loop(seconds=0, minutes=10, hours=0, reconnect=True)
    async def send_photos_to_twitter(self):
        """Send Idol Photos to twitter every 10 minutes."""
        # we should wait for the bot's cache to load before going further.
        while not self.ex.irene_cache_loaded:
            await asyncio.sleep(5)

        try:
            twitter_link = await self.ex.u_twitter.upload_random_image()  # upload unique random idol photo.
            if twitter_link:
                await self.ex.cache.twitter_channel.send(twitter_link)  # post to discord.
        except Exception as e:
            log.console(f"{e} -> send_photos_to_twitter")

    # BELOW THIS POINT IS THE CODE FOR TWITTER UPDATES
    # BELOW THIS POINT IS THE CODE FOR TWITTER UPDATES
    # BELOW THIS POINT IS THE CODE FOR TWITTER UPDATES

    @commands.group(aliases=["twitter"])
    @commands.has_guild_permissions(manage_messages=True)
    async def twitterupdates(self, ctx):
        """Follow a Twitter Channel and get tweets.

        [Format: %twitterupdates (idol/group/code) (idol id/group id/twitter code)]
        """
        ...  # this command can not be used in DMs already.

    @twitterupdates.command()
    async def idol(self, ctx, idol_id: int, role: discord.Role = None):
        """Follow a Twitter channel belonging to an Idol ID If they have one."""
        role_id = None if not role else role.id
        idol = await self.ex.u_group_members.get_member(idol_id)
        if not idol:
            msg = await self.ex.get_msg(ctx, "groupmembers", "invalid_id")
            return await ctx.send(msg)

        if not isinstance(idol.twitter, TwitterChannel):
            msg = await self.ex.get_msg(ctx, "twitter", "unknown_code", ["result", "idol"])
            return await ctx.send(msg)

        await ctx.send(await self.ex.get_msg(ctx, "general", "may_take_time"))
        asyncio.create_task(self.ex.u_twitter.follow_or_unfollow(ctx, ctx.channel, idol.twitter.id, role_id=role_id))

    @twitterupdates.command()
    async def group(self, ctx, group_id: int, role: discord.Role = None):
        """Follow a Twitter channel belonging to a Group ID If they have one."""
        role_id = None if not role else role.id
        group = await self.ex.u_group_members.get_group(group_id)
        if not group:
            msg = await self.ex.get_msg(ctx, "groupmembers", "invalid_id")
            return await ctx.send(msg)

        if not isinstance(group.twitter, TwitterChannel):
            msg = await self.ex.get_msg(ctx, "twitter", "unknown_code", ["result", "group"])
            return await ctx.send(msg)

        await ctx.send(await self.ex.get_msg(ctx, "general", "may_take_time"))
        asyncio.create_task(self.ex.u_twitter.follow_or_unfollow(ctx, ctx.channel, group.twitter.id, role_id=role_id))

    @twitterupdates.command(aliases=["user", "username"])
    async def code(self, ctx, channel_user_name: str, role: discord.Role = None):
        """Follow a Twitter channel based on the channel username/code."""
        role_id = None if not role else role.id
        channel_code = channel_user_name.lower()
        twitter_obj = self.ex.cache.twitter_channels.get(channel_code)
        if not twitter_obj:
            twitter_obj = TwitterChannel(channel_code)

            # check if the code works
            if not await twitter_obj.check_channel_id():
                # code does not work
                msg = await self.ex.get_msg(ctx, "twitter", "invalid_code")
                return await ctx.send(msg)

            # add new object to the cache
            self.ex.cache.twitter_channels[twitter_obj.id] = twitter_obj

        await ctx.send(await self.ex.get_msg(ctx, "general", "may_take_time"))
        asyncio.create_task(self.ex.u_twitter.follow_or_unfollow(ctx, ctx.channel, channel_code, role_id=role_id))

    @twitterupdates.command()
    async def list(self, ctx):
        """Lists the Twitter channels currently being followed in the text channel."""
        channel_codes = []
        twitter_channels_copied = self.ex.cache.twitter_channels.copy()
        for twitter_obj in twitter_channels_copied.values():
            if twitter_obj.check_channel_followed(ctx.channel):
                channel_codes.append(twitter_obj.id)
        msg = await self.ex.get_msg(ctx, "twitter", "list_channel_codes", ["result", ", ".join(channel_codes)])
        return await ctx.send(msg)

    # notification loop
    @tasks.loop(seconds=45, minutes=0, hours=0, reconnect=True)
    async def twitter_notification_updates(self):
        """Send Twitter announcements for new tweets."""
        try:
            if not self.ex.irene_cache_loaded:
                return

            if self._update_loop_busy:
                # we do not want to mess up another iteration's task process for updates
                # wait until the next iteration.
                return
            self._update_loop_busy = True

            for twitter_channel in self.ex.cache.twitter_channels.values():
                try:
                    await asyncio.sleep(0)  # bare yield

                    if not twitter_channel:  # no channels are following the channel.
                        continue

                    log.useless(f"Checking if Twitter Channel {twitter_channel.id} has a new Tweet.",
                                method=self.twitter_notification_updates)
                    await asyncio.sleep(10)
                    twitter_link = await twitter_channel.fetch_new_tweet()
                    if twitter_link:
                        await twitter_channel.send_update_to_followers(twitter_link)
                except Exception as e:
                    log.console(f"{e} (Exception)", method=self.twitter_notification_updates)
        except Exception as e:
            log.console(f"{e} (Exception2)", method=self.twitter_notification_updates)

        self._update_loop_busy = False
