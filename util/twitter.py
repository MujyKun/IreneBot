from Utility import Utility


class Twitter(Utility):
    async def update_status(self, context):
        self.api.update_status(status=context)
        tweet = self.api.user_timeline(user_id=f'{keys.twitter_account_id}', count=1)[0]
        return f"https://twitter.com/{keys.twitter_username}/status/{tweet.id}"

    async def delete_status(self, context):
        self.api.destroy_status(context)

    async def recent_tweets(self, context):
        tweets = self.api.user_timeline(user_id=f'{keys.twitter_account_id}', count=context)
        final_tweet = ""
        for tweet in tweets:
            final_tweet += f"> **Tweet ID:** {tweet.id} | **Tweet:** {tweet.text}\n"
        return final_tweet

