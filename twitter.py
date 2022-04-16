import re
import time

import pandas as pd
from selenium_helper import SeleniumBase
from tqdm import tqdm


class Twitter:
    def __init__(self, keyword, start_date=None, end_date=None):
        base_url = "https://twitter.com/search?q="
        query = f"{keyword} &src=typed_query&f=top"

        if start_date:
            query += f"&since%3A{start_date}"

        if end_date:
            query += f"&until%3A{end_date}"

        self.url = base_url + query

        self.selenium = SeleniumBase()
        self.driver = self.selenium.driver

    def run(self):
        self.driver.get(self.url)
        time.sleep(10)
        try:
            return self._scroll_to_the_end()
        except KeyboardInterrupt:
            return self.data

    def _scroll_to_the_end(self):
        post_xpath = "/html/body/div[1]/div/div/div[2]/main/div/div/div/div[1]/div/div[2]/div/section/div/div/div"

        num_posts_before = -1

        self.data = {}
        retweets = []
        height = 0
        scroll = 200
        while True:

            posts = self.driver.find_elements_by_xpath(post_xpath)

            for post in posts:
                try:
                    key = re.search(
                        "transform: translateY\((.+)px\)",
                        post.get_attribute("style"),
                    ).group(1)

                    if key not in self.data.keys():
                        text_xpath = "./div/div/article/div/div/div/div[2]/div[2]/div[2]/div[1]/div/div"
                        text = post.find_element_by_xpath(text_xpath).text

                        date_xpath = "./div/div/article/div/div/div/div[2]/div[2]/div[1]/div/div/div[1]/a/time"
                        date = post.find_element_by_xpath(
                            date_xpath
                        ).get_attribute("datetime")

                        url_xpath = "./div/div/article/div/div/div/div[2]/div[2]/div[1]/div/div/div[1]/a"
                        url = post.find_element_by_xpath(
                            url_xpath
                        ).get_attribute("href")
                        self.data[key] = {
                            "text": text,
                            "date": date,
                            "url": url,
                            "src": "twitter",
                        }

                        # retweets with comment (quote)
                        retweet_url = (
                            f"https://twitter.com{url}/retweets/with_comments"
                        )
                        retweets.append(retweet_url)
                except:
                    continue

            height = self.driver.execute_script(
                "return document.documentElement.scrollTop || document.body.scrollTop"
            )
            height += scroll
            self.selenium.scroll_down(height, bottom=False)

            if len(self.data) == num_posts_before:
                self.driver.execute_script(
                    f"window.scrollTo(0, {height - 1000});"
                )
                time.sleep(10)
            num_posts_before = len(self.data)

            print(f"Collected {len(self.data)} tweets", end="\r")

        return self.data

    def save(self, data, filename="twitter.csv"):

        result = list(data.values())

        df = pd.DataFrame(result)
        df.to_csv(filename)

        return df

    def get_user_page(self, urls):

        self.user_stats = {}
        self.failed = []
        for url in tqdm(urls):
            self.driver.get(url)
            time.sleep(5)
            try:
                num_tweet_xpath = "/html/body/div[1]/div/div/div[2]/main/div/div/div/div[1]/div/div[1]/div[1]/div/div/div/div/div[2]/div/div"
                num_following_xpath = "/html/body/div[1]/div/div/div[2]/main/div/div/div/div[1]/div/div[2]/div/div/div/div/div[5]/div[1]/a/span[1]/span"
                num_follower_xpath = "/html/body/div[1]/div/div/div[2]/main/div/div/div/div[1]/div/div[2]/div/div/div/div/div[5]/div[2]/a/span[1]/span"
                num_tweet = self.driver.find_element_by_xpath(
                    num_tweet_xpath
                ).text
                num_following = self.driver.find_element_by_xpath(
                    num_following_xpath
                ).text
                num_follower = self.driver.find_element_by_xpath(
                    num_follower_xpath
                ).text

                self.user_stats[url] = {
                    "num_tweet": num_tweet,
                    "num_following": num_following,
                    "num_follower": num_follower,
                }
            except:
                self.failed.append(url)

        return pd.DataFrame(self.user_stats), self.failed

    def get_follower_list(self, profile_url):
        pass

    def get_timeline(self, profile_url):
        self.driver.get(profile_url)
        time.sleep(5)

        post_xpath = "/html/body/div[1]/div/div/div[2]/main/div/div/div/div[1]/div/div[2]/div/div/section/div/div/div"

        num_posts_before = -1

        self.data = {}
        retweets = []
        height = 0
        scroll = 300
        collected = time.time()
        while True:

            posts = self.driver.find_elements_by_xpath(post_xpath)

            for post in posts:
                try:
                    key = re.search(
                        "transform: translateY\((.+)px\)",
                        post.get_attribute("style"),
                    ).group(1)

                    if key not in self.data.keys():
                        text_xpath = "./div/div/article/div/div/div/div[2]/div[2]/div[2]/div[1]/div/div"
                        text = post.find_element_by_xpath(text_xpath).text

                        try:
                            media_xpath = "./div/div/article/div/div/div/div[2]/div[2]/div[2]/div[2]/div/div/div/div/div/a/div/div[2]/div/img"
                            media = post.find_element_by_xpath(
                                media_xpath
                            ).get_attribute("src")
                        except:
                            media = None

                        date_xpath = "./div/div/article/div/div/div/div[2]/div[2]/div[1]/div/div/div[1]/a/time"
                        date = post.find_element_by_xpath(
                            date_xpath
                        ).get_attribute("datetime")

                        url_xpath = "./div/div/article/div/div/div/div[2]/div[2]/div[1]/div/div/div[1]/a"
                        url = post.find_element_by_xpath(
                            url_xpath
                        ).get_attribute("href")
                        self.data[key] = {
                            "text": text,
                            "date": date,
                            "url": url,
                            "media": media,
                            "src": "twitter",
                        }

                        # retweets with comment (quote)
                        retweet_url = (
                            f"https://twitter.com{url}/retweets/with_comments"
                        )
                        retweets.append(retweet_url)
                        collected = time.time()
                except:
                    continue

            height = self.driver.execute_script(
                "return document.documentElement.scrollTop || document.body.scrollTop"
            )
            height += scroll
            self.selenium.scroll_down(height, bottom=False)

            if (
                len(self.data) == num_posts_before
                and time.time() - collected > 10
            ):
                self.driver.execute_script(
                    f"window.scrollTo(0, {height - 1000});"
                )
                time.sleep(10)
            num_posts_before = len(self.data)

            print(f"Collected {len(self.data)} tweets", end="\r")

        return self.data
