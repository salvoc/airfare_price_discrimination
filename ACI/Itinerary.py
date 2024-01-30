class Itinerary:
    def __init__(self, 
                 origin: str, 
                 destination: str, 
                 outbound_date: str, 
                 inbound_date: str, 
                 num_adults: int, 
                 num_yadults: int, 
                 num_children: int, 
                 num_infants: int):
        self.origin = origin
        self.destination = destination
        self.outbound_date = outbound_date
        self.inbound_date = inbound_date
        self.num_adults = num_adults
        self.num_yadults = num_yadults
        self.num_children = num_children
        self.num_infants = num_infants 
        
    def logLine(self):
        return f"{self.origin} {self.destination} {self.outbound_date} {self.inbound_date} {self.num_adults} {self.num_yadults} {self.num_children} {self.num_infants}"
        