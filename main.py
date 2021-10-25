from dotenv import load_dotenv
import tweepy
import sys
import os

load_dotenv()
consumer_key    = os.environ['TWITTER_APIKEY']
consumer_secret = os.environ['TWITTER_APISECRET']






def format_tweet(tweet): 
    # a dict to contain information about single tweet
    tweet_information=dict()

    # text of tweet
    tweet_information['text']=tweet.text #.encode('utf-8')

    # date and time at which tweet was created
    tweet_information['created_at']=tweet.created_at.strftime("%Y-%m-%d %H:%M:%S")

    # id of this tweet
    tweet_information['id_str']=tweet.id_str

    # retweet count
    tweet_information['retweet_count']=tweet.retweet_count

    # favourites count
    tweet_information['favorite_count']=tweet.favorite_count

    # screename of the user to which it was replied (is Nullable)
    tweet_information['in_reply_to_screen_name']=tweet.in_reply_to_screen_name

    #geo location
    tweet_information['geo']=tweet.geo

    tweet_information['source']=tweet.source

    tweet_information['language']=tweet.lang


    #######################################
    # user information in user dictionery #
    #######################################
    user_dictionery=tweet._json['user']

    # no of followers of the user
    tweet_information['followers_count']=user_dictionery['followers_count']

    # screename of the person who tweeted this
    tweet_information['id']=user_dictionery['id']

    # name of the person who tweeted this
    tweet_information['name_at_tweet_time']=user_dictionery['name']

    # screename of the person who tweeted this
    tweet_information['screen_name']=user_dictionery['screen_name']

    #user location    
    tweet_information['user_location']=user_dictionery['location']

    #user location    
    tweet_information['user_created_at']=user_dictionery['created_at']

    # return formated tweet
    return tweet_information

def fetch_search(SearchQuery, MaxItens):
    '''
        Autentica com usuario e senho, a partir das variaveis de ambiente e
        inicia a biblioteca Tweepy para lidar com a API do Twitter
    ''' 
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    api = tweepy.API(auth)
    # auth.set_access_token(access_token, access_token_secret)
    
    #public_tweets = api.home_timeline()
    #for tweet in public_tweets:
    return tweepy.Cursor(api.search_tweets, q=f'{SearchQuery}', lang='pt', geocode='-23.6640269,-46.6359077,25km').items(MaxItens)


def print_tweets(Tweets, onlyText=False):
    for tweet in Tweets:
        if(onlyText):
            print(tweet.text)            
        else:
            print(format_tweet(tweet))
        print("----------------------------------")
        #print(tweet)

def get_them_all():
    _max_itens = 100
    _terms = ['hbomax', 'disneyplus', 'disney+', 'netflix', 'star+', 'globoplay', 'amazon prime', 'primevideo']
    all_tweets = [];    
    for term in _terms:
        print("----------------------------------")
        print(f"--- {term}")
        print("----------------------------------")
        all_tweets.extend(fetch_search(term, _max_itens))
        print_tweets(all_tweets, False)

def main():
    # Garante que todos os parametros estão sendo enviados
    if len(sys.argv) == 1:
        sys.exit("Usage: python main.py QuerySearch [MaxItens]")
    
    # Inicia com valor padrão, caso nao seja enviado nada
    _search = 'bolsonaro'
    _max_itens = 10
    if len(sys.argv) >= 2:
        _search=sys.argv[1]
    if len(sys.argv) == 3:
        _max_itens=int(sys.argv[2])
    print_tweets(fetch_search(_search, _max_itens), True)

if __name__ == '__main__':
    get_them_all()
    #main()    
