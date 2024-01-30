import gzip
import os
from pathlib import Path
import sys
import unicodedata
import logging
from bs4 import BeautifulSoup

# INPUT_FOLDER_PATH = 'z:/scrape-data'
INPUT_FOLDER_PATH = os.path.join(os.getcwd(), "data", "scrape-data")

# OUTPUT_FILE_PATH = 'z:/output/output.csv'
OUTPUT_FILE_PATH = os.path.join(os.getcwd(), "data", "output", "output.csv")

CSV_SEPARATOR = ','

class SearchInfo:
        
    def __init__(self, file_path:str):
        
        #strip the .html.gz
        while file_path.suffix:
            file_path = file_path.with_suffix('')
            
        #normalize the filename and replace ? with :
        normalized_name = unicodedata.normalize('NFKD', file_path.name).encode('ASCII', 'replace').decode('ASCII')
        normalized_name = normalized_name.replace("?",":")

        (
            self.profile_name,
            self.airline_name,
            self.flight_origin,
            self.flight_destination,
            self.outbound_date_year,
            self.outbound_date_month,
            self.outbound_date_day,
            self.inbound_date_year,
            self.inbound_date_month,
            self.inbound_date_day,
            self.num_adults,
            self.num_yadults,
            self.num_children,
            self.num_infants,
            *search_date_parts
        ) = normalized_name.split("-")
        
        self.datetime = "-".join(search_date_parts).replace(" ","T")
        
    def toCSVstring(self, separator:str):
        return separator.join([
                            self.airline_name,
                            self.flight_origin,
                            self.flight_destination,
                            f"{self.outbound_date_year}-{self.outbound_date_month}-{self.outbound_date_day}",
                            f"{self.inbound_date_year}-{self.inbound_date_month}-{self.inbound_date_day}",
                            self.num_adults,
                            self.num_yadults,
                            self.num_children,
                            self.num_infants,
                            self.datetime,
                            self.profile_name
                        ])

class APDParser:

    def __init__(self):
        logging.basicConfig(level=logging.INFO, stream=sys.stdout)


    def parse_FR_prices(self, html_content:str):
        
        results = []
        soup = BeautifulSoup(html_content, 'html.parser')  
        flight_tags = soup.find_all("flight-card-new")

        for tag in flight_tags:
            flight_number = tag.find(class_="card-flight-num__content").text.strip().replace(" ", "")

            # the last price is the one we want
            flight_prices = tag.find_all("flights-price-simple")

            if len(flight_prices)>0:
                flight_price = flight_prices[-1].text.replace(",", ".").strip()
                results.append( f"{flight_number}{CSV_SEPARATOR}{flight_price}" )


        return results

    def parseAll(self):
        logging.info(f"Opening output file: {OUTPUT_FILE_PATH}")
        with open(OUTPUT_FILE_PATH, 'w', encoding='utf-8') as output_file:
            
        # Iterate over all files in the folder
            logging.info(f"Scanning source directory: {INPUT_FOLDER_PATH}")

            for file_path in Path(INPUT_FOLDER_PATH).iterdir():
                if file_path.name.endswith('.html.gz'):

                    search_info = SearchInfo(file_path)

                    # Read the HTML file
                    with gzip.open(file_path, 'rt', encoding='utf-8') as file:

                        if "RYANAIR" in search_info.airline_name.upper():
                            results = self.parse_FR_prices( file.read() )
                        else:
                            logging.error(f"The parser does not support airline {search_info.airline_name} - processing file: {file_path.name}")
                            continue

                    for price_data in results:
                        output_file.write( f"{search_info.toCSVstring(separator=CSV_SEPARATOR)}{CSV_SEPARATOR}{price_data}\n" )
                    
                    logging.info(f"{len(results)} flights found processing file: {file_path.name}")

