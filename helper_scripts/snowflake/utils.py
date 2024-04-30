import snowflake.connector


def sf_connect(config):

    ctx = snowflake.connector.connect(
        **config
    )

    cs = ctx.cursor()

    return cs, ctx


def sf_run_query(connection, cursor, query):
    try:
        cursor.execute(query)
        print("Query \u2714", end=" ")

    except Exception as e:
        print("Query \u2716", end=" ")
        print("\n\nERROR: ", e, "\n")


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
    sf_run_query(connection, cursor, create_user_query)
    sf_run_query(connection, cursor, grant_role_query)
    print("DONE\n")
