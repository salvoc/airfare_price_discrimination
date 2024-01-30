import logging
from flights_scraper import FlightsScraper
from Itinerary import Itinerary
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By

class Easyjet_Scraper(FlightsScraper):

    def __init__(self, userprofile:str):
        self.airline = "EASYJET"
        super().__init__(userprofile)
        
    def flights_search(self, itinerary: Itinerary):
        
        COOKIES_ACCEPT_BUTTON = (By.ID, "ensCloseBanner")
        ONE_WAY_BUTTON = (By.ID, "one-way")
        ORIGIN_FIELD = (By.XPATH, "//*[@name='origin']")
        DESTINATION_FIELD = (By.XPATH, "//*[@name='destination']")
        DATE_PICKER_BUTTON = (By.CLASS_NAME, "route-date-picker-control")
        OUTBOUND_DATE = (By.XPATH, f"//*[@data-date='{itinerary.outbound_date}']")
        INBOUND_DATEPICKER_BUTTON = (By.XPATH, f"//*[@data-tab='Date Calendar Return']//*[@data-date='{itinerary.inbound_date}']/a")
        INBOUND_DATE = (By.XPATH, f"//*[@data-id='{itinerary.inbound_date}']")
        ADULTS_FIELD = (By.XPATH, "//*[@name='Adults']")
        CHILDREN_FIELD = (By.XPATH, "//*[@name='Children']")
        INFANTS_FIELD = (By.XPATH, "//*[@name='Infants']")
        SEARCH_FLIGHTS_BUTTON = (By.CLASS_NAME, "search-submit")

        logging.info(f'Request to search Easyjet endpoint: {itinerary.logLine()}')

        self.driver.get('https://www.easyjet.com')
        
        oneWay = itinerary.inbound_date == "0000-00-00"
            
        self.human_click(COOKIES_ACCEPT_BUTTON)

        self.human_click(ORIGIN_FIELD)
        self.human_type(itinerary.origin + Keys.RETURN)
        
        self.human_click(DESTINATION_FIELD)
        self.human_type(itinerary.destination + Keys.RETURN)
        
        one_way_checkbox:WebElement = self.wait_for_clickable_element(ONE_WAY_BUTTON)
        one_way_checkbox_checked = "true" in one_way_checkbox.get_attribute("aria-checked")
        
        if oneWay != one_way_checkbox_checked:
            self.human_click(ONE_WAY_BUTTON)

        self.human_click(DATE_PICKER_BUTTON)
        self.human_click(OUTBOUND_DATE)
        
        if not oneWay:
            self.human_click(INBOUND_DATEPICKER_BUTTON)
            self.human_click(INBOUND_DATE)
        
        self.human_click(ADULTS_FIELD)
        self.human_type(Keys.BACKSPACE*2 + Keys.DELETE*2 + f"{int(itinerary.num_adults)}" + Keys.RETURN)

        self.human_click(CHILDREN_FIELD)
        self.human_type( Keys.BACKSPACE*2 + Keys.DELETE*2 + f"{int(itinerary.num_children) + int(itinerary.num_yadults)}" + Keys.RETURN)
        
        self.human_click(INFANTS_FIELD)
        self.human_type(Keys.BACKSPACE*2 + Keys.DELETE*2 + f"{int(itinerary.num_infants)}" + Keys.RETURN)

        self.human_click(SEARCH_FLIGHTS_BUTTON)
        
        pass
    
    
    def flights_scrape(self, itinerary: Itinerary):

        FLIGHT_SUMMARY = (By.CLASS_NAME, "flight-grid-window")
        
        self.flights_search(itinerary)
        
        #manage the newly opened window, if any
        handles = self.driver.window_handles
        self.driver.switch_to.window(handles[len(handles) - 1])

        result = self.wait_for_clickable_element(FLIGHT_SUMMARY)

        if (result == False):
            self.log_no_flights_found()
        else:
            self.save_html_content(self.build_filename(itinerary), result.get_attribute("outerHTML"))
        
        pass