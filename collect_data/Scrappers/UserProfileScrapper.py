from .UrlFinder import UrlFinder
import sqlite3
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import tqdm

class UserProfileScrapper(UrlFinder):
    def __init__(self):
        super().__init__()

    def get_user_data(
        self,
        user_list : list[str],
        cursor : sqlite3.Cursor
        ) -> None:
        """ Get user data from CSFD user pages.
            We will scrape data about:
            - username
            - total reviews
            - age of account
            - where is user from
        """
        for username, user_url in tqdm.tqdm(user_list):
            try:
                data_point = self.__scrap_user_data_from_page(user_url)
                if data_point:
                    cursor.execute("""
                        INSERT OR IGNORE INTO users (username, total_reviews, since_when, place, user_ref)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        username, 
                        data_point["total_reviews"],
                        data_point["since_when"],
                        data_point["place"],
                        user_url
                    ))
                    cursor.connection.commit()
                    
            except Exception as e:
                print(f"[WARN] Could not find user {username}: {e}")

    def __scrap_user_data_from_page(
        self, 
        url: str
        ) -> list[dict]:
        """ Scrape user data from CSFD user pages.
            We will scrape data about:
            - username
            - total reviews
            - age of account
            - where is user from
        """
        service = Service('chromedriver.exe')  # Update with your chromedriver path
        driver = webdriver.Chrome(service=service, options=self.chrome_options)
        wait = WebDriverWait(driver, 30)
        try:
            driver.get(url)
            if "didomi-notice-agree-button" in driver.page_source:
                wait.until(EC.presence_of_element_located((By.ID, "didomi-notice-agree-button")))
                wait.until(EC.element_to_be_clickable((By.ID, "didomi-notice-agree-button"))).click()
            content = driver.find_element(By.CLASS_NAME, "user-profile-content")

            username = content.find_element(By.XPATH, "//h1").text
            since_when_present = int(
                content.find_elements(By.XPATH, "//div[@class='user-profile-footer-left']")\
                [0].text.split()[3].split(".")[2]
            )
            place = self.__extract_place_from_profile(driver)          
            sec = driver.find_element(By.XPATH, "//section[@class='box box-user-rating striped-articles']")
            elem = sec.find_element(By.CSS_SELECTOR, ".count")
            raw = (elem.get_attribute("textContent") or elem.text or "").strip()
            raw = raw.strip().lstrip("(").rstrip(")")

            # Remove non-digit characters (spaces, NBSP, commas, etc.) and keep digits only
            digits = re.sub(r"[^\d]", "", raw)

            count = int(digits) if digits else 0
            driver.close()
            return {
                "username": username,
                "total_reviews": count,
                "since_when": since_when_present,
                "place": place
            }
    
        except Exception as e:
            print(f"[WARN] Could not scrape user data from {url}: {e}")
        # Implementation would go here
        return None
    
    def __extract_place_from_profile(
        self,
        driver,
        timeout= 8
        ) -> str | None:
        wait = WebDriverWait(driver, timeout)
        # wait for the block to exist
        p = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".user-profile-content p")))

        # get username (strong) and full p textContent (keeps whitespace)
        try:
            name = p.find_element(By.TAG_NAME, "strong").get_attribute("textContent").strip()
        except Exception:
            name = ""
        full = (p.get_attribute("textContent") or "").strip()

        # remove the username occurrence (if present) and normalize whitespace
        if name:
            full = full.replace(name, "")
        full = " ".join(full.split())        # collapse whitespace
        full = full.strip().strip('"')       # strip leading/trailing quotes

        # split by newline or comma and take first meaningful token
        parts = [part.strip().strip('"') for part in re.split(r'[\n,]+', full) if part.strip()]
        place = parts[0] if parts else None
        return place