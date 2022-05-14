import pandas as pd

from tweepy_client import TweepyClient

if __name__ == '__main__':

    df = pd.read_csv("List_PRO_RECOVERY.csv")
    


    tweepy_client = TweepyClient()


    # get retweet
    tweet_id = "1509286895062290436"
    retweets = tweepy_client.get_retweets(tweet_id)
    print(retweets)