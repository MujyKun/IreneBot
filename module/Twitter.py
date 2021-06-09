from discord.ext import commands, tasks
from IreneUtility.Utility import Utility
from IreneUtility.util import u_logger as log
import asyncio


class Twitter(commands.Cog):
    def __init__(self, ex):
        self.ex: Utility = ex

    @commands.command()
    @commands.is_owner()
    async def tweet(self, ctx, *, tweet):
        """
        Tweets a status update on Twitter

        [Format: %tweet (status)]
        """
        tweet_url = await self.ex.u_twitter.update_status(tweet)
        msg = await self.ex.get_msg(ctx.author.id, "twitter", "tweet_success", ['tweet_url', tweet_url])
        await ctx.send(msg)

    @commands.command()
    @commands.is_owner()
    async def deletetweet(self, ctx, *, tweet_id):
        """
        Delete a Tweet by it's ID

        [Format: %deletetweet (id)]
        """
        await self.ex.u_twitter.delete_status(tweet_id)
        msg = await self.ex.get_msg(ctx.author.id, "twitter", "delete_success", ['tweet_id', tweet_id])
        await ctx.send(msg)

    @commands.command()
    @commands.is_owner()
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
            await self.ex.cache.twitter_channel.send(twitter_link)  # post to discord.
        except Exception as e:
            log.console(f"{e} -> send_photos_to_twitter")
