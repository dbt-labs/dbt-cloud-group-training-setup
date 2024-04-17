import os
from jinja2 import Environment, FileSystemLoader


def render_html(dictionary, template_name):
    root = os.getcwd()
    templates_dir = os.path.join(root, 'html_templates')
    compiled_dir = os.path.join(root, 'html_compiled')

    env = Environment(loader=FileSystemLoader(templates_dir))
    template = env.get_template(template_name)

    filename = os.path.join(compiled_dir, f"{dictionary['sf_username']}.html")
    with open(filename, 'w') as fh:
        fh.write(template.render(dictionary))

    return filename


def main(dictionary, template_name):
    file_path = render_html(dictionary, template_name)
    print("HTML \u2714", end=" ")
    return file_path
