from discord.ext import commands
from Utility import resources as ex


class Twitter(commands.Cog):
    @commands.command()
    @commands.is_owner()
    async def tweet(self, ctx, *, tweet):
        """Tweets a status update on Twitter [Format: %tweet (status)]"""
        tweet_url = await ex.u_twitter.update_status(tweet)
        msg = await ex.get_msg(ctx.author.id, "twitter", "tweet_success")
        msg = await ex.replace(msg, ['tweet_url', tweet_url])
        await ctx.send(msg)

    @commands.command()
    @commands.is_owner()
    async def deletetweet(self, ctx, *, tweet_id):
        """Delete a Tweet by it's ID [Format: %deletetweet (id)]"""
        await ex.u_twitter.delete_status(tweet_id)
        msg = await ex.get_msg(ctx.author.id, "twitter", "delete_success")
        msg = await ex.replace(msg, ['tweet_id', tweet_id])
        await ctx.send(msg)

    @commands.command()
    @commands.is_owner()
    async def recenttweets(self, ctx, *, amount_of_tweets=20):
        """Show Most Recents Tweets[Format: %recenttweets (amount)]"""
        tweets = await ex.u_twitter.recent_tweets(amount_of_tweets)
        msg = await ex.get_msg(ctx.author.id, "twitter", "recent_tweets")
        msg = await ex.replace(msg, [['tweet_amount', amount_of_tweets], ['tweets', tweets]])
        await ctx.send(msg)
