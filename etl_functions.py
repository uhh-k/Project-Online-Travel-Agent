import traceback
from dataclasses import dataclass
import pandas as pd
import urllib.parse
from sqlalchemy import create_engine, text

@dataclass
class EngineParams:
    db_driver: str
    db_server: str
    db_name: str
    dbms: str
    dbms_pkg: str

def create_sqlalchemy_engine(params: EngineParams):
    parameters = (
        f"DRIVER={params.db_driver};"
        f"SERVER={params.db_server};"
        f"DATABASE={params.db_name};"
        f"Trusted_Connection=yes;"
        f"Encrypt=no;"
    )
    db_url = urllib.parse.quote_plus(parameters)

    try:
        engine = create_engine(f"{params.dbms}+{params.dbms_pkg}:///?odbc_connect={db_url}")
        print("Creating a SQLAlchemy engine succeeded.\n")
        return engine
    except Exception as error:
        traceback.print_exc()
        print(f"Creating a SQLAlchemy engine failed: {error}\n")

def process_sql_query(engine, query):
    try:
        with engine.connect() as conn:
            conn.execute(text(query))
            conn.commit()
    except Exception as error:
        traceback.print_exc()
        print(f"Processing SQL query failed: {error}\n")

def extract_data_sql(engine, query):
    try:
        df = pd.read_sql(query, engine)
        return df
    except Exception as error:
        traceback.print_exc()
        print(f"Extracting data from database failed: {error}\n")

def extract_data_csv(csv_file, separator, columns, if_header=None):
    try:
        df = pd.read_csv(csv_file, sep=separator, header=if_header, names=columns)
        return df
    except Exception as error:
        traceback.print_exc()
        print(f"Extracting data from csv file failed: {error}\n")

def load_data(df, engine, table, schema=None):
    try:
        df.to_sql(table, engine, schema=schema, if_exists='replace', index=False)
    except Exception as error:
        traceback.print_exc()
        print(f"Loading data to database failed: {error}\n")

if __name__ == "__main__":
    pass