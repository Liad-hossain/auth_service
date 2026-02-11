import logging
from pathlib import Path

from jinja2 import Template

logger = logging.getLogger("stdout")


def get_html_template(template_file_name: str) -> str:
    html_template = ""
    try:
        base_dir = Path(__file__).resolve().parents[1]
        template_path = base_dir / "htmls" / template_file_name
        html_template = template_path.read_text(encoding="utf-8")
    except Exception as e:
        logger.error(f"Error reading verification template at {template_path}: {e}")
    return html_template


def render_html_template(html_template: str, context: dict) -> str:
    try:
        template = Template(html_template)
        return template.render(**context)
    except Exception as e:
        logger.error(f"Error rendering HTML template: {e}")
    return html_template
