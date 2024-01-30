import abc
import datetime
import gzip
import io
import logging
import os

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from Itinerary import Itinerary

from human_emulator import HumanEmulator

class FlightsScraper(abc.ABC):
    """
    A class for scraping flight information from a website.
    """
    
    def __init__(self, userprofile:str):
        
        """
        Initialize the FlightScraper with user profile and data path.
        
        Args:
            userprofile (str): User profile information.
            data_path (str): Path to data directory.
        """
    
        self.userprofile = userprofile
        self.data_path = os.path.join(os.getcwd(), "data")

        chrome_options = webdriver.ChromeOptions()
        
        # Headless mode
        chrome_options.add_argument('--headless')
        
        # Setting the window size to 1600x1200
        chrome_options.add_argument('--window-size=1280,1600')
        
        #Disable sandbox mode to allow multiple tabs to interact if required. No security concerns as the browser is running in a container.
        chrome_options.add_argument('--no-sandbox')
        
        #Limit the cache size to 32MB to avoid excessive disk usage and transactions
        chrome_options.add_argument('--disk-cache-size=32000000')

        #Disable-dev-shm-usage flag to prevent Chrome from crashing
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        #Setting the user agent to a valid browser to avoid detection
        chrome_options.add_argument(f'--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36')
        
        # Adding argument to disable the AutomationControlled flag 
        chrome_options.add_argument("--disable-blink-features=AutomationControlled") 
        
        # Exclude the collection of enable-automation switches 
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"]) 
        
        # Turn-off userAutomationExtension 
        chrome_options.add_experimental_option("useAutomationExtension", False)
        
        #Setting the user profile if one is provided
        if "incognito" in self.userprofile:
            chrome_options.add_argument("--incognito")
        else:
            user_profile_path = os.path.join(self.data_path, "user-profiles", self.userprofile)
            chrome_options.add_argument(f'--user-data-dir={user_profile_path}')
        
        chrome_service = Service(ChromeDriverManager().install())
    
        self.driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

        # Use execute_cdp_cmd to clear the browser cache
        self.driver.execute_cdp_cmd("Network.clearBrowserCache", {})

        self.human_emulator = HumanEmulator(self.driver)
        
        # Changing the property of the navigator value for webdriver to undefined. Helps to avoid detection.
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})") 
        
    @abc.abstractmethod
    def flights_scrape(self, itinerary:Itinerary):
        pass
    
    @abc.abstractmethod
    def flights_search(self, itinerary:Itinerary):
        pass
    
    def visit_webpage(self, url:str):
        self.driver.get(url)
        
    def close_webpage(self):
        self.driver.close()
        
    def build_filename(self, itinerary:Itinerary):
        filename = (
            f"{self.userprofile}-"
            f"{self.airline}-"
            f"{itinerary.origin}-"
            f"{itinerary.destination}-"
            f"{itinerary.outbound_date}-"
            f"{itinerary.inbound_date}-"
            f"{itinerary.num_adults}-"
            f"{itinerary.num_yadults}-"
            f"{itinerary.num_children}-"
            f"{itinerary.num_infants}-"
            f"{datetime.datetime.now()}"
        )
        return filename
    
    def save_html_content(self, filename:str, html:str):
        
        screenshotpath = os.path.join(self.data_path, "scrape-pics", f"{filename}.png")
        self.driver.save_screenshot(f"{screenshotpath}")
            
        filepath = os.path.join(self.data_path, "scrape-data", f"{filename}.html")
        
        data = f"""
        <!DOCTYPE html>
        <html>
            <head>
                <title>{filename}</title>
            </head>
            <body>
                {html}
            </body>
        </html>
        """
        
        # Create a new file in memory
        file_in_memory = io.BytesIO(data.encode('utf-8'))  # gzip requires bytes-like object

        # Create a new gzip file and write the file in memory to it
        with gzip.open(f'{filepath}.gz', 'wb') as gz_file:
            gz_file.writelines(file_in_memory)
    
        pass

    def log_no_flights_found(self):

        log_screenshots_path = os.path.join(self.data_path, "logs", f"{self.userprofile}-{datetime.datetime.now()}.png")
        self.driver.save_screenshot(log_screenshots_path)
        logging.warning('No flights found')
        
        pass
    
    def wait_for_clickable_element (self, locator, timeout:int=5):
        return self.human_emulator.wait_for_clickable_element(locator, timeout)
    
    def wait_for_element (self, locator, timeout:int=5):
        return self.human_emulator.wait_for_element(locator, timeout)
            
    def human_click(self, element):
        self.human_emulator.human_click(element)

    def human_type(self, text):
        self.human_emulator.human_type(text)
