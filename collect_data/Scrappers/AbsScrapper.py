from selenium.webdriver.chrome.options import Options


class AbsScrapper:
    def __init__(self):
        self.chrome_options = Options()
       # self.chrome_options.add_argument("--headless")  # Run in headless mode
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument("--load-extension=c:\\Users\\marti\\Documents\\practice_data\\adblocker\\chrome")  # Load your extension here
