import os
import time

import tweepy
import pandas as pd


class TweepyClient:
    def __init__(self):
        with open(".env", "r") as file:
            for line in file.readlines():
                key, value = line.split("=")
                os.environ[key] = value
        self.client = tweepy.Client(os.environ["TWITTER_BEARER_TOKEN"])

    def get_all_tweets(self, query, start_time, end_time, max_results=100):
        pagination_token = "meaningless_initial_value"

        iter = 0
        result = set()
        while pagination_token is not None:
            res = self.client.search_all_tweets(
                query,
                start_time=start_time,
                end_time=end_time,
                max_results=max_results,
                expansions='author_id',
            )

            for tweet in res.data:
                result.add(tweet["author_id"])

            pagination_token = res.meta.get("next_token", None)
            iter += 1

            time.sleep(1)

        return {"id":result}

    def get_user_profiles(self, ids):
        res = self.client.get_users(
            ids=",".join(ids), user_fields="description,public_metrics"
        )
        result = []
        for data in res.data:
            result.append(
                {
                    "username": data["username"],
                    "id": data["id"],
                    "description": data["description"],
                    "followers": data["public_metrics"]["followers_count"],
                    "following": data["public_metrics"]["following_count"],
                    "num_tweets": data["public_metrics"]["tweet_count"],
                }
            )

        return result

    def get_user_id_by_name(self, username):
        res = self.client.get_user(username=username)
        return res.data.id

    def get_timeline(self, user_id, max_results=100):
        pagination_token = "meaningless_initial_value"

        iter = 0
        result = []
        while pagination_token is not None:
            res = self.client.get_users_tweets(
                id=user_id,
                max_results=max_results,
                tweet_fields="created_at,public_metrics",
                expansions="attachments.media_keys",
            )

            for tweet in res.data:
                result.append(
                    {
                        "user_id": user_id,
                        "text": tweet["text"],
                        "id": tweet["id"],
                        "like_count": tweet["public_metrics"]["like_count"],
                        "retweet_count": tweet["public_metrics"][
                            "retweet_count"
                        ],
                    }
                )

            pagination_token = res.meta.get("next_token", None)
            iter += 1

        return result

    def save(self, result, filename):
        print(f"Save data to {filename}")
        df = pd.DataFrame(result)
        df.to_csv(filename)
