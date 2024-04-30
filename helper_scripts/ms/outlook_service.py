import json
from msgraph.core import GraphClient
from azure.identity import InteractiveBrowserCredential


def azure_client_id():
    """Load client ID from credential store in creds folder"""
    return json.load(open("creds/azure_credentials.json"))['client_id']


def get_credits():
    """
    Get Microsoft Azure credentials for the graph api. Using the interactive
    browser credential function from azure.identity

    Returns:
        Azure credential object.
    """

    creds = InteractiveBrowserCredential(
        client_id=azure_client_id()
    )

    return creds


def outlook_service():
    """

    Returns:

    """
    creds = get_credits()
    print('Created outlook service')
    return GraphClient(credential=creds)
