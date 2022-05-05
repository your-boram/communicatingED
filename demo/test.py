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
            keyword, "2022-03-01T00:00:00Z", "2022-03-31T00:00:00Z"
        )
        df = tweepy_client.save(result, f"{keyword}_tweets.csv")

        df = pd.read_csv(f"{keyword}_tweets.csv")
        user_ids = df["author_id"].unique().astype(str)

        user_result = tweepy_client.get_user_profiles(user_ids)
        user_df = tweepy_client.save(user_result, f"{keyword}_users.csv")
