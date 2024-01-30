import pandas as pd
from datetime import timedelta

class APDAnalyzer:

    def __init__(self):
        pass

    @staticmethod
    def checkForPriceDifferences():
        
        # Read the CSV file
        flight_data = pd.read_csv("data\output\output.csv")
      
        # Parse the datetime column (assumed to be the 10th column)
        flight_data['search_datetime'] = pd.to_datetime(flight_data.iloc[:, 9])
        flight_data = flight_data.sort_values(by='search_datetime')

        # Assign session IDs
        session_ids = []
        current_session_id = 0
        current_session_start = (flight_data['search_datetime'].iloc[0]).floor('H')

        for index, row in flight_data.iterrows():
            if row['search_datetime'] < current_session_start + timedelta(hours=1):
                session_ids.append(current_session_id)
            else:
                current_session_id += 1
                current_session_start = row['search_datetime'].floor('H')
                session_ids.append(current_session_id)

        flight_data['session_id'] = session_ids

        # Identify sessions with price variations
        grouped_data = flight_data.groupby(['session_id', flight_data.iloc[:, 11]])
        price_variations = {k: v.iloc[:, 12].unique() for k, v in grouped_data if len(v.iloc[:, 12].unique()) > 1}
        sessions_with_variations = [k[0] for k in price_variations.keys()]

        # Analyze price variations within these sessions
        relevant_sessions_data = flight_data[flight_data['session_id'].isin(sessions_with_variations)]
        grouped_by_session_flight = relevant_sessions_data.groupby(['session_id', relevant_sessions_data.iloc[:, 11]])

        price_differences = []
        for (session_id, flight_number), group in grouped_by_session_flight:
            if group.iloc[:, 12].nunique() > 1:
                session_start = group['search_datetime'].min().floor('H')
                for profile in group.iloc[:, 10].unique():
                    profile_price = group[group.iloc[:, 10] == profile].iloc[:, 12].unique()[0]
                    price_differences.append((session_id, session_start, flight_number, profile, profile_price))

        print( pd.DataFrame(price_differences, columns=['Session ID', 'Session Start', 'Flight Number', 'Profile', 'Price']))

