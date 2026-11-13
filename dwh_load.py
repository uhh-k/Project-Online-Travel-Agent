import etl_functions as etl
import db_load as dbl
import dwh_extract as dwhe

# parameters for SQLAlchemy engine
dwh_engine_params = etl.EngineParams(
    'ODBC Driver 17 for SQL Server',
    'localhost',
    'Online_Travel_Agent_DWH',
    'mssql',
    'pyodbc'
)

dwh_schema = 'dbo'

dwh_tables_def = {
    "dim_date": {
        "date": "DATE NOT NULL",
        "day_of_week": "VARCHAR(15) NOT NULL",
        "day_of_month": "INT NOT NULL",
        "day_of_year": "INT NOT NULL",
        "week_of_month": "INT NOT NULL",
        "week_of_year": "INT NOT NULL",
        "month": "INT NOT NULL",
        "month_name": "VARCHAR(15) NOT NULL",
        "quarter_of_year": "INT NOT NULL",
        "year": "INT NOT NULL",
        "first_day_of_week": "BIT NOT NULL",
        "last_day_of_week": "BIT NOT NULL",
        "first_day_of_month": "BIT NOT NULL",
        "last_day_of_month": "BIT NOT NULL",
        "first_day_of_quarter": "BIT NOT NULL",
        "last_day_of_quarter": "BIT NOT NULL",
        "first_day_of_year": "BIT NOT NULL",
        "last_day_of_year": "BIT NOT NULL",
    },
    "dim_time": {
        "instant": "TIME(0) NOT NULL",
        "hours_24": "VARCHAR(2) NOT NULL",
        "hours_12": "VARCHAR(2) NOT NULL",
        "hour_minutes": "VARCHAR(2) NOT NULL",
        "day_minutes": "INT NOT NULL",
        "midday_midnight": "VARCHAR(10) NOT NULL",
    },
    "fct_flight_booking": {
        "flight_trip": "VARCHAR(4) NOT NULL",
        "flight_number": "VARCHAR(6) NOT NULL",
        "airport_src": "VARCHAR(3) NOT NULL",
        "airport_dst": "VARCHAR(3) NOT NULL",
        "departure_date": "INT NOT NULL",
        "departure_time": "INT NOT NULL",
        "flight_duration": "INT NOT NULL",
        "travel_class": "VARCHAR(8) NOT NULL",
        "seat_number": "VARCHAR(3) NOT NULL",
        "flight_price": "MONEY NOT NULL",
        "customer": "VARCHAR(7) NOT NULL",
        "customer_gender": "VARCHAR(1) NOT NULL",
        "customer_country": "NVARCHAR(100) NOT NULL",
        "airline": "VARCHAR(5) NOT NULL",
        "aircraft": "VARCHAR(10) NOT NULL",
    },
    "fct_hotel_booking": {
        "hotel_trip": "VARCHAR(4) NOT NULL",
        "hotel": f"VARCHAR(4) NOT NULL",
        "check_in_date": "INT NOT NULL",
        "check_out_date": "INT NOT NULL",
        "hotel_price": "MONEY NOT NULL",
        "breakfast_included": "VARCHAR(1) NOT NULL",
        "customer": "VARCHAR(7) NOT NULL",
        "customer_gender": "VARCHAR(1) NOT NULL",
        "customer_country": "NVARCHAR(100) NOT NULL",
    },
}

dwh_sql_data_types = list()
def add_scd_attributes(relation_name):
    scd_sql_queries = list()
    scd_attributes = ("valid_from", "valid_to")
    scd_data_type = "SMALLDATETIME NOT NULL"
    for scd_attribute in scd_attributes:
        scd_sql = f"ALTER TABLE {dwh_schema}.{relation_name} ALTER COLUMN {scd_attribute} {scd_data_type}"
        scd_sql_queries.append(scd_sql)
    return scd_sql_queries

for relation in dwh_tables_def.keys():
    attributes = dwh_tables_def[relation]
    for attribute in attributes:
        sql = f"ALTER TABLE {dwh_schema}.{relation} ALTER COLUMN {attribute} {attributes[attribute]}"
        dwh_sql_data_types.append(sql)
    if relation not in ("dim_date", "dim_time"):
        dwh_sql_data_types += add_scd_attributes(relation)

for relation in dwhe.dim_src_table_names:
    attributes = dbl.data_types[relation]
    relation_name = f"dim_{relation}"
    for attribute in attributes:
        if attribute not in dwhe.columns_to_remove[relation]:
            sql = f"ALTER TABLE {dwh_schema}.{relation_name} ALTER COLUMN {attribute} {attributes[attribute]}"
            dwh_sql_data_types.append(sql)
    dwh_sql_data_types += add_scd_attributes(relation_name)

dwh_sql_unique_indexes = list()
for relation in dwhe.dim_src_table_names:
    sql = f"ALTER TABLE {dwh_schema}.dim_{relation} ADD CONSTRAINT AK_{relation} UNIQUE ({relation}_code)"
    dwh_sql_unique_indexes.append(sql)

dwh_sql_primary_keys = list()
drop_dim_time_id = f"ALTER TABLE {dwh_schema}.dim_time DROP COLUMN time_id"
dwh_sql_primary_keys.append(drop_dim_time_id)

for relation in ("dim_date", "dim_time"):
    primary_key = f"{relation[4:]}_id"
    sql_pk = f"ALTER TABLE {dwh_schema}.{relation} ADD {primary_key} INT NOT NULL IDENTITY(1,1)"
    dwh_sql_primary_keys.append(sql_pk)
    sql_constraint = f"ALTER TABLE {dwh_schema}.{relation} ADD CONSTRAINT PK_{relation} PRIMARY KEY ({primary_key})"
    dwh_sql_primary_keys.append(sql_constraint)

for relation in ("flight", "hotel"):
    relation_name = f"fct_{relation}_booking"
    primary_key = f"{relation_name[4:]}_id"
    sql_pk = f"ALTER TABLE {dwh_schema}.{relation_name} ADD {primary_key} INT IDENTITY(1,1)"
    dwh_sql_primary_keys.append(sql_pk)
    sql_constraint = f"ALTER TABLE {dwh_schema}.{relation_name} ADD CONSTRAINT PK_{relation_name} PRIMARY KEY ({primary_key})"
    dwh_sql_primary_keys.append(sql_constraint)

for relation in dwhe.dim_src_table_names:
    relation_name = f"dim_{relation}"
    primary_key = f"{relation}_code"
    sql_constraint = f"ALTER TABLE {dwh_schema}.{relation_name} ADD CONSTRAINT PK_{relation_name} PRIMARY KEY ({primary_key})"
    dwh_sql_primary_keys.append(sql_constraint)

dwh_foreign_keys = {
    "fct_flight_booking": {
        "customer" : ("dim_customer", "customer_code", "customer"),
        "airline" : ("dim_airline", "airline_code", "airline"),
        "aircraft" : ("dim_aircraft", "aircraft_code", "aircraft"),
        "airport_src": ("dim_airport", "airport_code", "airport_src"),
        "airport_dst": ("dim_airport", "airport_code", "airport_dst"),
        "departure_date": ("dim_date", "date_id", "departure_date"),
        "departure_time": ("dim_time", "time_id", "departure_time"),
    },
    "fct_hotel_booking": {
        "customer": ("dim_customer", "customer_code", "customer"),
        "hotel": ("dim_hotel", "hotel_code", "hotel"),
        "check_in_date": ("dim_date", "date_id", "check_in_date"),
        "check_out_date": ("dim_date", "date_id", "check_out_date"),
    },
}

dwh_sql_foreign_keys = list()
for relation, attributes in dwh_foreign_keys.items():
    relation_name = f"{relation[4:]}"
    for attribute in attributes:
        sql = (f"ALTER TABLE {dwh_schema}.{relation} ADD CONSTRAINT FK_{relation_name}_{attributes[attribute][2]} "
               f"FOREIGN KEY ({attribute}) REFERENCES {dwh_schema}.{attributes[attribute][0]} ({attributes[attribute][1]})")
        dwh_sql_foreign_keys.append(sql)



for item in dwh_sql_primary_keys: print(item)
