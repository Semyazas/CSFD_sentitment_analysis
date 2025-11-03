import time
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.common.by import By
from .AbsScrapper import AbsScrapper

class UrlFinder(AbsScrapper):
    def __init__(self):
        super().__init__()

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