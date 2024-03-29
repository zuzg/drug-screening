import jinja2
from datetime import datetime


def generate_jinja_report(content: dict) -> str:
    """
    Generate jinja report using

    :param content: dict with variables needed to generate html file
    :return: rendered html file (string)
    """
    now = datetime.now()
    content["current_day"] = now.strftime("%d-%m-%y")
    content["current_time"] = now.strftime("%H:%M:%S")
    template_loader = jinja2.FileSystemLoader("dashboard/pages/correlation/report")
    template_env = jinja2.Environment(loader=template_loader)
    template = template_env.get_template("report.html")
    return template.render(content)
