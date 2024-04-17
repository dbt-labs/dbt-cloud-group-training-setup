import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import html2text


def parse_html(html_path):
    msg_html = open(html_path).read()
    msg_plain = html2text.html2text(msg_html)
    return msg_html, msg_plain


def create_reply(sender, to, subject, msg_html, msg_plain, messageId):
    """Create a message for an email.

    Args:
      sender: Email address of the sender.
      to: Email address of the receiver.
      subject: The subject of the email message.
      msg_html: The HTML of the message as a string.
      msg_plain: The plain text of the message as a string. Used as a fallback.

    Returns:
      An object containing a base64url encoded email object.
    """
    message = MIMEMultipart('alternative')

    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    message['In-Reply-To'] = messageId
    message['References'] = messageId

    body_mime = MIMEText(msg_plain, 'plain')
    message.attach(body_mime)

    html_mime = MIMEText(msg_html, 'html')
    message.attach(html_mime)

    print("Message \u2714", end=" ")
    print(type(message))
    return message


def create_draft(service, user_id, message_body, threadId):
    """Create and insert a draft email. Print the returned draft's message and id.

    Args:
      service: Authorized Gmail API service instance.
      user_id: User's email address. The special value "me"
      can be used to indicate the authenticated user.
      message_body: The body of the email message, including headers.

    Returns:
      Draft object, including draft id and message meta data.
    """
    print(threadId)
    print(type(threadId))
    msg_raw = {'raw': base64.urlsafe_b64encode(message_body.as_string().encode(
        "utf-8")).decode("utf-8"), 'threadId': threadId}
    message = {'message': msg_raw}

    try:
        draft = service.users().drafts().create(
          userId=user_id, body=message).execute()
        print("Draft \u2714", end=" ")
        print(draft)
        return draft

    except Exception as e:
        print("An error occurred: {}".format(e))
        raise e


def main(learner_dict, service, subject, html_path):

    messageId = learner_dict['messageId']
    threadId = learner_dict['threadId']
    sender = "kcoapman@fishtownanalytics.com"
    to = learner_dict['email']
    msg_html, msg_plain = parse_html(html_path)

    message = create_reply(sender, to, subject, msg_html, msg_plain, messageId)

    create_draft(service, "me", message, threadId)
