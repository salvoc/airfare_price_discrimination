import logging
from flights_scraper import FlightsScraper
from Itinerary import Itinerary
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By

class Jetblue_Scraper(FlightsScraper):

    def __init__(self, userprofile:str):
        self.airline = "JETBLUE"
        super().__init__(userprofile)
        
    def flights_search(self, itinerary: Itinerary):

        COOKIES_IFRAME = (By.CLASS_NAME, "truste_popframe")
        COOKIES_ACCEPT_BUTTON = (By.CLASS_NAME, "call")
        ORIGIN_FIELD = (By.XPATH, "//*[@data-qaid='fromAirport']//input")
        DESTINATION_FIELD = (By.XPATH, "//*[@data-qaid='toAirport']//input")
        TRIP_TYPE = (By.XPATH, "//*[@formcontrolname='tripType']")
        ONE_WAY_BUTTON = (By.XPATH, "//*[@data-qaid='OW']")
        RETURN_BUTTON = (By.XPATH, "//*[@data-qaid='RT']")
        OUTBOUND_DATE = (By.XPATH, "//*[@data-qaid='departDateInput']//input")
        INBOUND_DATE = (By.XPATH, "//*[@data-qaid='returnDateInput']//input")
        PAX_SELECTOR = (By.XPATH, "//*[@title='Travelers']")
        ADULTS_DECREASE_BUTTON = (By.XPATH, "//*[@aria-label='remove adult']")
        ADULTS_INCREASE_BUTTON = (By.XPATH, "//*[@aria-label='add adult']")
        CHILDREN_DECREASE_BUTTON = (By.XPATH, "//*[@aria-label='remove children']")
        CHILDREN_INCREASE_BUTTON = (By.XPATH, "//*[@aria-label='add children']")
        INFANTS_DECREASE_BUTTON = (By.XPATH, "//*[@aria-label='remove infant']")
        INFANTS_INCREASE_BUTTON = (By.XPATH, "//*[@aria-label='add infant']")
        SEARCH_FLIGHTS_BUTTON = (By.XPATH, "//*[@data-qaid='searchFlight']")

        logging.info(f'Request to search Jetblue endpoint: {itinerary.logLine()}')

        self.driver.get('https://www.jetblue.com/')
        
        iframe = self.wait_for_clickable_element(COOKIES_IFRAME, timeout=5)
        
        if (iframe != False):
            self.driver.switch_to.frame(iframe);

            self.human_click(COOKIES_ACCEPT_BUTTON)
        
            self.driver.switch_to.default_content();
        
        self.human_click(ORIGIN_FIELD)
        self.human_type(itinerary.origin + Keys.RETURN)
        
        self.human_click(DESTINATION_FIELD)
        self.human_type(itinerary.destination + Keys.RETURN)
        
        self.human_click(OUTBOUND_DATE)
        self.human_type(itinerary.outbound_date + Keys.RETURN)
        
        oneWay = itinerary.inbound_date == "0000-00-00"
        if oneWay:
            self.human_click(TRIP_TYPE)
            self.human_click(ONE_WAY_BUTTON)
        else:
            self.human_click(TRIP_TYPE)
            self.human_click(RETURN_BUTTON)
            self.human_click(INBOUND_DATE)
            self.human_type(itinerary.inbound_date + Keys.RETURN)

        self.human_click(PAX_SELECTOR)
        
        #reset adult number
        adult_decrease_button:WebElement = self.wait_for_element(ADULTS_DECREASE_BUTTON)
        while adult_decrease_button.is_enabled():
            self.human_click( adult_decrease_button )
        
        for i in range(0, int(itinerary.num_adults) + int(itinerary.num_yadults)):
            self.human_click(ADULTS_INCREASE_BUTTON)
            
        #reset child number
        children_decrease_button:WebElement = self.wait_for_element(CHILDREN_DECREASE_BUTTON)
        while children_decrease_button.is_enabled():
            self.human_click( children_decrease_button )
        
        for i in range(0, int(itinerary.num_children)):
            self.human_click(CHILDREN_INCREASE_BUTTON)
            
        #reset infant number
        infant_decrease_button:WebElement = self.wait_for_element(INFANTS_DECREASE_BUTTON)
        while infant_decrease_button.is_enabled():
            self.human_click( infant_decrease_button )
        
        for i in range(0, int(itinerary.num_infants)):
            self.human_click(INFANTS_INCREASE_BUTTON)

        self.human_click(SEARCH_FLIGHTS_BUTTON)
        
        pass
        
    
    def flights_scrape(self, itinerary: Itinerary):
        
        FLIGHT_SUMMARY = (By.TAG_NAME, "jb-flight-details")

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
