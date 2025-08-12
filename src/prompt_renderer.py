from jinja2 import Environment, FileSystemLoader, StrictUndefined, meta

from src import PROMPT_DIR


class PromptRenderer:
    def __init__(self, strict: bool = True, debug: bool = False):
        self.debug = debug
        self.env = Environment(
            loader=FileSystemLoader(PROMPT_DIR),
            undefined=StrictUndefined if strict else None,
            trim_blocks=True,
            lstrip_blocks=True
        )

    def _warn_unused(self, template_name: str, context: dict):
        if not self.debug:
            return
        source = self.env.loader.get_source(self.env, template_name)[0]
        parsed = self.env.parse(source)
        used_vars = meta.find_undeclared_variables(parsed)
        extra = context.keys() - used_vars
        if extra:
            print(f"⚠️ Unused variables: {sorted(extra)}")

    def render(self, template_name: str, context: dict = None) -> str:
        self._warn_unused(template_name, context)
        if ".j2" not in template_name:
            template_name += ".j2"
        template = self.env.get_template(template_name)
        return template.render(**(context or {}))