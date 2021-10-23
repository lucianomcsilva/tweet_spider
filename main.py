from dotenv import load_dotenv
import tweepy
import os

load_dotenv()
consumer_key    = os.environ['TWITTER_APIKEY']
consumer_secret = os.environ['TWITTER_APISECRET']

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
# auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

#public_tweets = api.home_timeline()
#for tweet in public_tweets:
for tweet in tweepy.Cursor(api.search_tweets, q='bolsonaro').items(10):
    print(tweet.text)