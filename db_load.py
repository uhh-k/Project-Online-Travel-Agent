import re

import etl_functions as etl

# parameters for SQLAlchemy engine
engine_params = etl.EngineParams(
    'ODBC Driver 17 for SQL Server',
    'localhost',
    'Online_Travel_Agent_DB',
    'mssql',
    'pyodbc'
)

# schema name
schema = 'ota'

# create a schema
test_create_schema = f"SELECT * FROM sys.schemas WHERE name = '{schema}'"
sql_create_schema = f"""
    IF NOT EXISTS({test_create_schema})
    BEGIN
        EXEC('CREATE SCHEMA [{schema}] AUTHORIZATION [dbo]')
    END
"""

# alter data types after loading data from csv into database
## data types to be set
data_types = {
    "country" : {
        "country_name" : "NVARCHAR(100) NOT NULL"
    },
    "city" : {
        "city_name" : "NVARCHAR(100) NOT NULL"
    },
    "aircraft" : {
        "aircraft_name" : "VARCHAR(100) NOT NULL",
        "aircraft_iata" : "VARCHAR(3)",
        "aircraft_icao" : "VARCHAR(4)",
        "aircraft_code" : "VARCHAR(10) NOT NULL"
    },
    "airline": {
        "airline_code" : "VARCHAR(5) NOT NULL",
        "airline_name" : "NVARCHAR(100) NOT NULL",
        "airline_country" : "NVARCHAR(100) NOT NULL",
        "airline_iata" : "VARCHAR(4)",
        "airline_icao" : "VARCHAR(6)",
        "airline_alias" : "NVARCHAR(100)"
    },
    "airport" : { 
        "airport_code" : "VARCHAR(3) NOT NULL",
        "airport_name" : "VARCHAR(100) NOT NULL",
        "airport_city" : "NVARCHAR(100) NOT NULL",
        "airport_latitude" : "FLOAT NOT NULL",
        "airport_longitude" : "FLOAT NOT NULL",
    },
    "customer" : {
        "customer_code" : "VARCHAR(7) NOT NULL",
        "customer_first_name" : "VARCHAR(25) NOT NULL",
        "customer_family_name" : "VARCHAR(25) NOT NULL",
        "customer_gender" : "VARCHAR(1) NOT NULL",
        "customer_birth_date" : "DATE NOT NULL",
        "customer_country": "NVARCHAR(100) NOT NULL",
        "customer_phone_number" : "VARCHAR(13) NOT NULL"
    },
    "flight_booking" : {
        "trip_id" : "VARCHAR(4) NOT NULL",
        "customer_code" : "VARCHAR(7) NOT NULL",
        "flight_number" : "VARCHAR(6) NOT NULL",
        "airline_code" : "VARCHAR(5) NOT NULL",
        "aircraft_code" : "VARCHAR(10) NOT NULL",
        "airport_src": "VARCHAR(3) NOT NULL",
        "airport_dst": "VARCHAR(3) NOT NULL",
        "departure_time" : "TIME NOT NULL",
        "departure_date" : "DATE NOT NULL",
        "flight_duration" : "TIME NOT NULL",
        "travel_class" : "VARCHAR(8) NOT NULL",
        "seat_number" : "VARCHAR(3) NOT NULL",
        "flight_price" : "MONEY NOT NULL"
    },
    "hotel" : {
        "hotel_code" : "VARCHAR(4) NOT NULL",
        "hotel_name" : "NVARCHAR(100) NOT NULL",
        "hotel_address" : "NVARCHAR(MAX) NOT NULL",
        "hotel_city" : "NVARCHAR(100) NOT NULL",
        "hotel_country" : "NVARCHAR(100) NOT NULL",
        "hotel_score" : "DECIMAL(2,1) NOT NULL",
    },
    "hotel_booking" : {
        "trip_id": "VARCHAR(4) NOT NULL",
        "customer_code" : f"VARCHAR(7) NOT NULL",
        "hotel_code": f"VARCHAR(4) NOT NULL",
        "check_in_date": "DATE NOT NULL",
        "check_out_date": "DATE NOT NULL",
        "hotel_price": "MONEY NOT NULL",
        "breakfast_included": "VARCHAR(1) NOT NULL"
    }
}
## SQL statements to alter data types of columns
sql_data_types = list()
for relation in data_types:
    attributes = data_types[relation]
    for attribute in attributes:
        sql = f"ALTER TABLE {schema}.{relation} ALTER COLUMN {attribute} {attributes[attribute]}"
        sql_data_types.append(sql)

# table names and columns
table_names = tuple(data_types.keys())
table_columns = dict()
for relation, attributes in data_types.items(): table_columns[relation] = tuple(attributes.keys())

# add constraints
## check constraints
check_constraints = {
    "airport" : {
        "airport_latitude" : "airport_latitude < 90",
        "airport_longitude" : "airport_longitude < 90",
    },
    "customer" : {
        "customer_gender" : "customer_gender IN ('M', 'F', 'D')",
        "customer_birth_date" : "customer_birth_date < CAST(GETDATE() AS DATE)"
    },
    "flight_booking" : {
        "travel_class" : "travel_class IN ('first', 'business', 'economy')",
    },
    "hotel_booking" : {
        "breakfast_included": "breakfast_included IN ('t', 'f')"
    }
}

## SQL statements to ada check constraints
sql_check_constraints = list()
for relation, attributes in check_constraints.items():
    for attribute in attributes:
        sql = f"ALTER TABLE {schema}.{relation} ADD CONSTRAINT CHK_{attribute} CHECK ({attributes[attribute]})"
        sql_check_constraints.append(sql)

## test check constraints
test_check_constraints = "SELECT name, definition FROM sys.check_constraints"

## unique indexes (for foreign keys)
unique_indexes = dict()
for relation in table_names:
    for column_name in table_columns[relation]:
        if re.search('_code$', column_name) and not re.search('_booking$', relation):
            unique_indexes[relation] = column_name
unique_indexes['country'] = 'country_name'
unique_indexes['city'] = 'city_name'

## SQL statements to add unique indexes
sql_unique_indexes = list()
for relation, attribute in unique_indexes.items():
    sql = f"ALTER TABLE {schema}.{relation} ADD CONSTRAINT AK_{attribute} UNIQUE ({attribute})"
    sql_unique_indexes.append(sql)

## test unique indexes
test_unique_indexes = "SELECT name, is_unique_constraint FROM sys.indexes WHERE is_unique_constraint = 1"

## primary keys
sql_primary_keys = list()
for relation in table_names:
    primary_key = f"{relation}_id"
    sql_PK_column = f"ALTER TABLE {schema}.{relation} ADD {primary_key} INT IDENTITY(1,1)"
    sql_primary_keys.append(sql_PK_column)
    sql_PK_constraint = f"ALTER TABLE {schema}.{relation} ADD CONSTRAINT PK_{relation} PRIMARY KEY ({primary_key})"
    sql_primary_keys.append(sql_PK_constraint)

## foreign keys
foreign_keys = {
    "airline": {
        "airline_country" : ("country", "country_name", "country")
    },
    "airport" : {
        "airport_city" : ("city", "city_name", "city")
    },
    "customer" : {
        "customer_country": ("country","country_name", "country")
    },
    "flight_booking" : {
        "customer_code" : ("customer", "customer_code", "customer"),
        "airline_code" : ("airline", "airline_code", "airline"),
        "aircraft_code" : ("aircraft", "aircraft_code", "aircraft"),
        "airport_src": ("airport", "airport_code", "airport_src"),
        "airport_dst": ("airport", "airport_code", "airport_dst"),
    },
    "hotel" : {
        "hotel_city" : ("city", "city_name", "city"),
        "hotel_country" : ("country","country_name", "country")
    },
    "hotel_booking" : {
        "customer_code" : ("customer", "customer_code", "customer"),
        "hotel_code": ("hotel", "hotel_code", "hotel"),
    }
}

## SQL statements for foreign keys
sql_foreign_keys = list()
for relation, attributes in foreign_keys.items():
    for attribute in attributes:
        sql = (f"ALTER TABLE {schema}.{relation} ADD CONSTRAINT FK_{relation}_{attributes[attribute][2]} "
               f"FOREIGN KEY ({attribute}) REFERENCES {schema}.{attributes[attribute][0]} ({attributes[attribute][1]})")
        sql_foreign_keys.append(sql)

## test foreign keys
test_foreign_keys = "SELECT name, type_desc FROM sys.foreign_keys"

# collect modifications
sql_db_modifications = [sql_data_types, sql_check_constraints, sql_unique_indexes, sql_primary_keys, sql_foreign_keys]
sql_test_modifications = [test_check_constraints, test_unique_indexes, test_foreign_keys]

for item in sql_check_constraints: print(item)