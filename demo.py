import pandas as pd

from tweepy_client import TweepyClient

if __name__ == '__main__':

    keywords = [
        "edtwt",
        "proana",
        "edrecovery",
        "anorexiarecovery",
        "eatingdisorderrecovery",
    ]

    for keyword in keywords:
        tweepy_client = TweepyClient()
        result = tweepy_client.get_all_tweets(
            keyword, "2022-03-30T00:00:00Z", "2022-03-31T00:00:00Z"
        )
        df = tweepy_client.save(result, f"{keyword}_tweets.csv")

        user_ids = df["author_id"].unique().astype(str)
        user_result = tweepy_client.get_user_profiles(user_ids)
        tweepy_client.save(user_result, f"{keyword}_users.csv")

        # Uncomment below if you want to go through all user ids
        # for user_id in user_ids:
        user_id = user_result["id"].iloc[0]
        timeline = tweepy_client.get_timeline(user_id)
        tweepy_client.save(timeline, f"{keyword}_timeline.csv")

    # get retweet
    tweet_id = "1509286895062290436"
    retweets = tweepy_client.get_retweets(tweet_id)
    print(retweets)