import os
import db_load as dbl

# entity (table) mapping to attributes (columns) -> csv file structures
entity_attributes = dict()
for entity in dbl.table_names:
    attributes = list(dbl.table_columns[entity])
    if entity in ('country', 'city'): continue
    entity_attributes[entity] = tuple(attributes)

# csv file names
dirname = os.path.dirname(os.getcwd())
filename = lambda entity_name : os.path.join(dirname, f'Online Travel Agent Source Data\\DataSource_{entity_name}.csv')
