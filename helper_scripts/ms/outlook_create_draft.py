
def create_outlook_draft(service, message):
    """
    Create and insert a draft email. Print the returned draft's message and id.

    Args:
      service: Authorized Outlook API service instance.
      message: The body of the email message, including headers, in Mime format.

    Returns:
      Reponse object, including draft id and message meta data.

    """

    try:
        draft_response = service.post('/me/messages',
                data=message['message']['raw'],
                headers={'Content-Type': 'text/plain'})
        print("Draft \u2714", end=" ")

        return draft_response

    except Exception as e:
        print("An error occurred: {}".format(e))
        raise e
