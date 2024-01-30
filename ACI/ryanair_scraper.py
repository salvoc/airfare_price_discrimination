import logging
import time
from selenium.webdriver.common.by import By
from flights_scraper import FlightsScraper
from Itinerary import Itinerary

class Ryanair_Scraper(FlightsScraper):

    def __init__(self, userprofile:str):
        self.airline = "RYANAIR"
        super().__init__(userprofile)


    def flights_search(self,itinerary: Itinerary):

        COOKIES_ACCEPT_BUTTON = (By.XPATH, "//*[@data-ref='cookie.accept-all']")
        ONE_WAY_BUTTON = (By.XPATH, "//*[@data-ref='flight-search-trip-type__one-way-trip']")
        DEPARTURE_FIELD = (By.XPATH, "//*[@uniqueid='departure']")
        CLEAR_DEPARTURE_FIELD = (By.CLASS_NAME, "list__clear-selection")
        ORIGIN_AIRPORT_BUTTON = (By.XPATH, f"//*[@data-id='{itinerary.origin}']")
        DESTINATION_AIRPORT_BUTTON = (By.XPATH, f"//*[@data-id='{itinerary.destination}']")
        OUTBOUND_DATE = (By.XPATH, f"//*[@data-id='{itinerary.outbound_date}']")
        NEXT_MONTH_BUTTON = (By.XPATH, "//*[@data-ref='calendar-btn-next-month']")
        INBOUND_DATE = (By.XPATH, f"//*[@data-id='{itinerary.inbound_date}']")
        INCREASE_ADULTS_BUTTON = (By.XPATH, f"//*[@aria-label='1Adults+1']/..")
        INCREASE_YADULTS_BUTTON = (By.XPATH, f"//*[@aria-label='0Teens+1']/..")
        INCREASE_CHILDREN_BUTTON = (By.XPATH, f"//*[@aria-label='0Children+1']/..")
        INCREASE_INFANTS_BUTTON = (By.XPATH, f"//*[@aria-label='0Infant+1']/..")
        SEARCH_FLIGHTS_BUTTON = (By.XPATH, "//*[@data-ref='flight-search-widget__cta']")

        logging.info(f'Request to search Ryanair endpoint: {itinerary.logLine()}')

        self.driver.get('https://www.ryanair.com/')
        
        self.human_click(COOKIES_ACCEPT_BUTTON)
        
        oneWay = itinerary.inbound_date == "0000-00-00"
        if oneWay:
            self.human_click(ONE_WAY_BUTTON)

        self.human_click(DEPARTURE_FIELD)
        self.human_click(CLEAR_DEPARTURE_FIELD)
        self.human_click(DEPARTURE_FIELD)
        self.human_type(itinerary.origin )
        self.human_click(ORIGIN_AIRPORT_BUTTON)
        
        self.human_type(itinerary.destination )
        self.human_click(DESTINATION_AIRPORT_BUTTON)
        
        for i in range(10):
            outbound_date_button = self.wait_for_clickable_element(OUTBOUND_DATE, timeout=10)
            if (outbound_date_button == False):
                self.human_click(NEXT_MONTH_BUTTON)
            else:
                self.human_click(outbound_date_button )
                break
        
        if not oneWay:
            for i in range(10):
                inbound_date_button = self.wait_for_clickable_element(INBOUND_DATE, timeout=10)
                if (inbound_date_button == False):
                    self.human_click(NEXT_MONTH_BUTTON)
                else:
                    self.human_click(inbound_date_button )
                    break
        
        
        for i in range(1,int(itinerary.num_adults)):
            self.human_click(INCREASE_ADULTS_BUTTON)
            
        for i in range(0,int(itinerary.num_yadults)):
            self.human_click(INCREASE_YADULTS_BUTTON)
            
        for i in range(0,int(itinerary.num_children)):
            self.human_click(INCREASE_CHILDREN_BUTTON)
            
        for i in range(0,int(itinerary.num_infants)):
            self.human_click(INCREASE_INFANTS_BUTTON)

        self.human_click(SEARCH_FLIGHTS_BUTTON)
        
        pass
        
        
        
    def flights_scrape(self, itinerary: Itinerary):

        FLIGHT_CARD = (By.TAG_NAME, "flight-card-new")
        FLIGHT_SUMMARY = (By.TAG_NAME, "flights-summary")
        
        self.flights_search(itinerary)
        
        self.wait_for_clickable_element(FLIGHT_CARD)
        time.sleep(5)
        
        result = self.wait_for_clickable_element(FLIGHT_SUMMARY)
    
        if (result == False):
            self.log_no_flights_found()
        else:
            self.save_html_content(self.build_filename(itinerary), result.get_attribute("outerHTML"))
        pass
