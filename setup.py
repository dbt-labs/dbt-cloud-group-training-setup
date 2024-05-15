import argparse
import yaml
import helper_scripts.dbt.create_project as create_dbt_project
import helper_scripts.google.auth_google as auth_google
import helper_scripts.google.gmail_service as gmail_service
import helper_scripts.google.read_sheets as read_sheets
import helper_scripts.html.merge_html as merge_html
import helper_scripts.html.write_draft as write_draft
import helper_scripts.snowflake.sf_open as sf_open
import helper_scripts.snowflake.sf_query as sf_query


def main():
    args = parse_args()
    training_config = load_yaml_file(args.config)
    email_config = load_yaml_file("email.yml")
    google_creds = auth_google.main()
    learner_infos = learner_infos_from_google_sheet(
        google_creds, training_config["google_sheet"])
    learn_type = training_config["learn_type"]
    setup_learners(
        google_creds,
        training_config,
        email_config[learn_type][args.stage],
        learner_infos,
        args.stage,
        args.test
    )


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--test",
        action="store_true",
        help="Include to run script for 1 learner"
    )
    parser.add_argument("config", help="Name of config file")
    parser.add_argument(
        "stage",
        choices=["setup", "followup", "followup_2", "ppd", "wrapup"],
        help="Which stage to execute. Selecting 'setup' will create "
        "Snowflake users and draft emails. All others will only draft emails."
    )
    args = parser.parse_args()
    if args.config is None:
        args.config = input("Enter configuration file name: ")
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
    headers = sheet_with_headers[1]
    learners = sheet_with_headers[2:]
    learner_infos = [dict(zip(headers, learner)) for learner in learners]
    return learner_infos


def setup_learners(
        google_creds, training_config, email_config, learners, stage,
        is_test_run=False
):
    # Connect to Gmail and Snowflake
    print("Connecting to Gmail")
    gmail_connection = gmail_service.main(google_creds)
    should_create_users_and_projects = stage == "setup"
    if should_create_users_and_projects:
        with open("./creds/snowflake_creds.yml") as file:
            snowflake_creds = yaml.full_load(file)
        sf_cursor, sf_connection = sf_open.main(snowflake_creds)
    else:
        print("Skipping user creation because stage is followup or followup_2")

    print("Setting up each user: \n")
    for count, learner in enumerate(learners):
        if is_test_run and count == 1:
            print("\nTest run complete")
            break
        # Skip creating email if learner has already been contacted
        if learner[email_config["contacted_field"]].upper() == "Y":
            print(
                f"{learner['first_name']} {learner['last_name']} already "
                "contacted. Skipping")
            continue
        # Skip creating email if row is empty in Google Sheet
        if learner["first_name"] == "":
            print(
                f"Skipping row {count + 1}. first_name is blank in Google "
                "Sheets.")
            continue
        create_email_draft(
            gmail_connection,
            learner,
            training_config["session"],
            email_config
        )
        if should_create_users_and_projects:
            if learner["sf_user_created"].upper() == "Y":
                print(
                    f"{learner['sf_username']} already created in Snowflake. "
                    "Skipping"
                )
            else:
                create_snowflake_user(
                    sf_connection,
                    sf_cursor,
                    learner["sf_username"],
                    learner["email"],
                    training_config["session"]["snowflake_password"],
                    training_config["session"]["snowflake_user_comment"],
                    training_config["session"]["snowflake_days_to_expiry"]
                )
            if learner["dbt_project_created"].upper() == "Y":
                print(
                    "dbt Cloud project already created for "
                    f"{learner['first_name']} {learner['last_name']}. "
                    "Skipping"
                )
            else:
                create_dbt_project.run(
                    learner["first_name"],
                    learner["last_name"],
                    training_config["session"]["dbt_cloud_account_id"]
                )
    if should_create_users_and_projects:
        # Close the Snowflake Connection
        sf_connection.close()
        sf_cursor.close()


def create_email_draft(gmail_connection, learner, session_info, config):
    # Create HTML file for email with Jinja
    joint_dict = {**learner, **session_info}
    file_path = merge_html.main(joint_dict, config["template"])

    # Create the email as a draft in Gmail
    subject = f"{config['subject_prefix']}{session_info['training_name']}"
    write_draft.main(learner, gmail_connection, subject, file_path)


def create_snowflake_user(
        connection, cursor, username, email, password, comment,
        days_to_expiry
        ):
    create_user_query = f"""
        create user {username}
        password = '{password}'
        email = '{email}'
        default_role = transformer
        default_warehouse = transforming
        comment = '{comment}'
        days_to_expiry = {days_to_expiry};
    """
    grant_role_query = f"""
        grant role transformer to user {username};
    """
    print(f"Creating {username} in Snowflake: ")
    sf_query.main(connection, cursor, create_user_query)
    sf_query.main(connection, cursor, grant_role_query)
    print("DONE\n")


if __name__ == "__main__":
    main()
