import os
import tweepy
import json
import time
import dataset
from sqlalchemy.exc import ProgrammingError

API_KEY = os.environ.get('TWITTER_API_KEY')
API_KEY_SECRET = os.environ.get('TWITTER_API_KEY_SECRET')
ACCESS_TOKEN = os.environ.get('TWITTER_API_ACCESS_TOKEN')
ACCESS_TOKEN_SECRET = os.environ.get('TWITTER_API_ACCESS_TOKEN_SECRET')

print("API_KEY:",API_KEY)
print("API_KEY_SECRET:",API_KEY_SECRET)
print("ACCESS_TOKEN:",ACCESS_TOKEN)
print("ACCESS_TOKEN_SECRET:",ACCESS_TOKEN_SECRET)

TABLE_NAME = 'tweets'
KEY_WORDS = ["covid", "covid-19", "sars-cov-2", "coronavirus", "koronavirus", "koronawirus"]

CONNECTION_STRING = 'sqlite:///db/tweets.db'

auth = tweepy.OAuthHandler(API_KEY, API_KEY_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

api = tweepy.API(auth)

db = dataset.connect(CONNECTION_STRING)

class StreamListener(tweepy.StreamListener):
    def on_status(self, status):
        if status.retweeted:
            return
        
        self._save_tweet(status)
    def on_error(self, status_code):
        print('Error ocurred:', status_code)
        if status_code == 420:
            print('Rate limited, sleeping for 15 minutes')
            time.sleep(15*60.0)

    def _save_tweet(self, status):
        description = status.user.description
        loc = status.user.location
        text = status.text
        coords = status.coordinates
        geo = status.geo
        name = status.user.screen_name
        user_created = status.user.created_at
        followers = status.user.followers_count
        id_str = status.id_str
        created = status.created_at
        retweets = status.retweet_count
        bg_color = status.user.profile_background_color

        if geo is not None:
            geo = json.dumps(geo)

        if coords is not None:
            coords = json.dumps(coords)

        tweet = dict(
                user_description=description,
                user_location=loc,
                coordinates=coords,
                text=text,
                geo=geo,
                user_name=name,
                user_created=user_created,
                user_followers=followers,
                id_str=id_str,
                created=created,
                retweet_count=retweets,
                user_bg_color=bg_color,
            )

        table = db[TABLE_NAME]
        try:
            table.insert(tweet)
            print('Saved:', tweet)
        except ProgrammingError as err:
            print(err)
            

stream_listener = StreamListener()
stream = tweepy.Stream(auth=api.auth, listener=stream_listener)
stream.filter(track=KEY_WORDS)