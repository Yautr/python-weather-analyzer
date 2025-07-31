from datetime import datetime
import pandas as pd
from meteostat import Daily, Hourly, Stations
from typing import Dict

# --- Configuration Constants ---
LATITUDE = 52.2297
LONGITUDE = 21.0122
MAX_DISTANCE_METERS = 50000
START_DATE = datetime(1900, 7, 23)
END_DATE = datetime(2025, 12, 31)
MONTH_NAMES = {
    1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June',
    7: 'July', 8: 'August', 9: 'September', 10: 'October', 11: 'November', 12: 'December'
}

def get_stations(lat: float, lon: float, max_dist: int) -> pd.DataFrame:
    """
    Fetches a DataFrame of weather stations within a given distance from a location.
    
    Args:
        lat: Latitude of the location.
        lon: Longitude of the location.
        max_dist: Maximum distance in meters to search for stations.
        
    Returns:
        A pandas DataFrame of nearby stations.
    """
    stations = Stations()
    stations = stations.nearby(lat, lon)
    stations_df = stations.fetch(10)  # Fetch top 10 closest
    return stations_df[stations_df['distance'] < max_dist]

def fetch_all_data(stations_df: pd.DataFrame, start: datetime, end: datetime) -> tuple[Dict, Dict]:
    """
    Fetches all daily and hourly data for the provided list of stations.

    Args:
        stations_df: DataFrame of stations to fetch data for.
        start: The start date for the data fetch.
        end: The end date for the data fetch.

    Returns:
        A tuple containing two dictionaries: (all_daily_data, all_hourly_data).
    """
    print('\nFetching data for all stations...')
    all_daily_data = {}
    all_hourly_data = {}
    for station_id in stations_df.index:
        print(f"  -> Fetching data for station {station_id}...")
        all_daily_data[station_id] = Daily(station_id, start, end).fetch()
        all_hourly_data[station_id] = Hourly(station_id, start, end).fetch()
    print('Data fetching complete.')
    return all_daily_data, all_hourly_data

def create_weather_timeline(
    stations_df: pd.DataFrame, 
    daily_data: Dict, 
    hourly_data: Dict, 
    start: datetime, 
    end: datetime
) -> pd.DataFrame:
    """
    Creates a single timeline of the maximum daily temperature, trying multiple sources.

    Args:
        stations_df: DataFrame of available weather stations.
        daily_data: Dictionary of daily data from stations.
        hourly_data: Dictionary of hourly data from stations.
        start: The start date for the timeline.
        end: The end date for the timeline.

    Returns:
        A pandas DataFrame with a single 'tmax' column for the entire date range.
    """
    print('\nBuilding weather timeline...')
    date_range = pd.date_range(start=start, end=end, freq='D')
    timeline_df = pd.DataFrame(index=date_range)
    
    # Pre-calculate max hourly temps to speed up the main loop
    max_hourly_temps = {
        station_id: df['temp'].resample('D').max()
        for station_id, df in hourly_data.items()
        if not df.empty
    }

    tmax_values = []
    for date in timeline_df.index:
        temp_value = None
        for station_id, station_info in stations_df.iterrows():
            # Try to get data from the daily records first
            if station_info['daily_start'] <= date <= station_info['daily_end']:
                try:
                    temp_value = daily_data[station_id].loc[date, 'tmax']
                    if pd.notna(temp_value):
                        break
                except KeyError:
                    pass
            
            # If not found, try to get it from the hourly records
            if station_info['hourly_start'] <= date <= station_info['hourly_end']:
                try:
                    temp_value = max_hourly_temps[station_id].get(date)
                    if pd.notna(temp_value):
                        break
                except KeyError:
                    pass

        tmax_values.append(temp_value)
    
    timeline_df['tmax'] = tmax_values
    print('Timeline built successfully.')
    return timeline_df

def get_user_input() -> tuple[int, int]:
    """Gets the target day and month from the user."""
    day = int(input("\nEnter the target day you want to find out the max temperature for: "))
    month = int(input("Enter the month you want to look up: "))
    return day, month

def analyze_and_display_results(timeline_df: pd.DataFrame, day: int, month: int):
    """
    Filters the timeline for a specific day and prints the analysis.

    Args:
        timeline_df: The complete weather timeline DataFrame.
        day: The target day of the month.
        month: The target month.
    """
    is_specific_day = (timeline_df.index.month == month) & (timeline_df.index.day == day)
    specific_day_df = timeline_df[is_specific_day].dropna()

    if specific_day_df.empty:
        print(f"\nSorry, no temperature data could be found for {MONTH_NAMES[month]} {day}.")
        return

    max_temp_on_day = specific_day_df['tmax'].max()
    date_of_max_temp = specific_day_df['tmax'].idxmax()

    print('\n' + '-'*80)
    print(f"\nTemperatures for {MONTH_NAMES[month]} {day} across all available years:")
    print(specific_day_df)
    print('\n' + '-'*80)
    print(f"\nThe highest temperature recorded on any {MONTH_NAMES[month]} {day} was {max_temp_on_day}°C, which occurred in {date_of_max_temp.year}.")
    print('-'*80)

# --- Main Execution Block ---

def main():
    """Main function to run the weather analysis script."""
    
    # 1. Get User Input
    target_day, target_month = get_user_input()

    # 2. Fetch Data
    nearby_stations = get_stations(LATITUDE, LONGITUDE, MAX_DISTANCE_METERS)
    print(f'\nFound {len(nearby_stations)} stations within {MAX_DISTANCE_METERS / 1000} km.')
    print(nearby_stations[['name', 'distance']])
    
    daily_data, hourly_data = fetch_all_data(nearby_stations, START_DATE, END_DATE)

    # 3. Process Data
    weather_timeline = create_weather_timeline(nearby_stations, daily_data, hourly_data, START_DATE, END_DATE)

    # 4. Analyze and Display Results
    analyze_and_display_results(weather_timeline, target_day, target_month)
    
    # Optional: Export for debugging
    # weather_timeline.to_csv('weather_timeline.csv')
    
    print('\nEnd of report.\n')


if __name__ == "__main__":
    main()