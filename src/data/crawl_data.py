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
from abc import abstractmethod, ABC
from typing import Any, Set

DRIVER_PATH = 'chromedriver'
# option.add_argument('headless')
driver = webdriver.Chrome(executable_path=DRIVER_PATH)


class CrawlData(ABC):
    def __init__(self, url: str, _driver: Any):
        self.url = url
        self._driver = _driver

    @abstractmethod
    def access_product_page(self, category_name: str) -> None:
       pass

    @abstractmethod
    def get_product_urls(self) -> Set:
        pass
