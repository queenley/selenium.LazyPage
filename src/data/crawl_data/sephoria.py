from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from time import sleep
import pandas as pd
from tqdm import tqdm
import time
from bs4 import BeautifulSoup
import requests
from src.data.crawl_data import CrawlData
from typing import Set, Any
import openai
from src.config.chatgpt_key import chatgpt_key

openai.api_key = chatgpt_key


class SephoriaData(CrawlData):
    def __call__(self, *args, **kwargs):
        self.access_product_page(*args, **kwargs)
        self.get_product_urls(*args, **kwargs)
        self.get_content_from_url(*args, **kwargs)
        self.generate_label(*args, **kwargs)

    def access_product_page(self, category_name) -> None:
        # Click element to go to the page of all products
        click_title = WebDriverWait(self._driver, 50).until(EC.element_to_be_clickable((By.LINK_TEXT, category_name)))
        action = ActionChains(self._driver)
        action.click(click_title).key_down(Keys.CONTROL).key_up(Keys.CONTROL).perform()
        sleep(10)
        click_title.click()

    def get_product_urls(self, scroll_height=400, add_height=300, pro_per_page=60, num_pages=46) -> Set:
        all_urls = set()
        # giving some time to load
        page = 1
        while True:
            # Scroll down until no more content is loaded
            self._driver.execute_script(f"window.scrollTo(0, {scroll_height});")
            # giving time to load
            time.sleep(10)

            # get all urls of products
            elm_products = self._driver.find_elements(By.CSS_SELECTOR,
                                                      "body > div:nth-child(3) > div > div > div > "
                                                      "div.css-1t2x5d0.eanm77i0 "
                                                      "> main > div:nth-child(3) > div.css-1322gsb > * > a")
            for product in tqdm(elm_products):
                url = product.get_attribute("href")
                all_urls.add(url)

            # continue scroll
            scroll_height += add_height
            if len(all_urls) == pro_per_page * page:
                print(f"Loaded all urls from the page {page}")
                # click Show More Product button
                more_button = WebDriverWait(self._driver, 50).until(EC.element_to_be_clickable((By.CSS_SELECTOR,
                                                                                                "body > "
                                                                                                "div:nth-child(3) > "
                                                                                                "div > div > div > "
                                                                                                "div.css-1t2x5d0"
                                                                                                ".eanm77i0 > "
                                                                                                "main > "
                                                                                                "div:nth-child(3) > "
                                                                                                "div.css-1322gsb > "
                                                                                                "div.css-unii66 > "
                                                                                                "button")))
                action = ActionChains(self._driver)
                action.click(more_button).key_down(Keys.CONTROL).key_up(Keys.CONTROL).perform()
                more_button.click()
                page += 1

            # break when load all pages
            if page == num_pages:
                break

        return all_urls

    def generate_label(self, product_name: str, information: str) -> str:
        messages = [{"role": "system", "content": "You are a intelligent assistant."}]

        message = f"please create a post to advertise {product_name} with knowledge: {information}"

        if message:
            messages.append(
                {"role": "user", "content": message},
            )
            chat = openai.ChatCompletion.create(
                model="gpt-3.5-turbo", messages=messages
            )

        reply = chat.choices[0].message.content
        return reply

    def get_content_from_url(self, url: str) -> Any:
        self._driver.get(url)

        df = pd.DataFrame(columns=['url', 'product name', 'full content'])
        df.at[len(df), 'url'] = url

        name_product = self._driver.find_element(By.XPATH, "//span[contains(@data-at, 'product_name')]")
        df.at[len(df) - 1, 'product name'] = name_product.text

        elm_contents = self._driver.find_elements(By.CSS_SELECTOR,
                                                  "body > div:nth-child(3) > main > div:nth-child(1) > "
                                                  "div.css-32uy52.eanm77i0 > div:nth-child(2) > div > div/*")
        html_content = elm_contents[0].get_attribute("innerHTML")
        soup_content = BeautifulSoup(html_content, 'html.parser')
        for elem in soup_content.find_all(["a", "p", "div", "h3", "br"]):
            elem.replace_with(elem.text + "\n")
        content = soup_content.get_text(separator='\n', strip=True)
        df.at[len(df) - 1, 'full content'] = content

        return df
