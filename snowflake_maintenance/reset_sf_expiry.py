import helper_scripts.goog.auth_google as auth_google
import helper_scripts.goog.read_sheets as read_sheets
import helper_scripts.snowflake.sf_open as sf_open
import helper_scripts.snowflake.sf_query as sf_query
import yaml
import argparse

# Step 1: Get configurations and credentials
# Parse arguments
parser = argparse.ArgumentParser()
parser.add_argument("-c", "--config", help="Name of Config File")
args = parser.parse_args()

# Prompt for config file if not given
if args.config is not None:
    config_name = args.config
else:
    config_name = input("Enter configuration file name: ")
config_string = './config/' + config_name

# Get training sessions configurations
with open(config_string) as file:
    config = yaml.full_load(file)

# Get Snowflake creds
with open('./creds/snowflake_creds.yml') as file:
    sf_creds = yaml.full_load(file)
snowflake_creds = sf_creds['snowflake']

# Step 2: Open connections with Google and Snowflake
# Authenticate with Google
creds = auth_google.main()

# Open Snowflake Connection with ACCOUNTADMIN role
snowflake_creds["role"] = "ACCOUNTADMIN"
cs, ctx = sf_open.main(snowflake_creds)

# Step 3: Read attendee sheet
# Get information from config files
spreadsheet_id = config['sheet']['spreadsheet_id']
spreadsheet_range = config['sheet']['spreadsheet_range']

# Read the values from the Google Sheet
sheet_with_headers = read_sheets.main(creds, spreadsheet_id, spreadsheet_range)

# Parse the sheets object into headers and learner information
headers = sheet_with_headers[0]
learner_info = sheet_with_headers[1:]

print("Resetting expiry date for each user: \n")

for learner in learner_info:

    # Create dictionary of learner and session information
    learner_dict = dict(zip(headers, learner))
    sf_username = learner_dict['sf_username']
    snowflake_days = config['session']['snowflake_days']

    print("* {user}:".format(user=sf_username), end=" ")

    # Write and submit the query
    query1 = f"""
    alter user {sf_username}
    set days_to_expiry = {snowflake_days};"""
    sf_query.main(ctx, cs, query1)

    print("DONE\n")

# Close the Snowflake Connection
cs.close()
ctx.close()
