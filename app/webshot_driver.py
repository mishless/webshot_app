from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from app.logger import logger


class WebshotDriver:
    def __init__(self):
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        # options.add_argument("--remote-debugging-port=9230")
        options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome(options=options)

    def get_links(self, url: str) -> list:
        self.driver.get(url)
        links = [
            element.get_attribute("href")
            for element in self.driver.find_elements(by=By.XPATH, value="//*[@href]")
        ]
        return links

    def save_screenshot(self, url: str, path: str) -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Saving screenshot for {url}.")
        self.driver.get(url)
        self.driver.save_screenshot(path)
        logger.debug(f"Screenshot for {url} saved successfully.")

    def __del__(self):
        logger.debug("Quitting driver.")
        self.driver.quit()
