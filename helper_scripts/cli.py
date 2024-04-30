import click
from dbt_learn_setup.utils import load_yaml_file
from dbt_learn_setup.setup_learners import setup_learners


@click.command()
@click.argument('config_name', required=True)
@click.option('--stage', '-s', default='setup',
              type=click.Choice(["setup", "followup", "followup_2", "ppd", "wrapup"]),
              help="Which stage to execute. Selecting 'setup' will create "
              "Snowflake users and draft emails. All others will only draft emails.")
@click.option('--test', '-t', is_flag=True, help="Include to run script for 1 learner")
def setup_course(config_name, stage, test=False):
    """
    Setup training course using the given config and credentials set in the repository.

    Args:
        config_name: Config file name provides on the CLI
        stage: type of contact with the participants can be one of
            - setup
            - followup
            - followup_2
            - ppd
            - Wrapup
        test: Flag set this flag to run only for 1 learner.
    """
    training_config = load_yaml_file(config_name)

    email_config = load_yaml_file("email.yml")

    learn_type = training_config["learn_type"]

    setup_learners(
        training_config,
        email_config[learn_type][stage],
        stage,
        test
    )
