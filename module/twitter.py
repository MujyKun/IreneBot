import tweepy
# NOTE: I put my keys in the keys.py to separate them
# from this main file.
# Please refer to keys_format.py to see the format.
from module import keys

# NOTE: flush=True is just for running this script
# with PythonAnywhere's always-on task.
# More info: https://help.pythonanywhere.com/pages/AlwaysOnTasks/
print('', flush=True)

auth = tweepy.OAuthHandler(keys.CONSUMER_KEY, keys.CONSUMER_SECRET)
auth.set_access_token(keys.ACCESS_KEY, keys.ACCESS_SECRET)
api = tweepy.API(auth)

FILE_NAME = 'last_seen_id.txt'


def retrieve_last_seen_id(file_name):
    f_read = open(file_name, 'r')
    last_seen_id = int(f_read.read().strip())
    f_read.close()
    return last_seen_id


def store_last_seen_id(last_seen_id, file_name):
    f_write = open(file_name, 'w')
    f_write.write(str(last_seen_id))
    f_write.close()
    return


def reply_to_tweets():
    print('retrieving and replying to tweets...', flush=True)
    # DEV NOTE: use 1060651988453654528 for testing.
    last_seen_id = retrieve_last_seen_id(FILE_NAME)
    # NOTE: We need to use tweet_mode='extended' below to show
    # all full tweets (with full_text). Without it, long tweets
    # would be cut off.
    mentions = api.mentions_timeline(
                        last_seen_id,
                        tweet_mode='extended')
    for mention in reversed(mentions):
        print(str(mention.id) + ' - ' + mention.full_text, flush=True)
        last_seen_id = mention.id
        store_last_seen_id(last_seen_id, FILE_NAME)
        if '#mujybottest' in mention.full_text.lower():
            print('found #mujybottest!', flush=True)
            print('responding back...', flush=True)
            api.update_status('@' + mention.user.screen_name +
                    ' Working!', mention.id)


def update_status(context):
    print('Updating Status')
    api.update_status(status=context, )
    tweet = api.user_timeline(user_id='1119714202615259136', count=1)[0]
    #print (tweet.id)
    final_url = "https://twitter.com/BotMujy/status/{}".format(tweet.id)
    f = open("twitterlink.txt","w")
    f.write(final_url)
    f.close

def delete_status(context):
    print('Deleting Status')
    api.destroy_status(context)

def recent_tweets(context):
    print ('Grabbing Tweets')
    tweets = api.user_timeline(user_id='1119714202615259136', count=context)
    f = open('recent_tweets.txt',"w")
    for tweet in tweets:
        f.write("> **Tweet ID:** {} | **Tweet:** {}\n".format(tweet.id, tweet.text,))
    f.close()


"""
while True:
    reply_to_tweets()
    time.sleep(15)
"""
