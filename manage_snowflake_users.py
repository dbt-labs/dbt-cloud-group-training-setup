import click
import yaml

from helper_scripts.snowflake import sf_open, sf_query


def load_yaml_file(path):
    with open(path) as file:
        config = yaml.full_load(file)
    return config


@click.group
@click.option("--config-path", required=True)
@click.pass_context
def cli(ctx, config_path):
    ctx.config = load_yaml_file(config_path)

    with open("./creds/snowflake_creds.yml") as file:
        snowflake_creds = yaml.full_load(file)

    ctx.cursor, ctx.connection = sf_open.main(snowflake_creds)


def get_snowflake_users(cursor):
    cursor.execute("show users;")
    sf_users = cursor.fetchall()
    sf_users = [sf_users[r][0] for r in range(len(sf_users))]
    return sf_users


def grant_role_to_user(connection, cursor, role, username):
    grant_role_query = f"""
        grant role "{role}" to user "{username}";
    """
    sf_query.main(connection, cursor, grant_role_query)
    print("DONE\n")


def reset_user_password(connection, cursor, password, username):
    grant_role_query = f"""
        ALTER USER "{username}" SET password='{password}';
    """
    sf_query.main(connection, cursor, grant_role_query)
    print("DONE\n")


def unlock_user_account(connection, cursor, username):
    grant_role_query = f"""
        ALTER USER "{username}" SET mins_to_unlock=0;
    """
    sf_query.main(connection, cursor, grant_role_query)
    print("DONE\n")


@cli.command()
@click.argument("user")
@click.pass_context
def fix_role(ctx, user):
    """Fix a user's role in snowflake."""
    grant_role_to_user(
        ctx.parent.connection,
        ctx.parent.cursor,
        role=ctx.parent.config["session"]["default_role"],
        username=user,
    )


@cli.command()
@click.argument("user")
@click.pass_context
def reset_password(ctx, user):
    """Reset a user's password to the given string."""
    reset_user_password(
        ctx.parent.connection,
        ctx.parent.cursor,
        password=ctx.parent.config["session"]["snowflake_password"],
        username=user,
    )


@cli.command()
@click.argument("user")
@click.pass_context
def unlock_user(ctx, user):
    """Unlock a user who has been locked out of snowflake due to repeated login failures."""
    unlock_user_account(ctx.parent.connection, ctx.parent.cursor, username=user)


if __name__ == "__main__":
    cli()
