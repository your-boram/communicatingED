import os
import time

import tweepy
import pandas as pd

INTERVAL = 3


class TweepyClient:
    """
    Thin wrapper for tweepy API v2 client
    """

    def __init__(self):
        with open(".env", "r") as file:
            for line in file.readlines():
                key, value = line.split("=")
                os.environ[key] = value
        self.client = tweepy.Client(os.environ["TWITTER_BEARER_TOKEN"])

    def get_all_tweets(self, query, start_time, end_time, max_results=500):
        """
        Reference: https://developer.twitter.com/en/docs/twitter-api/tweets/search/api-reference/get-tweets-search-all
        """
        next_token = ""

        iter = 0
        self.result = []
        try:
            while next_token is not None:
                if next_token:
                    kwargs = {"next_token": next_token}
                else:
                    kwargs = {}
                res = self.client.search_all_tweets(
                    query,
                    start_time=start_time,
                    end_time=end_time,
                    max_results=max_results,
                    expansions='author_id,attachments.media_keys',
                    tweet_fields='created_at,public_metrics,lang',
                    media_fields='type,url,media_key',
                    **kwargs,
                )

                media_list = [entry for entry in res.includes.get("media", [])]
                for tweet in res.data:
                    media_keys = None
                    if tweet.attachments:
                        media_keys = tweet.attachments["media_keys"]
                    media_type = None
                    media_urls = []

                    if media_keys is not None:
                        for media_key in media_keys:
                            for media in media_list:
                                if media_key == media["media_key"]:
                                    media_type = media["type"]
                                    media_urls.append(media.get("url", None))
                                    break

                    if tweet["lang"] != "en":
                        continue

                    public_metrics = tweet.public_metrics

                    self.result.append(
                        {
                            "author_id": tweet["author_id"],
                            "text": tweet["text"],
                            "created_at": tweet["created_at"],
                            "media_type": media_type,
                            "media_url": media_urls,
                            "retweet_count": public_metrics["retweet_count"],
                            "reply_count": public_metrics["reply_count"],
                            "like_count": public_metrics["like_count"],
                            "quote_count": public_metrics["quote_count"],
                        }
                    )

                next_token = res.meta.get("next_token", None)
                iter += 1
                print(f"Collected {len(self.result)} tweets", end="\r")
                time.sleep(INTERVAL)
        except Exception as exc:
            print(exc)
            raise exc
        finally:
            print("\nCollection finished")
            return pd.DataFrame(self.result)

    def get_user_profiles(self, ids):
        self.user_result = []
        for idx in range(0, len(ids), 100):
            # split ids with the interval of 100
            chunk = ids[idx : idx + 100]
            res = self.client.get_users(
                ids=",".join(chunk), user_fields="description,public_metrics"
            )
            for data in res.data:
                self.user_result.append(
                    {
                        "username": data["username"],
                        "url": f"https://twitter.com/{data['username']}",
                        "id": data["id"],
                        "description": data["description"],
                        "followers": data["public_metrics"]["followers_count"],
                        "following": data["public_metrics"]["following_count"],
                        "num_tweets": data["public_metrics"]["tweet_count"],
                    }
                )
            print(f"Processed {idx}/{len(ids)} data", end="\r")
            time.sleep(INTERVAL)

        return pd.DataFrame(self.user_result)

    def get_user_id_by_name(self, username):
        res = self.client.get_user(username=username)
        return res.data.id

    def get_timeline(self, user_id, max_results=100):
        next_token = ""

        iter = 0
        result = []
        while next_token is not None:
            if next_token:
                kwargs = {"next_token": next_token}
            else:
                kwargs = {}
            res = self.client.get_users_tweets(
                id=user_id,
                max_results=max_results,
                tweet_fields="created_at,public_metrics",
                expansions="attachments.media_keys",
                **kwargs,
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

            next_token = res.meta.get("next_token", None)
            iter += 1
            time.sleep(INTERVAL)

        return pd.DataFrame(result)

    def save(self, dataframe, filename):
        print(f"Save data to {filename}")
        dataframe.to_csv(filename)
