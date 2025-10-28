from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import re
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
import tqdm
import sqlite3
class Scrapper:
    def __init__(self):
        self.chrome_options = Options()
       # self.chrome_options.add_argument("--headless")  # Run in headless mode
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument("--load-extension=c:\\Users\\marti\\Documents\\practice_data\\adblocker\\chrome")  # Load your extension here


    def scrap_url_from_genres(
            self, 
            genres: list[tuple[str,bool]],
            number_of_movies_from_genre : int  = 5,
        ) -> list[str]:
        """Scrape URLs from CSFD genre pages."""
        # Set up the Chrome driver
        service = Service('chromedriver.exe')  # Update with your chromedriver path
        driver = webdriver.Chrome(service=service, options=self.chrome_options)

        try:
            all_urls = []
            for genre, only_genre in genres:
                genre_url = f'https://www.csfd.cz/podrobne-vyhledavani/?sort=rating_average/'
                driver.get(genre_url)
                time.sleep(0.5)  # Wait for the page to load
                if "didomi-notice-agree-button" in driver.page_source:
                    driver.find_element(By.ID, "didomi-notice-agree-button").click()
                genres_button = driver.find_element(By.ID, "complex-selects-genre-include")
                genre = genres_button.find_element(By.XPATH, f".//option[text()='{genre}']")
                genre.click()

                if only_genre:
                    filter = driver.find_element(By.ID, "frm-filmsForm-genre")
                    filter.find_element(By.XPATH, ".//option[@value='1']").click()
                print("genre clicked: ",genre.get_attribute('text'))
                time.sleep(0.5)  # Wait for the elements to be found

                driver.find_element(By.XPATH, "//button[@class='icon-in-left']").click()
                time.sleep(0.5)  # Wait for the elements to be found
                results = driver.find_elements(By.XPATH, "//a[@class='film-title-name']")
                urls = [results[i].get_attribute('href') for i in range(min(number_of_movies_from_genre,len(results)))]
                all_urls.extend(urls)
        
            return all_urls

        finally:
            # Close the driver
            driver.quit()

    def scrap_url_from_searches(
            self, 
            queries: list[str],
            path :str,
            how_many : int = 5
        ) -> list[str]:
        """Scrape URLs from CSFD search results."""

        # Set up the Chrome driver
        service = Service('chromedriver.exe')  # Update with your chromedriver path
        driver = webdriver.Chrome(service=service, options=self.chrome_options)

        try:
            all_urls = []
            for query in queries:
                search_url = f'https://www.csfd.cz/hledat/?q={query.replace(" ", "+")}'
                driver.get(search_url)
                time.sleep(0.5)  # Wait for the page to load
                if "didomi-notice-agree-button" in driver.page_source:
                    driver.find_element(By.ID, "didomi-notice-agree-button").click()
                results = driver.find_elements(By.XPATH, path)
                time.sleep(0.5)  # Wait for the elements to be found
                urls = [result.get_attribute('href') for result in results]
                urls = urls[:how_many]
                all_urls.extend(urls)
            return all_urls

        finally:
            # Close the driver
            driver.quit()

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
    
    def get_user_data(
        self,user_list : list[str],
        cursor : sqlite3.Cursor
        ) -> None:
        """ Get user data from CSFD user pages.
            We will scrape data about:
            - username
            - total reviews
            - age of account
            - where is user from
        """
        for username in user_list:
            try:
                actual_username = self.scrap_url_from_searches(
                    [username], 
                    path = "//a[@class='user-title-name']",
                    how_many = 1
                )
                data_point = self.__scrap_user_data_from_page(actual_username[0])
                if data_point:
                    cursor.execute("""
                        INSERT OR IGNORE INTO users (username, total_reviews, since_when, place)
                        VALUES (?, ?, ?, ?)
                    """, (
                        data_point["username"],
                        data_point["total_reviews"],
                        data_point["since_when"],
                        data_point["place"]
                    ))
                    print(f"Inserted data for user {username}")
                    cursor.connection.commit()
            except Exception as e:
                print(f"[WARN] Could not find user {username}: {e}")

    def __scrap_user_data_from_page(self, url: str) -> list[dict]:
        """ Scrape user data from CSFD user pages.
            We will scrape data about:
            - username
            - total reviews
            - age of account
            - where is user from
        """
        service = Service('chromedriver.exe')  # Update with your chromedriver path
        driver = webdriver.Chrome(service=service, options=self.chrome_options)
        try:
            driver.get(url)
            time.sleep(0.5)  # Wait for the page to load
            if "didomi-notice-agree-button" in driver.page_source:
                driver.find_element(By.ID, "didomi-notice-agree-button").click()
                # Implementation would go her
            content = driver.find_element(By.CLASS_NAME, "user-profile-content")

            username = content.find_element(By.XPATH, "//h1").text
            since_when_present = int(
                content.find_elements(By.XPATH, "//div[@class='user-profile-footer-left']")\
                [0].text.split()[3].split(".")[2]
            )
            place = self.extract_place_from_profile(driver)          
            sec = driver.find_element(By.XPATH, "//section[@class='box box-user-rating striped-articles']")
            elem = sec.find_element(By.CSS_SELECTOR, ".count")
            raw = (elem.get_attribute("textContent") or elem.text or "").strip()
            # raw will be like "(6\u00A0106)" or "(6 106)" or "6,106"

            # Remove parentheses and surrounding whitespace
            raw = raw.strip().lstrip("(").rstrip(")")

            # Remove non-digit characters (spaces, NBSP, commas, etc.) and keep digits only
            digits = re.sub(r"[^\d]", "", raw)

            count = int(digits) if digits else 0
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
    def extract_place_from_profile(self,driver,timeout= 8):
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