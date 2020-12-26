from discord.ext import commands
from Utility import resources as ex


class Twitter(commands.Cog):
    @commands.command()
    @commands.is_owner()
    async def tweet(self, ctx, *, tweet):
        """Tweets a status update on Twitter [Format: %tweet (status)]"""
        tweet_url = await ex.u_twitter.update_status(tweet)
        await ctx.send(f"> Your Tweet has been successfully uploaded to {tweet_url}")

    @commands.command()
    @commands.is_owner()
    async def deletetweet(self, ctx, *, tweet_id):
        """Delete a Tweet by it's ID [Format: %deletetweet (id)]"""
        await ex.u_twitter.delete_status(tweet_id)
        await ctx.send(f"> The Tweet ID **{tweet_id}** has been successfully deleted.")

    @commands.command()
    @commands.is_owner()
    async def recenttweets(self, ctx, *, amount_of_tweets=20):
        """Show Most Recents Tweets[Format: %recenttweets (amount)]"""
        tweets = await ex.u_twitter.recent_tweets(amount_of_tweets)
        await ctx.send(f"> Here are the past **{amount_of_tweets}** tweets:\n{tweets}")
