import os
from discord.ext import commands, tasks
from module import twitter


client = 0


def setup(client1):
    client1.add_cog(Twitter(client1))
    global client
    client = client1

class Twitter(commands.Cog):
    def __init__(self, client):
        pass

    @commands.command()
    @commands.is_owner()
    async def tweet(self, ctx, *, context):
        """Tweets a status update on Twitter [Format: %tweet (status)]"""
        twitter.update_status(context)
        f = open("twitterlink.txt", "r")
        final_url = f.read()
        f.close()
        await ctx.send("> Your Tweet has been successfully uploaded to {}".format(final_url))
        os.remove("twitterlink.txt")

    @commands.command()
    @commands.is_owner()
    async def deletetweet(self, ctx, *, context):
        """Delete a Tweet by it's ID [Format: %deletetweet (id)]"""
        twitter.delete_status(context)
        await ctx.send("> The Tweet ID **{}** has been successfully deleted.".format(context))

    @commands.command()
    @commands.is_owner()
    async def recenttweets(self, ctx, *, context=20):
        """Show Most Recents Tweets[Format: %recenttweets (amount)]"""
        twitter.recent_tweets(int(context))
        f = open("recent_tweets.txt", "r")
        list = f.read()
        f.close()
        await ctx.send("> Here are the past **{}** tweets:\n{}".format(context, list))
        os.remove("recent_tweets.txt")