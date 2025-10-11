from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import re

def scrap_CSFD_reviews(movie_url: str) -> list[str]:
    """Scrape reviews from a CSFD movie page."""
    # Set up Chrome options
    chrome_options = Options()
   # chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Set up the Chrome driver
    service = Service('chromedriver.exe')  # Update with your chromedriver path
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        # Navigate to the URL
        driver.get(movie_url)
        time.sleep(0.5)  # Wait for the page to load
        driver.find_element(By.ID, "didomi-notice-agree-button").click()
        next_page = True
        pagination = driver.find_element(By.CLASS_NAME, "pagination")

        while next_page:
            reviews = driver.find_elements(By.CSS_SELECTOR, "article.article.article-white")
            # Example: Extract all paragraph texts from the page
            for review in reviews:
                username = review.find_element(By.CLASS_NAME, "user-title").text
                print("Username:", username)  # Print the text of each review
                # I want to find rating of the user, it is in format "stars stars-X" where X is number of stars
                pattern = re.compile(r"^stars stars-(\d)$")
                # okey, star-rating has one subclass and it is in format stars stars-X, i want to find all subclasses and match pattern
                rating_element = review.find_element(By.CLASS_NAME, "star-rating")
                subclasses = rating_element.find_elements(By.XPATH, ".//span[contains(@class, 'stars')]") # This xpath selects all span elements that have a class containing 'stars'
                for subclass in subclasses:
                    match = pattern.match(subclass.get_attribute("class"))
                    if match:
                        print(f"Rating: {match.group(1)}")
                        break
                review_text = review.find_element(By.CLASS_NAME, "comment").text
                print("Text:", review_text)
                
                movie_name = driver.find_element(By.CLASS_NAME, "film-header-name").find_element(By.TAG_NAME, "h1").text
                print("Movie name:", movie_name)
                
            next_button = pagination.find_element(By.TAG_NAME, "a")
            if next_button is None or 'disabled' in next_button.get_attribute('class'):
                next_page = False
                break
            time.sleep(2)  # Wait before clicking the next button
            next_button.click()
            time.sleep(2)  # Wait for the page to load

            print("funguju")
            exit()

        return reviews

    finally:
        # Close the driver
        driver.quit()

def main():
    movie_url = 'https://www.csfd.cz/film/1069-batman/recenze/'  # Replace with the target URL
    data = scrap_CSFD_reviews(movie_url)

if __name__ == "__main__":
    main()