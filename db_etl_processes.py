import etl_functions as etl
import db_extract as dbe
import db_transform as dbt
import db_load as dbl

# create a SQLAlchemy engine
def get_engine():
    db_engine_params = dbl.engine_params
    return etl.create_sqlalchemy_engine(db_engine_params)

# create a schema in the database
def create_schema(engine):
    etl.process_sql_query(engine, dbl.sql_create_schema)
    print(etl.extract_data_sql(engine, dbl.test_create_schema))
    print()

# extrac data from csv files
def retrieve_data():
    src_data = dict()
    for entity in dbe.entity_attributes.keys():
        csv_file = dbe.filename(entity)
        attributes = dbe.entity_attributes[entity]
        src_data[entity] = etl.extract_data_csv(csv_file, ';', attributes)
    return src_data

def move_data(src_data, engine):
    # extract data for new tables 'country' and 'city'
    db_data = dbt.transform_new_tables(src_data)
    # load data into database
    for source in db_data.keys():
        df = db_data[source]
        etl.load_data(df, engine, source, schema=dbl.schema)

def modify_database(engine):
    for sql_db_modification in dbl.sql_db_modifications:
        for query in sql_db_modification:
            etl.process_sql_query(engine, query)
    for sql_test_modification in dbl.sql_test_modifications:
        print(etl.extract_data_sql(engine, sql_test_modification))

if __name__ == "__main__":
    db_engine = get_engine()
    # create_schema(engine)

    # source_data = retrieve_data()
    # move_data(source_data, db_engine)
    modify_database(db_engine)
