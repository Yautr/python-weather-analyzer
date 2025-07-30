# Import Meteostat library and dependencies
from datetime import datetime
import matplotlib.pyplot as plt
from meteostat import Point, Daily, Hourly, Stations
import pandas as pd

# Setup
start = datetime(1900, 7, 23)
end = datetime(2025, 12, 31)
latitude = 52.2297
longitude = 21.0122
max_distance = 50000
daily_dates = pd.date_range(start=start, end=end, freq='D')
timeline_df = pd.DataFrame(index=daily_dates, columns=['source_type', 'station', 'tmax'])
target_day = int(input("Enter the target day you want to find out the max temperature for"))
target_month = int(input("Enter the month you want to look up"))


def getStations(lat, lon, d, start, end):
    stations = Stations()
    stations = stations.nearby(lat, lon)
    stations_set = stations.fetch(10)
    stations_set = stations_set[stations_set['distance'] < d]

    return(stations_set)


stations_set = getStations(latitude, longitude, max_distance, start, end)
print(stations_set)

all_daily_data = {}
all_hourly_data = {}

def getData():
    for station in stations_set.index:
        print(f"Fetching all data for {station}")
        all_daily_data[station] = Daily(station, start, end).fetch()
        all_hourly_data[station] = Hourly(station, start, end).fetch()


getData()

def fetchDailyMaxTemp(date, stationID):
    try:
        temp = all_daily_data[stationID].loc[date, 'tmax']
        return temp
    except KeyError:
        return None

    


def fetchDailyfromHourly(date, stationID):
    try:
        station_df = all_hourly_data[stationID]
        temp = station_df.loc[date.date(), 'temp'].max()
        return temp
    except (KeyError, ValueError):
        return None

    





def initTimeline (timeline_df, stations_set):
    for time, row in timeline_df.iterrows():
        for station_index, station_data in stations_set.iterrows():
            if station_data['daily_start'] <= time <= station_data['daily_end']:
                timeline_df.loc[time, 'tmax'] = fetchDailyMaxTemp(time, station_index)
                break
            elif station_data['hourly_start'] <= time <= station_data['hourly_end']:
                timeline_df.loc[time, 'tmax'] = fetchDailyfromHourly(time, station_index)
            else:
                timeline_df.loc[time, 'tmax'] = 0
                continue
            


        

initTimeline(timeline_df, stations_set)

is_correct_day = (timeline_df.index.month == target_month) & \
                 (timeline_df.index.day == target_day)

specific_day_df = timeline_df[is_correct_day]

print(f"Temperatures for July 29th across all available years:")
print(specific_day_df)

max_temp_on_day = specific_day_df['tmax'].max()

# Find the full date of that max temperature
date_of_max_temp = specific_day_df['tmax'].idxmax()

print(f"\nThe highest temperature recorded on any July 29th was {max_temp_on_day}°C, which occurred in {date_of_max_temp.year}.")

print(f"{timeline_df.loc[:, 'tmax'].max()} and {timeline_df.loc[:, 'tmax'].idxmax()}")

timeline_df.to_csv('C:/Users/yauhenit/Desktop/weather_timeline.csv')






