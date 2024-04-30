import os
import html2text
from jinja2 import Environment, FileSystemLoader


def render_html(dictionary, template_name):
    root = os.getcwd()
    templates_dir = os.path.join(root, 'html_templates')
    compiled_dir = os.path.join(root, 'html_compiled')

    env = Environment(loader=FileSystemLoader(templates_dir))
    template = env.get_template(template_name)

    file_path = os.path.join(compiled_dir, f"{dictionary['sf_username']}.html")
    with open(file_path, 'w') as fh:
        fh.write(template.render(dictionary))

    return file_path


def parse_html(html_path):
    """

    Args:
        html_path: File path to the compiled html email

    Returns:
        msg_html: The HTML of the message as a string.
        msg_plain: The plain text of the message as a string. Ued as a fall back.
    """
    msg_html = open(html_path).read()
    msg_plain = html2text.html2text(msg_html)
    return msg_html, msg_plain
