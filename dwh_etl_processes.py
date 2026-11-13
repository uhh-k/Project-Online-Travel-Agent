import etl_functions as etl
import db_load as dbl
import dwh_extract as dwhe
import dwh_transform as dwht
import dwh_load as dwhl

def dwh_extract_data():
    db_engine = etl.create_sqlalchemy_engine(dbl.engine_params)
    src_data = dict()
    for source_table in dwhe.dwh_extract_data_sql.keys():
        if source_table in dwhe.dim_src_table_names: prefix = "dim_"
        elif source_table in dwhe.fct_src_table_names: prefix = "fct_"
        else:
            prefix = ""
            print("cannot find source table")
        dim_table_name = f"{prefix}{source_table}"
        src_data[dim_table_name] = etl.extract_data_sql(db_engine, dwhe.dwh_extract_data_sql[source_table])
    return src_data

def dwh_transform_data(src_data):
    staging_data1 = dwht.add_dimensions(src_data)
    staging_data2 = dwht.transform_date_columns(staging_data1)
    staging_data3 = dwht.transform_time_columns(staging_data2)
    snk_data = dwht.transform_valid_dates(staging_data3)
    return snk_data

def dwh_load_data(engine, snk_data):
    dwh_load_to_database(engine)
    pass

def dwh_load_to_database(engine):
    for dwh_table in sink_data.keys():
        df = sink_data[dwh_table]
        etl.load_data(df, engine, dwh_table)



if __name__ == "__main__":
    # source_data = dwh_extract_data()
    # sink_data = dwh_transform_data(source_data)

    dwh_engine = etl.create_sqlalchemy_engine(dwhl.dwh_engine_params)
    # dwh_load_data(dwh_engine, sink_data)

    # # alter data type to SMALLDATE -> working in SSMS, not in Python
    # for sql_query in dwhl.dwh_sql_data_types:
    #     etl.process_sql_query(dwh_engine, sql_query)

    # for sql_query in dwhl.dwh_sql_unique_indexes:
    #     etl.process_sql_query(dwh_engine, sql_query)
    # print(etl.extract_data_sql(dwh_engine, dbl.test_unique_indexes))

    # for sql_query in dwhl.dwh_sql_primary_keys:
    #     etl.process_sql_query(dwh_engine, sql_query)

    for sql_query in dwhl.dwh_sql_foreign_keys:
        etl.process_sql_query(dwh_engine, sql_query)
    print(etl.extract_data_sql(dwh_engine, dbl.test_foreign_keys))
