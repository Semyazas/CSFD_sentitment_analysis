from .AbsScrapper import AbsScrapper
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import time
import tqdm

class MovieReviewScraper(AbsScrapper):
    def __init__(self):
        super().__init__()
        
    def scrap_CSFD_reviews_from_movie(
            self,
            movie_url: str,
            number_of_pages : int  = 5 
        ) -> list[str]:
        """Scrape reviews from a CSFD movie page."""

        service = Service('chromedriver.exe')  # Update with your chromedriver path
        driver = webdriver.Chrome(service=service, options=self.chrome_options)
        wait = WebDriverWait(driver, 30)
        try:
            driver.get(movie_url)
            time.sleep(0.5)  # Wait for the page to load
            driver.find_element(By.ID, "didomi-notice-agree-button").click()
            current_page = 1
            review_info = []
            time.sleep(1)  # Wait for the page to load
            elem = driver.find_element(By.CLASS_NAME, "film-rating-average")
            raw = (elem.get_attribute("textContent") or "").strip()
            m = re.search(r"([0-9]+(?:[.,][0-9]+)?)", raw)
            average_rating = float(m.group(1).replace(",", ".")) if m else None
            print(f"Average rating extracted: {average_rating}")
            for _ in tqdm.tqdm(range(number_of_pages)): # Limit to 10 pages
                reviews = driver.find_elements(By.CSS_SELECTOR, "article.article.article-white")
                for review in reviews: 
                    result = self.__extract_info_from_review(review, current_page, driver, wait)
                    if result:
                        review_info.append(result)
                self.__move_to_next_page(driver, wait, current_page )
              #  print(f"--- End of page {current_page} ---")
                current_page += 1
            return {"reviews": review_info, 
                    "average_rating": average_rating,
            }

        finally:
            driver.quit()

    def __extract_info_from_review(
            self,
            review : WebElement,
            wait : WebDriverWait) -> tuple[str, str, str, str] | None: # I want to find rating of the user, it is in format "stars stars-X" where X is number of stars
        pattern = re.compile(r"^stars stars-(\d)$")
        try:
            username = review.find_element(By.CLASS_NAME, "user-title").text
            rating_element = WebDriverWait(review, 3).until(
                lambda r: r.find_element(By.CLASS_NAME, "star-rating")
            )
            subclasses = rating_element.find_elements(By.XPATH, ".//span[contains(@class, 'stars')]")
            for subclass in subclasses:
                match = pattern.match(subclass.get_attribute("class"))
                if match:
                    break
            review_text = review.find_element(By.CLASS_NAME, "comment").text
            movie_name = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "film-header-name"))).find_element(By.TAG_NAME, "h1").text
            rating = match.group(1) if match else None
            print(f"✅ {username=} {rating=} {len(review_text or '')} chars {movie_name=}")
            return username, rating, review_text, movie_name
        except Exception as e:
            print(f"[WARN] Rating not found for one review: {e}")
            rating_element = None
            # driver.save_screenshot(f"debug_page_{current_page}.png")
            return None

    def __move_to_next_page(self, driver, wait, current_page):
        for attempt in range(3):
            try:
                next_button = wait.until(
                    EC.element_to_be_clickable((By.XPATH, f"//div[contains(@class, 'pagination')]//a[text()='{current_page+1}']"))
                )
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_button)
                driver.execute_script("arguments[0].click();", next_button)
                time.sleep(1.5)
                return True
            except Exception as e:
                print(f"[WARN] Attempt {attempt+1}/3 to click page {current_page+1} failed: {e}")
                time.sleep(2)
        return False