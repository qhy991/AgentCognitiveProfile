"""Mini template engine — Jinja2-like syntax with auto-escaping.

Supports:
    {{ variable }}              — output with auto-escaping
    {% if condition %}...{% endif %}
    {% for item in items %}...{% endfor %}
    {% include "other.html" %}  — include another template
    {% macro name(args) %}...{% endmacro %}
    {{ name|upper }}            — filters
"""

from lexer import tokenize
from parser import parse
from compiler import compile_template
from context import Context
from filters import DEFAULT_FILTERS


class Template:
    """A compiled template that can be rendered with a context."""

    def __init__(self, source, name="<string>"):
        self.source = source
        self.name = name
        self._loader = None
        tokens = tokenize(source)
        self._ast = parse(tokens)
        self._compiled = compile_template(self._ast)

    def render(self, **context_vars):
        """Render the template with the given variables."""
        ctx = Context(
            variables=context_vars,
            filters=dict(DEFAULT_FILTERS),
            loader=self._loader,
            auto_escape=True,
        )
        return self._compiled(ctx)

    def set_loader(self, loader):
        """Set the template loader for {% include %} support."""
        self._loader = loader


class TemplateLoader:
    """Loads templates by name (for include/macro support)."""

    def __init__(self, templates=None):
        self._templates = templates or {}  # {name: source_string}

    def register(self, name, source):
        """Register a template by name."""
        self._templates[name] = source

    def load(self, name):
        """Load a template by name, returning a Template object."""
        if name not in self._templates:
            raise ValueError(f"template not found: {name}")
        t = Template(self._templates[name], name=name)
        t.set_loader(self)
        return t