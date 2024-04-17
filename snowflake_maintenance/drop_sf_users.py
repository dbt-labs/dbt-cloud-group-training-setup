import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'helper_scripts/snowflake'))

import sf_open as sf_open
import yaml
import datetime

# Get snowflake creds
with open('../creds/snowflake_creds.yml') as file:
    snowflake_creds = yaml.full_load(file)

# Open Snowflake Connection
snowflake_creds["role"] = "ACCOUNTADMIN"

cs, ctx = sf_open.main(snowflake_creds)

# Get the schemas in the analytics database

query1 = """
show users
"""

cs.execute(query1)
query_id = cs.sfqid

query2 = """
select
    "name",
    "login_name",
    "created_on",
    "last_success_login",
    "expires_at_time"
from table(result_scan('{query_id}'))
order by "name"
""".format(query_id=query_id)

print(query2)

cs.execute(query2)

users = []

for (name) in cs:
    dict_temp = {}
    dict_temp['name'] = name[0]
    dict_temp['created_at'] = name[2]
    dict_temp['expires_at'] = name[4]
    users.append(dict_temp)

# Find the users who's expiration is set before the cutoff time.

cutoff_time = datetime.datetime(
    2022, 10, 31, 0, 0, 0, 0, tzinfo=datetime.timezone.utc)

for user in users:
    if user['expires_at'] is None or user['name'] == 'SNOWFLAKE':
        continue
    if user['expires_at'] < cutoff_time:
        print(user["name"])
        query3 = """
        drop user \"{user}\"
        """.format(user=user['name'])
        cs.execute(query3)

cs.close
ctx.close
