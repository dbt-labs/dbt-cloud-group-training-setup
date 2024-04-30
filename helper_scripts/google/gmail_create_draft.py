from googleapiclient.discovery import build


def create_gmail_draft(service, message_body, user_id="me",):
    """Create and insert a draft email. Print the returned draft's message and id.

    Args:
      service: Authorized Gmail API service instance.
      user_id: User's email address. The special value "me"
      can be used to indicate the authenticated user.
      message_body: The body of the email message, including headers.

    Returns:
      Draft object, including draft id and message meta data.
    """
    try:
        draft = service.users().drafts().create(
          userId=user_id, body=message_body).execute()
        print("Draft \u2714", end=" ")

        return draft

    except Exception as e:
        print("An error occurred: {}".format(e))
        raise e
