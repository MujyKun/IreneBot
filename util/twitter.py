from Utility import resources as ex


class Twitter:
    @staticmethod
    async def update_status(context):
        ex.api.update_status(status=context)
        tweet = ex.api.user_timeline(user_id=f'{ex.keys.twitter_account_id}', count=1)[0]
        return f"https://twitter.com/{ex.keys.twitter_username}/status/{tweet.id}"

    @staticmethod
    async def delete_status(context):
        ex.api.destroy_status(context)

    @staticmethod
    async def recent_tweets(context):
        tweets = ex.api.user_timeline(user_id=f'{ex.keys.twitter_account_id}', count=context)
        final_tweet = ""
        for tweet in tweets:
            final_tweet += f"> **Tweet ID:** {tweet.id} | **Tweet:** {tweet.text}\n"
        return final_tweet


ex.u_twitter = Twitter()
