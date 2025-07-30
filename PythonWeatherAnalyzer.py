from datetime import datetime
from meteostat import Daily, Hourly, Stations
import pandas as pd

# Setup
start = datetime(1900, 7, 23)
end = datetime(2025, 12, 31)
latitude = 52.2297
longitude = 21.0122
max_distance = 50000
daily_dates = pd.date_range(start=start, end=end, freq='D')
timeline_df = pd.DataFrame(index=daily_dates, columns=['source_type', 'station', 'tmax'])
target_day = int(input("\n\nEnter the target day you want to find out the max temperature for: "))
target_month = int(input("Enter the month you want to look up: "))
monthno_toname = {1 : 'January',  2 : 'February', 3 : 'March', 4 : 'April', 5 : 'May', 6 : 'June', 7 : 'July', 8 : 'August', 9 : 'September' , 10 : 'October' , 11 : 'November' , 12 : 'December'}
all_daily_data = {}
all_hourly_data = {}


def getStations(lat, lon, d):

    '''Identify stations to be used for data'''

    stations = Stations()
    stations = stations.nearby(lat, lon)
    stations_set = stations.fetch(10)
    stations_set = stations_set[stations_set['distance'] < d]

    return(stations_set)






def getData():

    '''Fetch all the data from the selected stations'''

    print('\n\n')
    for station in stations_set.index:
        print(f"Fetching all data for {station}...")
        all_daily_data[station] = Daily(station, start, end).fetch()
        all_hourly_data[station] = Hourly(station, start, end).fetch()
    print('\n\n-----------------------------------------------------------------------------------------------------------------------')






def fetchDailyMaxTemp(date, stationID):

    '''Helper function called to take in values from Daily dataframe and return a concrete maximum temperature'''

    try:
        temp = all_daily_data[stationID].loc[date, 'tmax']
        return temp
    except KeyError:
        return None

    


def fetchDailyfromHourly(date, stationID):

    '''Helper function called to take in values from Hourly dataframe and return a concrete maximum temperature'''

    try:
        station_df = all_hourly_data[stationID]
        temp = station_df.loc[date.date(), 'temp'].max()
        return temp
    except (KeyError, ValueError):
        return None

    



def initTimeline(timeline_df, stations_set):

    '''Function used to create the timeline dataframe and fill it with maximum temperatures recorded for each day'''

    for time in timeline_df.index:
        temp_value = None  

        for station_index, station_data in stations_set.iterrows():
            
            if station_data['daily_start'] <= time <= station_data['daily_end']:
                temp_value = fetchDailyMaxTemp(time, station_index)

            
            if pd.isna(temp_value) and (station_data['hourly_start'] <= time <= station_data['hourly_end']):
                temp_value = fetchDailyfromHourly(time, station_index)

        
            if pd.notna(temp_value):
                break
        
        timeline_df.loc[time, 'tmax'] = temp_value
            



stations_set = getStations(latitude, longitude, max_distance)
getData()
initTimeline(timeline_df, stations_set)
is_correct_day = (timeline_df.index.month == target_month) & \
                 (timeline_df.index.day == target_day)
specific_day_df = timeline_df[is_correct_day]
max_temp_on_day = specific_day_df['tmax'].max()
date_of_max_temp = specific_day_df['tmax'].idxmax()






print(f'\n\nStations used for the data: \n {stations_set}')
print('\n\n-----------------------------------------------------------------------------------------------------------------------')
print(f"\n\nTemperatures for {monthno_toname[target_month]} {target_day} across all available years:")
print(f'\n{specific_day_df}')
print('\n\n-----------------------------------------------------------------------------------------------------------------------')
print(f"\nThe highest temperature recorded on any {monthno_toname[target_month]} {target_day} was {max_temp_on_day}°C, which occurred in {date_of_max_temp.year}.")
print('\n-----------------------------------------------------------------------------------------------------------------------')
print('End of report\n\n\n')


#Export everything to CSV for debugging
#timeline_df.to_csv('C:/Users/yauhenit/Desktop/weather_timeline.csv', mode='w')






