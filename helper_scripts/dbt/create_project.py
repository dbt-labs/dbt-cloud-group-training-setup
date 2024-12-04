import json
import requests

DBT_CLOUD_BASE_URL = "<ENTER_ACCESS_URL>/api/v3/"


def run(first_name, last_name, account_id):
    print("Starting to create dbt project")
    my_dbt_cloud_project = DbtCloudProject(
        first_name, last_name, account_id)
    my_dbt_cloud_project.create_project()
    my_dbt_cloud_project.create_project_credentials()
    my_dbt_cloud_project.associate_user_credentials()
    my_dbt_cloud_project.create_project_connection()
    my_dbt_cloud_project.update_project()
    my_dbt_cloud_project.create_dev_environment()
    my_dbt_cloud_project.create_managed_repo()
    my_dbt_cloud_project.associate_managed_repo_to_project()
    print("DONE")


class DbtCloudProject:
    def __init__(self, first_name, last_name, account_id):
        with open("./creds/dbt_creds.json", "r") as f:
            config = json.load(f)

        self.token = config["dbt_cloud_token"]
        self.account_id = account_id
        self.user_id = config["dbt_cloud_user_id"]
        self.project = None
        self.project_id = None
        self.first_name = first_name
        self.last_name = last_name
        self.schema = config["schema"]
        self.credentials_id = None
        self.connection_id = None

        # TODO: break this out into a different class
        self.snowflake_user = config["snowflake_user"]
        self.snowflake_password = config["snowflake_password"]

    def make_post_request(self, endpoint, data):
        headers = {
            "Accept": "application/json",
            "Authorization": "Token {}".format(self.token),
        }

        url = "{}/{}".format(DBT_CLOUD_BASE_URL, endpoint)

        print("Making post request to {}".format(url))

        response = requests.post(url=url, headers=headers, json=data)

        if response.status_code in [200, 201]:
            return response
        else:
            print("ERROR! HTML status code: {}".format(response.status_code))
            print(response.json()["data"])
            quit()

    def create_project(self):

        endpoint = "accounts/{}/projects/".format(self.account_id)

        data = {
            "id": self.project_id,
            "name": f"dbt Learn - {self.first_name} {self.last_name}",
            "dbt_project_subdirectory": None,
            "account_id": self.account_id,
            "connection_id": self.connection_id,
            "repository_id": None,
        }

        response = self.make_post_request(endpoint, data)

        self.project = response.json()["data"]
        self.project_id = response.json()["data"]["id"]

    def update_project(self):
        # trailing slash is required for this call to work
        endpoint = "accounts/{}/projects/{}/".format(
            self.account_id, self.project_id)

        self.project["connection_id"] = self.connection_id
        data = self.project

        self.make_post_request(endpoint, data)

    def create_project_credentials(self):

        endpoint = "accounts/{}/projects/{}/credentials/".format(
            self.account_id, self.project_id
        )

        data = {
            "id": None,
            "account_id": self.account_id,
            "project_id": self.project_id,
            "state": 1,
            "threads": 4,
            "target_name": "dev",
            "type": "snowflake",
            "auth_type": "password",
            "schema": self.schema,
            "user": self.snowflake_user,
            "password": self.snowflake_password,
        }

        response = self.make_post_request(endpoint, data)

        self.credentials_id = response.json()["data"]["id"]

    def associate_user_credentials(self):
        # create the user credentials
        endpoint = "users/{}/credentials/".format(self.user_id)

        data = {
            "account_id": self.account_id,
            "project_id": self.project_id,
            "user_id": self.user_id,
            "credentials_id": self.credentials_id,
        }

        self.make_post_request(endpoint, data)

    def create_project_connection(self):
        # create Connection
        # this doesn't have any creds yet
        # figure out later how to make this change for different warehouses

        endpoint = "accounts/{}/projects/{}/connections/".format(
            self.account_id, self.project_id
        )

        data = {
            "id": None,
            "account_id": self.account_id,
            "project_id": self.project_id,
            "state": 1,
            "type": "snowflake",
            "name": "Snowflake training account",
            "created_by_id": self.user_id,
            "details": {
                "allow_sso": False,
                "client_session_keep_alive": False,
                "account": "fka50167",
                "role": "transformer",
                "database": "analytics",
                "warehouse": "transforming",
            },
        }

        response = self.make_post_request(endpoint, data)

        self.connection_id = response.json()["data"]["id"]

    def create_dev_environment(self):

        endpoint = "accounts/{}/environments/".format(self.account_id)

        data = {
            "id": None,
            "name": "Development",
            "type": "development",
            "account_id": self.account_id,
            "project_id": self.project_id,
            "credentials_id": self.credentials_id,
        }

        self.make_post_request(endpoint, data)

    def create_managed_repo(self):

        endpoint = "accounts/{}/projects/{}/managed-repositories/".format(
            self.account_id, self.project_id)
        
        first_initial = self.first_name[0]
        
        data = {
            "name": f"{first_initial}{self.last_name}".lower()
        }

        response = self.make_post_request(endpoint, data)
        self.project["repository_id"] = response.json()["data"]["id"]

    def associate_managed_repo_to_project(self):
        endpoint = "accounts/{}/projects/{}/".format(
            self.account_id, self.project_id)

        data = self.project

        self.make_post_request(endpoint, data)
