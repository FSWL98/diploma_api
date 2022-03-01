from jinja2 import Template, Environment, TemplateSyntaxError
from flask import current_app


def render_template(template_name, data):
    template = Template(open(f"{current_app.config['API_TEMPLATES_DIR']}/{template_name}.jinja2").read())
    return template.render(data)


def is_jinja_template_valid(template):
    env = Environment()
    try:
        t = env.from_string(template)
    except TemplateSyntaxError:
        return False
    return True
