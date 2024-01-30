import datetime
import logging
import time
from flights_scraper import FlightsScraper
from Itinerary import Itinerary
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By

class Vueling_Scraper(FlightsScraper):

    def __init__(self, userprofile:str):
        self.airline = "VUELING"
        super().__init__(userprofile)
        
    def flights_search(self, itinerary: Itinerary):
        
        COOKIES_ACCEPT_BUTTON = (By.ID, "onetrust-accept-btn-handler")
        ORIGIN_FIELD = (By.ID, "originInput")
        DESTINATION_FIELD = (By.ID, "destinationInput")
        ONE_WAY_BUTTON = (By.ID, "onewayList")

        outbound = datetime.datetime.strptime(itinerary.outbound_date,"%Y-%m-%d")
        OUTBOUND_DATE = (By.XPATH, f"//*[@data-year='{outbound.year}' and @data-month='{outbound.month - 1}']/a[contains(text(),' {outbound.day} ')]")
        
        if itinerary.inbound_date == "0000-00-00":
            inbound = False
        else:
            inbound = datetime.datetime.strptime(itinerary.inbound_date,"%Y-%m-%d")
            INBOUND_DATE = (By.XPATH, f"//*[@data-year='{inbound.year}' and @data-month='{inbound.month - 1}']/a[contains(text(),' {inbound.day} ')]")

        PAX_SELECTOR = (By.TAG_NAME, "vy-pax-selector")
        ADULTS_DECREASE_BUTTON = (By.ID, "adultsDecrease")
        ADULTS_INCREASE_BUTTON = (By.ID, "adultsIncrease")
        CHILDREN_DECREASE_BUTTON = (By.ID, "childrenDecrease")
        CHILDREN_INCREASE_BUTTON = (By.ID, "childrenIncrease")
        INFANTS_DECREASE_BUTTON = (By.ID, "infantsDecrease")
        INFANTS_INCREASE_BUTTON = (By.ID, "infantsIncrease")
        SEARCH_FLIGHTS_BUTTON = (By.ID, "btnSubmitHomeSearcher")

        logging.info(f'Request to search Vueling endpoint: {itinerary.logLine()}')

        self.driver.get('https://www.vueling.com/')
        
        #accept all cookies
        self.human_click(COOKIES_ACCEPT_BUTTON)
        
        self.human_click(ORIGIN_FIELD)
        self.human_type(itinerary.origin + Keys.RETURN)
        
        self.human_click(DESTINATION_FIELD)
        self.human_type(itinerary.destination + Keys.RETURN)
        
        
        self.human_click(OUTBOUND_DATE)

        if inbound:
            self.human_click(INBOUND_DATE)
        else:
            self.human_click(ONE_WAY_BUTTON)

        self.human_click(PAX_SELECTOR)
        
        #reset adult number
        adult_decrease_button:WebElement = self.wait_for_clickable_element(ADULTS_DECREASE_BUTTON)
        
        while adult_decrease_button and adult_decrease_button.get_attribute("aria-disabled")=="false":
            self.human_click( adult_decrease_button )
        
        for i in range(0,int(itinerary.num_adults) + int(itinerary.num_yadults)):
            self.human_click(ADULTS_INCREASE_BUTTON)
            
        #reset child number
        children_decrease_button:WebElement = self.wait_for_clickable_element(CHILDREN_DECREASE_BUTTON)
        while children_decrease_button and children_decrease_button.get_attribute("aria-disabled")=="false":
            self.human_click( children_decrease_button )
        
        for i in range(0,int(itinerary.num_children)):
            self.human_click(CHILDREN_INCREASE_BUTTON)
            
        #reset infant number
        infant_decrease_button:WebElement = self.wait_for_clickable_element(INFANTS_DECREASE_BUTTON)
        while infant_decrease_button and infant_decrease_button.get_attribute("aria-disabled")=="false":
            self.human_click( infant_decrease_button )

        for i in range(0,int(itinerary.num_infants)):
            self.human_click(INFANTS_INCREASE_BUTTON)

        self.human_click(SEARCH_FLIGHTS_BUTTON)
        
        pass
        
    
    def flights_scrape(self, itinerary: Itinerary):
        
        FLIGHT_SUMMARY = (By.ID, "flightCardsContainer")

        self.flights_search(itinerary)
        
        #manage the newly opened window, if any
        handles = self.driver.window_handles
        self.driver.switch_to.window(handles[len(handles) - 1])

        #allow to load results
        time.sleep(15)
        
        result = self.wait_for_clickable_element(FLIGHT_SUMMARY)

        if (result == False):
            self.log_no_flights_found()
        else:
            self.save_html_content(self.build_filename(itinerary), result.get_attribute("outerHTML"))
        pass
        
