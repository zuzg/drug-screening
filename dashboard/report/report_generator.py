import jinja2
from datetime import datetime


def report_generator(content: dict):
    now = datetime.now()
    content["current_time"] = now.strftime("%H:%M:%S")
    template_loader = jinja2.FileSystemLoader("dashboard/report")
    template_env = jinja2.Environment(loader=template_loader)
    template = template_env.get_template("report.html")
    return template.render(content)
