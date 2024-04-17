import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'helper_scripts/snowflake'))

import sf_open as sf_open
import yaml
import datetime

# Get snowflake creds
with open('../creds/snowflake_creds.yml') as file:
    snowflake_creds = yaml.full_load(file)

# Open Snowflake Connection
snowflake_creds["role"] = "TRANSFORMER"

cs, ctx = sf_open.main(snowflake_creds)

# Get the schemas in the analytics database

query1 = """
show schemas in analytics
"""

cs.execute(query1)
query_id = cs.sfqid

query2 = """
select
    "name",
    "created_on"
from table(result_scan('{query_id}'))
""".format(query_id=query_id)

print(query2)

cs.execute(query2)

schemas = []

for (name) in cs:
    dict_temp = {}
    dict_temp['schema'] = name[0]
    dict_temp['created_at'] = name[1]
    schemas.append(dict_temp)

# Find the schemas that are from 2020.

cutoff_time = datetime.datetime(
    2021, 4, 30, 0, 0, 0, 0, tzinfo=datetime.timezone.utc)

for schema in schemas:
    if schema['created_at'] < cutoff_time:
        query3 = """
            drop schema {schema} cascade
        """.format(schema=schema['schema'])
        cs.execute(query3)

cs.close
ctx.close
