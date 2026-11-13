import db_load as dbl

columns_to_remove = {
    "customer" : ("customer_phone_number",),
    "aircraft" : (),
    "airline" : ("airline_iata", "airline_icao", "airline_alias"),
    "airport" : ("airport_latitude", "airport_longitude",),
    "hotel" : ("hotel_address",),
}
dim_src_table_names = tuple(columns_to_remove.keys())

dim_src_table_columns = dict()
for table_name in dim_src_table_names:
    table_columns = list(dbl.table_columns[table_name])
    for column in columns_to_remove[table_name]: table_columns.remove(column)
    dim_src_table_columns[table_name] = tuple(table_columns)

dwh_extract_data_sql = dict()
for table_name in dim_src_table_names:
    column_names = ", ".join(dim_src_table_columns[table_name])
    sql = f"SELECT {column_names} FROM {dbl.schema}.{table_name}"
    dwh_extract_data_sql[table_name] = sql

fct_src_table_columns = {
    "customer" : "c.customer_code AS customer, customer_gender, customer_country",
    "flight_booking" : "fb.trip_id AS flight_trip, flight_number, airport_src, airport_dst, "
                       "departure_date, departure_time, flight_duration, travel_class, seat_number, flight_price",
    "hotel_booking" : "hb.trip_id AS hotel_trip, hb.hotel_code AS hotel, "
                      "check_in_date, check_out_date, hotel_price, breakfast_included"
}

fct_src_tables_sql = {
    "flight_booking" : f"""
        SELECT {fct_src_table_columns['flight_booking']}, {fct_src_table_columns['customer']}, 
        al.airline_code AS airline, ac.aircraft_code AS aircraft 
        FROM ota.flight_booking AS fb
        JOIN ota.customer AS c ON c.customer_code = fb.customer_code
        JOIN ota.airline AS al ON al.airline_code = fb.airline_code
        JOIN ota.airport AS ap ON ap.airport_code = fb.airport_src
        JOIN ota.aircraft AS ac ON ac.aircraft_code = fb.aircraft_code
        """,
    "hotel_booking" : f"""
        SELECT {fct_src_table_columns['hotel_booking']}, {fct_src_table_columns['customer']}        
        FROM ota.hotel_booking AS hb
        JOIN ota.customer AS c ON c.customer_code = hb.customer_code
        JOIN ota.hotel AS h ON h.hotel_code = hb.hotel_code
        """,
    # "flight_hotel_booking" : f"""
    #     SELECT fb.customer_code AS flight_customer, hb.customer_code AS hotel_customer,
    #     {fct_src_table_columns['flight_booking']}, {fct_src_table_columns['hotel_booking']}
    #     FROM ota.flight_booking AS fb
    #     FULL JOIN ota.hotel_booking AS hb ON hb.trip_id = fb.trip_id
    #     """
}
dwh_extract_data_sql.update(fct_src_tables_sql)
fct_src_table_names = tuple(fct_src_tables_sql.keys())

