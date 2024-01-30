import sys
import click
import requests
import logging

from flights_scraper import Itinerary
from easyjet_scraper import Easyjet_Scraper
from ryanair_scraper import Ryanair_Scraper
from jetblue_scraper import Jetblue_Scraper
from vueling_scraper import Vueling_Scraper
from apd_parser import APDParser
from apd_analyzer import APDAnalyzer

__author__ = "Salvo Cucinella"

def get_user_location(ip_address=None):
    if ip_address is None:
        # If IP address is not provided, it will automatically detect the public IP address
        response = requests.get('https://ipinfo.io')
    else:
        # If IP address is provided, it will fetch location for that IP
        response = requests.get(f'https://ipinfo.io/{ip_address}/json')

    # Parse the JSON response
    data = response.json()

    # Extract relevant information from the response
    ip = data.get('ip', 'N/A')
    city = data.get('city', 'N/A')
    region = data.get('region', 'N/A')
    country = data.get('country', 'N/A')
    location = data.get('loc', 'N/A')

    # Return the location information
    return {
        'IP Address': ip,
        'City': city,
        'Region': region,
        'Country': country,
        'Location': location
    }

@click.group()
def main():
    """
    Airline Price Discrimination CLI
    """
    pass

@main.command()
@click.argument('profile_name')
@click.argument('airline')
@click.argument('origin')
@click.argument('destination')
@click.argument('outbound_date')
@click.argument('inbound_date')
@click.argument('num_adults')
@click.argument('num_yadults')
@click.argument('num_children')
@click.argument('num_infants')
def scrape(profile_name, airline, origin, destination, outbound_date, inbound_date, num_adults, num_yadults, num_children, num_infants):
    """Scrape flight search results"""
    
    logging.basicConfig(level=logging.WARNING, stream=sys.stdout)
    
    if airline=='Ryanair':
        sc = Ryanair_Scraper(profile_name)
    elif airline=='Easyjet':
        sc = Easyjet_Scraper(profile_name)
    elif airline=='Vueling':
        sc = Vueling_Scraper(profile_name)
    elif airline=='Jetblue':
        sc = Jetblue_Scraper(profile_name)

    itinerary = Itinerary(origin, destination, outbound_date, inbound_date, num_adults, num_yadults, num_children, num_infants)
    
    sc.flights_scrape(itinerary)
    
    logging.info('Scraping complete.') 

@main.command()
def parseall():
    """Parse all results to CSV"""
    APDParser().parseAll()
    logging.info('Parsing complete.') 

@main.command()
def whereismyip():
    """Find my IP location"""
    user_location = get_user_location()
    print(user_location)
    logging.info(f'User location: {user_location}') 

@main.command()
def checkforpricedifferences():
    """Find Price differences in the same search"""
    APDAnalyzer().checkForPriceDifferences()
    logging.info(f'Checking for price differences') 

if __name__ == "__main__":
    main()
