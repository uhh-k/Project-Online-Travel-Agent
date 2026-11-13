import datetime
from datetime import datetime, date

import pandas as pd
import random

end_date = pd.to_datetime('today')
start_date = pd.Timestamp(2009, 5, 1)

# slowly changing dimension

def add_dimensions(src_data):
    sink_data = dict(src_data)
    sink_data['dim_time'] = create_dim_time()
    sink_data['dim_date'] = create_dim_date()
    return sink_data

def transform_time_columns(src_data):
    sink_data = dict(src_data)

    time_columns = {
        "fct_flight_booking": ("departure_time", "flight_duration"),
    }
    time_indexes = sink_data['dim_time']['instant']
    time_format = '%H:%M'

    for fct_table in time_columns:
        for time_column in time_columns[fct_table]:
            instants_in_column = sink_data[fct_table][time_column]
            time_codes = transform_date_indexes(instants_in_column, time_indexes, find_time_index)
            sink_data[fct_table][time_column] = time_codes

    return sink_data

def transform_date_columns(src_data):
    sink_data = dict(src_data)

    date_columns = {
        "fct_flight_booking" : ("departure_date",),
        "fct_hotel_booking" : ("check_in_date", "check_out_date"),
    }
    date_indexes = sink_data['dim_date']['date']

    for fct_table in date_columns.keys():
        for date_column in date_columns[fct_table]:
            dates_in_column = sink_data[fct_table][date_column]
            date_codes = transform_date_indexes(dates_in_column, date_indexes, find_date_index)
            sink_data[fct_table][date_column] = date_codes
    return sink_data

def transform_date_indexes(dates_in_column, date_indexes, find_index_func):
    find_index_map = lambda instant: find_index_func(instant, date_indexes)
    return list(map(find_index_map, dates_in_column))

def find_time_index(instant, time_indexes):
    time_format = '%H:%M'
    timestamp_to_str = instant.strftime(time_format)
    return pd.Index(time_indexes).get_loc(timestamp_to_str)

def find_date_index(instant, date_indexes):
    date_to_timestamp = datetime.combine(instant, datetime.min.time())
    return pd.Index(date_indexes).get_loc(date_to_timestamp)

def transform_valid_dates(src_data):
    sink_data = dict(src_data)
    for table_name in sink_data.keys():
        if (table_name == 'dim_date') or (table_name == 'dim_time'): continue
        df = add_valid_dates(sink_data[table_name])
        sink_data[table_name] = df
    return sink_data

def add_valid_dates(input_df):
    df = pd.DataFrame(input_df)
    time_format = '%Y-%m-%d %H:%M'
    valid_from_dates = [generate_random_date().strftime(time_format) for _ in range(len(df))]
    df['valid_from'] = valid_from_dates
    df['valid_to'] = end_date.strftime(time_format)
    return df

def generate_random_date():
    random_date = start_date + (end_date - start_date) * random.random()
    while random_date > end_date:
        random_date = start_date + (end_date - start_date) * random.random()

    return random_date

def create_dim_time():
    table_time = dict()
    instants = [pd.Timestamp(f"{h}:{m}").strftime('%H:%M') for h in range(24) for m in range(60)]
    table_time['time_id'] = pd.Series(range(len(instants))) + 1
    table_time['instant'] = instants

    hours = list(map(lambda instant: instant[:2], instants))
    table_time['hours_24'] = hours
    table_time['hours_12'] = list(map(lambda hour: '12' if hour=='00' else hour, hours[:len(hours)//2])) * 2

    table_time['hour_minutes'] = list(map(lambda instant: instant[3:], instants))
    table_time['day_minutes'] = table_time['time_id'] - 1
    table_time['midday_midnight'] = list(map(lambda instant: 'a.m.' if instant < '12' else 'p.m.', instants))
    return pd.DataFrame(table_time)

def create_dim_date():
    table_dates = dict()
    all_dates = pd.date_range(start_date, end_date + pd.DateOffset(years=10)).to_series()
    table_dates['date'] = all_dates

    table_dates['day_of_week'] = all_dates.dt.day_name()
    table_dates['day_of_month'] = all_dates.dt.day
    table_dates['day_of_year'] = all_dates.dt.day_of_year

    week_in_month = lambda day_of_month: ((day_of_month + pd.offsets.MonthBegin().rollback(day_of_month).weekday()) // 7) + 1
    table_dates['week_of_month'] = list(map(week_in_month, all_dates.dt.day))
    table_dates['week_of_year'] = all_dates.dt.isocalendar().week
    table_dates['month'] = all_dates.dt.month
    table_dates['month_name'] = all_dates.dt.month_name()
    table_dates['quarter_of_year'] = all_dates.dt.quarter
    table_dates['year'] = all_dates.dt.year

    table_dates['first_day_of_week'] = list(map(lambda weekday: weekday==0, all_dates.dt.weekday))
    table_dates['last_day_of_week'] = list(map(lambda weekday: weekday==6, all_dates.dt.weekday))
    table_dates['first_day_of_month'] = all_dates.dt.is_month_start
    table_dates['last_day_of_month'] = all_dates.dt.is_month_end
    table_dates['first_day_of_quarter'] = all_dates.dt.is_quarter_start
    table_dates['last_day_of_quarter'] = all_dates.dt.is_quarter_end
    table_dates['first_day_of_year'] = all_dates.dt.is_year_start
    table_dates['last_day_of_year'] = all_dates.dt.is_year_end

    # DatetimeIndex used -> drop it and reset to regular index
    return pd.DataFrame(table_dates).reset_index(drop=True)

if __name__ == "__main__":
    pass