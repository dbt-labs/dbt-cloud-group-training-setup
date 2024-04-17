import requests
import pandas as pd
import yaml

with open('creds/zero_dbt_account_creds.json') as file:
    dbt_account_creds = yaml.full_load(file)

#identifying the dbt_token requires admin access inside the dbt Cloud account
dbt_token = dbt_account_creds['dbt_token']
account_id = dbt_account_creds['account_id']

headers =  {
    'Authorization': 'Bearer %s' % dbt_token,
    'Content-type': 'application/json'
}

all_users = []
has_new_results = True

print("Retrieving all users in dbt Cloud account: \n")
users_url = f'https://cloud.getdbt.com/api/v2/accounts/{account_id}/users/'
offset = 0
while has_new_results:
    users_api = requests.get(users_url + f"?offset={offset}", headers=headers)
    new_results = users_api.json()['data']
    all_users.extend(new_results)
    offset = users_api.json()['extra']['filters']['offset']+users_api.json()['extra']['pagination']['count']
    total_count = users_api.json()['extra']['pagination']['total_count']
    if offset >= total_count:
        has_new_results = False


print("Subsetting to non-dbt users: \n")
users_df = pd.DataFrame(all_users)
non_dbt_users = users_df[~(users_df.email.str.contains('@dbtlabs.com') | users_df.email.str.contains('@fishtownanalytics.com'))].copy()
non_dbt_users['license_id'] = non_dbt_users['licenses'].copy().apply(lambda x: x[account_id]['id'])


print("Changing non-dbt users to have read-only seats \n")
all_results = []
for idx, row in non_dbt_users.iterrows():
    user_id = row['id']
    license_id = row['license_id']
    user_licenses_url = f'https://cloud.getdbt.com/api/v2/accounts/{account_id}/permissions/{license_id}'    

    data = {
        "id": license_id,
        "user_id": user_id,
        "state": 1,
        "account_id": int(account_id),
        "license_type": "read_only"
    }


    results = requests.post(user_licenses_url, headers=headers, json=data)
    final_results = {'user_id': user_id, 'status': results.json()['status']['code']}
    print(final_results)
    all_results.append(final_results)

all_results_df = pd.DataFrame(all_results)
