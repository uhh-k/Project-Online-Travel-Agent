import pandas as pd
import re

import db_extract as dbe

def transform_new_tables(source_data):
    db_data = dict(source_data)
    entity_names = dbe.entity_attributes.keys()

    new_tables = ('country', 'city')
    for new_table in new_tables:
        datasets = set()
        for entity_name in entity_names:
            attributes = dbe.entity_attributes[entity_name]
            for attribute in attributes:
                if re.search(f'{new_table}$', attribute):
                    duplicates = source_data[entity_name][attribute]
                    datasets.update(duplicates)
                    break
        df = pd.DataFrame({f"{new_table}_name": sorted(list(datasets))})
        db_data[new_table] = df

    return db_data

# # archiving some attempt
# def transform_referencing():
#     entity_name = 'customers'
#     customer_data = source_data[entity_name]
#     attributes = list(customer_data.keys())
#
#     country_entity = 'country'
#     country_list = tuple(sink_data[country_entity][f"{country_entity}_name"])
#     country_index = lambda country_name: country_list.index(country_name) + 1
#
#     for attribute in attributes:
#         if re.search(f"{country_entity}$", attribute):
#             print(source_data[entity_name][attribute])
#             try:
#                 source_data[entity_name][attribute] = source_data[entity_name][attribute].map(country_index)
#             except Exception as error:
#                 print(error)

