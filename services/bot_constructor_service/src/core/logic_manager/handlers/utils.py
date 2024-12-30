from functools import lru_cache
from typing import Any

from jinja2 import Environment, BaseLoader


template_env = Environment(loader=BaseLoader())


@lru_cache(maxsize=128)
def get_template(template_str: str) -> Any:
    """Returns a cached Jinja2 template."""
    return template_env.from_string(template_str)