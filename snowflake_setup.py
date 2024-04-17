import argparse
import yaml
import helper_scripts.goog.auth_google as auth_google
import helper_scripts.goog.read_sheets as read_sheets
import helper_scripts.snowflake.sf_open as sf_open
import helper_scripts.snowflake.sf_query as sf_query
import re
from googleapiclient.errors import HttpError


def main():
    args = parse_args()
    print(args)
    training_config = load_yaml_file(args.config)
    update_google_sheets = args.update_google_sheets
    google_creds = auth_google.main()
    learners, sheet_headers = learner_infos_from_google_sheet(
        google_creds, training_config["google_sheet"])
    
    snowflake_creds_path = training_config['path_to_snowflake_credentials_for_script']
    
    num_learners = len(learners)
    new_learners = [
        learner 
        for learner in learners 
        if learner.get('Created in Snowflake') != 'Y'
    ]
    
    if len(new_learners) > 0:
        setup_learners(
            snowflake_creds_path,
            training_config,
            new_learners
        )

        if update_google_sheets == 'yes':
            sheets_range, sheets_values = get_sheets_range_and_values(sheet_headers, num_learners)
            add_indicator_google_sheets(
                service=read_sheets.sheets_service(google_creds), 
                spreadsheet_id=training_config["google_sheet"]["spreadsheet_id"], 
                range_name=sheets_range, 
                values=sheets_values,
                value_input_option="USER_ENTERED")
    else:
        print('No new learners to create. \n')
        print('Done.')

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("config", 
        help="""Name of the configuation file. Includes information
             about the Google spreadsheet to reference and the Snowflake credentials for learners.
             """)
    parser.add_argument(
        "--update_google_sheets",
        default="no",
        help="""Update Google Sheets with an indidicator that you have
            already added the user to Snowflake. Values get added to a column
            labeled 'Created in Snowflake'. The default value is 'no'. Pass in the
            value 'yes' to update the column."""
    )
    args = parser.parse_args()
    return args

def load_yaml_file(config_file_name):
    config_string = f"./config/{config_file_name}"
    with open(config_string) as file:
        config = yaml.full_load(file)
    return config

def learner_infos_from_google_sheet(google_creds, sheet_config):
    # Read the values from the Google Sheet
    sheet_with_headers = read_sheets.main(
        google_creds,
        sheet_config["spreadsheet_id"],
        sheet_config["spreadsheet_range"]
    )
    headers = sheet_with_headers[0]
    learners = sheet_with_headers[1:]
    learner_infos = [dict(zip(headers, learner)) for learner in learners]
    return learner_infos, headers


def setup_learners(snowflake_creds_path, training_config, learners):
    
    with open(snowflake_creds_path) as file:
        snowflake_creds = yaml.full_load(file)
    sf_cursor, sf_connection = sf_open.main(snowflake_creds)

    sf_users = get_snowflake_users(sf_cursor)

    
    print("Setting up each user: \n")
    for count, learner in enumerate(learners):
        
        learner_username = '"{learner}"'.format(learner=learner['Email'].lower())
        role = training_config["session"]["default_role"].upper()
        
        # Skip creating email if row is empty in Google Sheet
        if learner["Email"] == "":
            print(f"Skipping row {count + 1}. email is blank in Google Sheets.")
            continue
        
        if learner_username.strip('"') in sf_users:
            user_grants = show_grants_to_snowflake_user(sf_cursor, learner_username)
            if role in user_grants:
                print(f"Skipping row {count + 1}. User {learner_username} already exists with role {role}.")
                continue
            else:
                print(f"Granting user {learner_username} the role {role}")
                grant_role_to_user(sf_connection, sf_cursor, role, learner_username)
                print("DONE\n")
        else:
            create_snowflake_user(
                    sf_connection,
                    sf_cursor,
                    learner_username,
                    learner["Email"],
                    training_config["session"]["snowflake_password"],
                    training_config["session"]["snowflake_user_comment"],
                    training_config["session"]["snowflake_days_to_expiry"],
                    training_config["session"]["default_role"],
                    training_config["session"]['default_warehouse']
            )
            grant_role_to_user(sf_connection, sf_cursor, training_config["session"]["default_role"], learner_username)

    sf_connection.close()
    sf_cursor.close()

def create_snowflake_user(
        connection, cursor, username, email, password, comment,
        days_to_expiry, default_role, default_warehouse
        ):

    create_user_query = f"""
        create user {username}
        password = '{password}'
        email = '{email}'
        default_role = '{default_role}'
        default_warehouse = '{default_warehouse}'
        comment = '{comment}'
        days_to_expiry = {days_to_expiry};
    """
    print(f"Creating {username} in Snowflake: ")
    sf_query.main(connection, cursor, create_user_query)
    print("DONE\n")

def grant_role_to_user(connection, cursor, role, username):
    grant_role_query = f"""
        grant role {role} to user {username};
    """
    sf_query.main(connection, cursor, grant_role_query)
    print("DONE\n")


def get_snowflake_users(cursor):
    cursor.execute("show users;")
    sf_users = cursor.fetchall()
    sf_users = [sf_users[r][0] for r in range(len(sf_users))]
    return sf_users

def show_grants_to_snowflake_user(cursor, username):
    cursor.execute(f"show grants to user {username};")
    user_grants = cursor.fetchall()
    user_grants = [user_grants[r][1] for r in range(len(user_grants))]
    return user_grants

def get_sheets_range_and_values(sheet_headers, num_learners):
    sheets_column_to_update = f"{chr(ord('@')+sheet_headers.index('Created in Snowflake')+1)}"
    sheets_update_range_start = f"{sheets_column_to_update}2"
    sheets_update_range_end = f"{sheets_column_to_update}{str(num_learners+1)}"
    sheets_range = f"{sheets_update_range_start}:{sheets_update_range_end}"
    sheets_values = [['Y'] for _ in range(num_learners)]
    return sheets_range, sheets_values

def add_indicator_google_sheets(service, spreadsheet_id, range_name, values, value_input_option):
    try:
        body = {
            'values': values
        }
        result = service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id, range=range_name,
            valueInputOption=value_input_option, body=body).execute()
        print(f"{result.get('updatedCells')} Google Sheet cells updated.")
        return result
    except HttpError as error:
        print(f"An error occurred: {error}")
        return error

if __name__ == "__main__":
    main()
