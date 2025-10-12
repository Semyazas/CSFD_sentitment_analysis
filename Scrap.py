from ast import pattern
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import re
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement

class Scrapper:
    def __init__(self):
        self.chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Run in headless mode
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument("--load-extension=c:\\Users\\marti\\Documents\\practice_data\\adblocker\\chrome")  # Load your extension here


    def scrap_url_from_searches(self, queries: list[str]) -> list[str]:
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
                results = driver.find_elements(By.XPATH, "//a[@class='film-title-name']")
                time.sleep(0.5)  # Wait for the elements to be found
                urls = [result.get_attribute('href') for result in results]
                all_urls.extend(urls)
            return all_urls

        finally:
            # Close the driver
            driver.quit()

    def scrap_CSFD_reviews_from_movie(self, movie_url: str) -> list[str]:
        """Scrape reviews from a CSFD movie page."""

        service = Service('chromedriver.exe')  # Update with your chromedriver path
        driver = webdriver.Chrome(service=service, options=self.chrome_options)
        wait = WebDriverWait(driver, 3000)
        try:
            driver.get(movie_url)
            time.sleep(0.5)  # Wait for the page to load
            driver.find_element(By.ID, "didomi-notice-agree-button").click()
            next_page = True
            current_page = 1

            while next_page:
                reviews = driver.find_elements(By.CSS_SELECTOR, "article.article.article-white")
                for review in reviews: 
                    result = self.extract_info_from_review(review, current_page, driver, wait)
                   
                self.move_to_next_page(driver, wait, current_page )
                print(f"--- End of page {current_page} ---")
                current_page += 1
            return reviews

        finally:
            driver.quit()

    def extract_info_from_review(self, 
            review : WebElement, 
            current_page : int,
            driver : webdriver.Chrome, 
            wait : WebDriverWait) \
        -> tuple[str, str, str, str] | None: 

        username = review.find_element(By.CLASS_NAME, "user-title").text
        print("Username:", username)  
        # I want to find rating of the user, it is in format "stars stars-X" where X is number of stars
        pattern = re.compile(r"^stars stars-(\d)$")
        try:
            rating_element = WebDriverWait(review, 3).until(
                lambda r: r.find_element(By.CLASS_NAME, "star-rating")
            )
            subclasses = rating_element.find_elements(By.XPATH, ".//span[contains(@class, 'stars')]") 
            for subclass in subclasses:
                match = pattern.match(subclass.get_attribute("class"))
                if match:
                    print(f"Rating: {match.group(1)}")
                    break
            review_text = review.find_element(By.CLASS_NAME, "comment").text
            print("Text:", review_text)

            movie_name = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "film-header-name"))).find_element(By.TAG_NAME, "h1").text
            print("Movie name:", movie_name)
            return username, match.group(1), review_text, movie_name
        
        except Exception as e:
            print(f"[WARN] Rating not found for one review: {e}")
            rating_element = None                    
            driver.save_screenshot(f"debug_page_{current_page}.png")
            return None
        
    def move_to_next_page(self, driver : webdriver.Chrome, wait : WebDriverWait , current_page : int) -> bool:
        """Move to the next page of reviews if available."""
        time.sleep(2)  # Wait before clicking the next button
                
        try:
            next_page_button = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, f"//div[contains(@class, 'pagination')]//a[contains(text(), '{current_page}')]")
                )
            )
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_page_button)
            time.sleep(0.3)
            driver.execute_script("arguments[0].click();", next_page_button)
            print(f"[INFO] Clicked page {current_page}")
            return True
        
        except Exception as e:
            print(f"[ERROR] Could not click page {current_page}: {e}")
            driver.save_screenshot(f"debug_page_{current_page}.png")
            time.sleep(2)  # Wait for the page to load
            return False

def main():
    scrapper = Scrapper()
    queries = ["Batman", "Superman"]
    movies = scrapper.scrap_url_from_searches(queries)
    print(movies)
    for movie_url in movies:
        print(f"Scraping reviews for movie: {movie_url}")
        data = scrapper.scrap_CSFD_reviews_from_movie(movie_url + "recenze/")

if __name__ == "__main__":
    main()