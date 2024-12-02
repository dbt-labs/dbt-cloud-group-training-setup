# learn-setup

A repo for documentation and code involved in setting up different dbt Learn experiences, including mail merging, Snowflake user creation, and dbt Cloud project creation.

## How to use this repository

<!-- TODO: make new Loom video that includes the dbt Cloud project creation -->

[Loom Video: How to set up a dbt Learn](https://www.loom.com/share/59561da83d9b4dc59d22aaa0dc95c7e9)

### First Time Set-Up

1. In the folder of your choosing, clone this repo.

2. Install Python dependencies with `pip install -r requirements.txt`.

3. Double check [.gitignore](.gitignore) for the following files. This will ensure you never push any credentials or compiled HTML files to GitHub.

   ```
   creds/
   html_compiled/
   ```


4. Create a folder at the root of your cloned repo called `creds`.

5. Create `snowflake_creds.yml` in the `creds/` folder with the following template. These are the Snowflake credentials that will be used to create the Snowflake users for each learner.

   ```yml
   user: "enter username here"
   password: "enter password here"
   account: "fka50167"
   database: "ANALYTICS"
   warehouse: "TRANSFORMING"
   role: "ACCOUNTADMIN"
   ```

6. Create `dbt_creds.json` in the `creds/` folder with the following template. These are the dbt Cloud API credentials that will be used to create dbt Cloud projects for each learner.

  ```json
  {
    "dbt_cloud_token": "enterdbt cloud token",
    "dbt_cloud_user_id": enter dbt cloud user id,
    "snowflake_user": "enter username",
    "snowflake_password": "enter password",
    "schema": "enter schema"
  }
  ```

  - The dbt_cloud_token is accessible by Creating a new Personal access token (PAT) from dbt Cloud under Your Profile > API tokens > Personal tokens. Pay attention to create a PAT and not a Service token. Your PAT should start with a dbtu_ prefix.
  - The dbt_cloud_user_id is your personal user ID in dbt Cloud. You can find it by navigating to any dbt Cloud project you're a part of, navigating to users, searching for your user, clicking on your name, and then looking at the URL. Grab the ID at the end of the URL. For example, in the URL https://cloud.getdbt.com/settings/accounts/181132/users/87365 your user ID is 87365.
  - The Snowflake user and password is your personal user account that will be used as your development credentials for each of the dbt Cloud projects the script creates.

7. Navigate to the [Google Cloud Console](https://console.cloud.google.com/home) to create a new project and activate the Google Sheets API and the Gmail API.

- Create a new project called "learn-setup".
- Find the **APIs and Services** section on the left and go to **Dashboard**.
- Click on "+ Enable APIs and Services". Find Google Sheets and Gmail and click "Enable".

8. Create an OAuth 2.0 Client ID.

- Still in the **APIs and Services** section, go to **Credentials**. Click "+ Create Credentials" --> "OAuth Client ID".
- At some point it'll ask you to set up the "OAuth consent screen". Select "internal" user type, click create. Fill in the "App name" (maybe learn-setup) and put your own email address in "User support email" and "Developer contact information". Save and continue. 
- Then go back and click "Create Cred entials again"
- Under Application Type pick "Desktop application".
- Under name write something like "learn-setup-script".
- Download the OAuth 2.0 Client ID. Save this as `credentials.json` in `creds/`.
- Excellent! Now you have all the credentials that you need to access Google and Snowflake!

**Optional**: Set up outlook connection, only if you want to send email via an Outlook email account.

Register your app

- Go to Azure portal login with the organizations account that is linked to the email you want to use
- Navigate to the "App Registration" using the search bar
- Register a new app
   - Give it a name like "dbt-learn-setup"
   - Set supported account type to be "Accounts in this organizational directory only"
   - Set the redirect URI to "web" with the following link "http://localhost/"
- Open API Premissions in the menu on the right and add the following premissions for the microsoft Graph API
   - email
   - mail.ReadWrite
   - User.Read
   - User.ReadBasics.All
- Create a folder called `azure_credentials.json` in the `creds\` folder. 
- Copy the client ID of the registered app save it to azure_credentials.json in the creds\ folder. Example of file:

```
{
  "client_id": "xxx-xxx"
}
```


9. Create a folder at the root of the repo called `html_compiled`. This is where the compiled HTML will live when you run the script to create draft emails for each learner. This is also in the .gitignore and won't be committed to the repo.
   

### Set Up a New Learn

1. **Note if you are a partner trainer, then skip this step. You will use the one of the two training accounts your team already has**
Create a new dbt Cloud account and name it with the format "CLIENT Group dbt Learn MONTH YEAR". For example "Siemens Group dbt Learn May 2023". Use the backend to set billing plan to "Free". Also add the number of developer seats and increase the run slots - maybe to 5. Note the account ID (e.g., in the URL https://cloud.getdbt.com/#/accounts/28872 the account ID is 28872) for the config file you will create in a couple of steps.  Additionally, at the account level, set a `starter repo url` with the following text: `git@github.com:dbt-labs/dbt-learn-gt-init.git`.  This will allow all repo's to start with basic modeling, tests, and docs of the Jaffle Shop data.

2. Check out a new branch.

3. Create a new file using the private template in the [config](config) folder. Name it based on the date of the training and the client name. Update the fields for the upcoming training.

4. Open the `create_project.py` in the `config/dbt` folder and update the DBT_CLOUD_BASE_URL. To update the correct value, find the Access URL by going Account settings > Account > Access URL.  E.g. If your Access URL is `https://a1.bc2.dbt.com`, your DBT_CLOUD_BASE_URL will be `https://a1.bc2.dbt.com/api/v3/`. Pay attention to include the `api/v3` at the end of the URL.
```json
{
  DBT_CLOUD_BASE_URL = "https://a.bc.dbt.com/api/v3/" 
}
```

4. Create a virtual environment that you can use to run the script. First create the virtual environment with the command `python3 -m venv env`. Then activate it using the command `source env/bin/activate`. Then install all dependencies using the command `pip3 install --upgrade pip && pip install -r requirements.txt`.

5. Do a test run by running a command similar to the following, except put in your YML file `python3 setup.py my_yaml_file.yml setup --test`. For example, `python3 setup.py 2021-08-25_private_scentre_group.yml setup --test`. This will run the script for one learner. You can run `python setup.py -h` for more details on the command-line arguments for this script.

6. If you want to make any changes to the email template, go to [html_templates](html_templates) and edit the relevant HTML file. Email templates can access any values in the Google Sheet and any info in the session block of the config file you created above.

7. Once you've confirmed that everything looks good to go, use the [Makefile](Makefile) to set the shell command that you want to run for setting up a learn. It will be similar to the command in step #3 above but without the `--test` flag. Run the command.

- The script will now work its magic. In its current version, the script will:
  - Create users in the Snowflake account you created credentials for.
  - Create drafts emails to attendees directly in your Gmail account. Note: This does NOT send them. Check your Drafts folder.
  - Create one project per learner in the dbt Cloud account that you specified in the config file.

8. Double check in the dbt Cloud account that all of the projects were made correctly - one per learner with their full name in the project name. Each project should have a database connection and a managed repo.

9. Invite each learner to the dbt Cloud project (Account Settings > Invite Users).
  - Another option: add each user through the backend. This reduces some confusion with learners who already have existing accounts. Caveat - this will only work for users who already have a dbt Cloud account. If they are new users, you will need to add them through the front end.
  - To add a learner to the account through the [dbt Cloud backend](https://cloud.getdbt.com/backend/), you will need to be connected to the [VPN](https://www.notion.so/dbtlabs/VPN-Setup-Guide-e169db2aa0a24bfeb16396f92cadfb20). Find the account you created for this training under "Accounts". Scroll to the "User Licenses" section and manually add each learner by clicking the "+ Add another User License" and then clicking on the magnifying glass icon next to the new field. Enter the learner's email address. 

10. Double check the email drafts and then send them.

11. Commit your changes to your branch.


### Reauthorizing Google Credentials
The Google credentials are saved by default to the `/creds/token.pickle` file the first time you use `helper_scripts/goog/auth_google.py` in any of the scripts. In order to regenerate the credentials (which is needed when the scopes change to include write permissions) just delete the `/creds/token.pickle` file. The next time you run a script that uses the `auth_google.py` script, it will open in the browser to create the credentials and the new credentials will get pickled and used for future uses.
