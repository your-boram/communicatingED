import re
import time

import pandas as pd
from selenium_helper import SeleniumBase
from selenium.common.exceptions import NoSuchElementException


class Twitter:
    def __init__(self):
        self.base_url = "https://twitter.com/search?q="

        self.selenium = SeleniumBase()
        self.driver = self.selenium.driver

    def get_tweets_by_keyword(self, keyword, start_date, end_date):
        query = (
            f"{keyword} until%3A{end_date}%20since%3A{start_date}"
            "&q=lang%3Aen&src=typed_query&f=top"
        )

        url = self.base_url + query
        self.driver.get(url)
        time.sleep(10)
        return self._get_tweets_by_keyword()

    def _get_tweets_by_keyword(self):
        post_xpath = "/html/body/div[1]/div/div/div[2]/main/div/div/div/div[1]/div/div[2]/div/section/div/div/div"

        key_before = 0
        height = None

        data = {}

        while True:
            posts = self.driver.find_elements_by_xpath(post_xpath)

            for post in posts:
                key = re.search(
                    "transform: translateY\((.+)px\)",
                    post.get_attribute("style"),
                ).group(1)
                if key not in data.keys():
                    print(key)
                    try:
                        user_xpath = "/div/div/article/div/div/div/div[2]/div[2]/div[1]/div/div/div[1]/div[1]/div/div[2]/div/a"                                     
                        element = post.find_element_by_xpath(user_xpath)
                        data[key] = element.get_attribute("href")

                    except NoSuchElementException:
                        continue

            if float(key) <= key_before:
                break

            if height is None:
                height = float(key)
            key_before = float(key)
            self.selenium.scroll_down(height + 600, bottom=False)
            time.sleep(1)

        return pd.DataFrame({"text": data})


twitter = Twitter()
print(twitter.get_tweets_by_keyword("edtwt", "2020-01-01", "2021-12-31"))
