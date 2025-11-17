from .AbsScrapper import AbsScrapper
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import tqdm
import sqlite3

class MovieReviewScraper(AbsScrapper):
    
    def __init__(self):
        super().__init__()
        self.service = Service('chromedriver.exe')  # Update with your chromedriver path
        self.driver = webdriver.Chrome(service=self.service, options=self.chrome_options)
        self.wait = WebDriverWait(self.driver, 30)
        self.conn =sqlite3.connect('movie_reviews.db')

    def _restart_driver(self) -> None:
        self.driver.quit()
        self.service = Service('chromedriver.exe')  # Update with your chromedriver path
        self.driver = webdriver.Chrome(service=self.service, options=self.chrome_options)
        self.wait = WebDriverWait(self.driver, 30)
        self.conn =sqlite3.connect('movie_reviews.db')
    
    def scrap_CSFD_reviews_from_movie(
            self,
            movie_url: str,
            genre : str,
            number_of_pages : int  = 5,
            page : int = 1
        ) -> None:
        self._restart_driver()
        try:
            self.driver.get(movie_url)
            self.wait.until(EC.presence_of_element_located((By.ID, "didomi-notice-agree-button")))
            self.wait.until(EC.element_to_be_clickable((By.ID, "didomi-notice-agree-button"))).click()
            current_page = page
            average_rating = self.__get_average_rating()

            for page_num in tqdm.tqdm(range(number_of_pages)): # Limit to 10 pages
                reviews = self.driver.find_elements(By.CSS_SELECTOR, "article.article.article-white")
                self.__handle_data_collection_from_page(
                    reviews,
                    page_num,
                    genre,
                    average_rating
                )
                try:
                    self.__move_to_next_page(current_page)
                except Exception as e:
                    print(f"[ERROR] Could not move to page {current_page + 1}: {e}")
                    return True, current_page
                current_page += 1
        finally:
            self.driver.quit()
            return False, current_page  # Indicate no retry needed
        
    def __get_average_rating(self) -> float | None:
            elem = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "film-rating-average")))
            raw = (elem.get_attribute("textContent") or "").strip()
            m = re.search(r"([0-9]+(?:[.,][0-9]+)?)", raw)
            average_rating = float(m.group(1).replace(",", ".")) if m else None
            return average_rating
        
    def __handle_data_collection_from_page(
            self,
            reviews : WebElement,
            page_num : int,
            genre : str,
            average_rating : float
            ) -> None:
        for review_index,review in enumerate(reviews): 
            try:
                result = self.__extract_info_from_review(review)
                if result:
                    self.__add_data_to_reviews_table(result)
                    self.__add_data_to_movies_table(
                        result["movie_name"],
                        genre,  # Genre is not known here
                        average_rating
                    )
            except Exception as e:
                print(f"[ERROR] Failed to extract/add review index {review_index} on page {page_num+1}: {e}")

    def __extract_info_from_review(
            self,
            review : WebElement) -> tuple[str, str, str, str] | None:
        try:
            username = review.find_element(By.CLASS_NAME, "user-title").text
            user_ref  = review.find_element(By.CLASS_NAME, "user-title-name").get_attribute("href")
            rating = self.__get_rating(review)

            review_text = review.find_element(By.CLASS_NAME, "comment").text
            movie_name = self.wait.until(
                EC.presence_of_element_located(
                    (By.CLASS_NAME, "film-header-name"))
            ).find_element(By.TAG_NAME, "h1").text

            print(f"✅ {username=} {rating=} {len(review_text or '')} chars {movie_name=}")
    
            return {
                "username" : username,
                "rating" : rating, 
                "review_text" : review_text, 
                "movie_name" : movie_name, 
                "user_ref" : user_ref
            }
        
        except Exception as e:
            print(f"[WARN] Rating not found for one review: {e}")
            return None
        
    def __get_rating(
            self,
            review : WebElement
            ) -> str | None:
        # I want to find rating of the user,
        # it is in format "stars stars-X" where X is number of stars
        pattern = re.compile(r"^stars stars-(\d)$")
        rating_element = WebDriverWait(review, 3).until(
            lambda r: r.find_element(By.CLASS_NAME, "star-rating")
        )
        subclasses = rating_element.find_elements(By.XPATH, ".//span[contains(@class, 'stars')]")
        for subclass in subclasses:
            match = pattern.match(subclass.get_attribute("class"))
            if match:
                break
        rating = match.group(1) if match else None

        return rating

    def __move_to_next_page(self, current_page) -> bool:
        for attempt in range(3):
            try:
                self.wait.until(
                    EC.presence_of_element_located((By.XPATH, f"//div[contains(@class, 'pagination')]//a[text()='{current_page+1}']"))
                )
                next_button = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, f"//div[contains(@class, 'pagination')]//a[text()='{current_page+1}']"))
                )
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_button)
                self.driver.execute_script("arguments[0].click();", next_button)
                return True
            except Exception as e:
                print(f"[WARN] Attempt {attempt+1}/3 to click page {current_page+1} failed: {e}")
        return False
        
    def __add_data_to_reviews_table(
            self,
            review_data : list[tuple[str, str, str, str, str]]) -> None:
        c = self.conn.cursor()
        # username, rating, review_text, movie_name
        # Create a table
        c.execute("""
            INSERT OR IGNORE INTO reviews (
                username,
                rating, 
                review_text, 
                movie_name,
                user_ref
            ) VALUES (?, ?, ?, ?, ?)
            """, 
            (review_data["username"],
            review_data["rating"],
            review_data["review_text"],
            review_data["movie_name"],
            review_data["user_ref"]
            )
        )
        self.conn.commit()

    def __add_data_to_movies_table(
            self,
            movie_name : str,
            genre : str,
            average_rating : float) -> None:
        c = self.conn.cursor()
        c.execute("""
            INSERT OR IGNORE INTO movies (
                movie_name,
                genre,
                average_rating
            ) VALUES (?, ?, ?)""",
            (movie_name, genre, average_rating))
        self.conn.commit()