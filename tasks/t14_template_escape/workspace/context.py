"""Template rendering context — holds variables, filters, and settings."""


class Context:
    """Rendering context for template evaluation.

    Attributes:
        variables: Dict of variable name → value.
        filters: Dict of filter name → callable.
        loader: TemplateLoader for include support.
        auto_escape: Whether to HTML-escape variable output.
    """

    def __init__(self, variables=None, filters=None, loader=None, auto_escape=True):
        self.variables = variables or {}
        self.filters = filters or {}
        self.loader = loader
        self.auto_escape = auto_escape

    def push(self, extra_vars):
        """Create a child context with additional variables.

        Used for for-loop scopes.
        """
        new_vars = dict(self.variables)
        new_vars.update(extra_vars)
        return Context(
            variables=new_vars,
            filters=self.filters,
            loader=self.loader,
            auto_escape=self.auto_escape,
        )

    def copy(self, **overrides):
        """Create a copy with optional overrides."""
        kwargs = {
            "variables": dict(self.variables),
            "filters": dict(self.filters),
            "loader": self.loader,
            "auto_escape": self.auto_escape,
        }
        kwargs.update(overrides)
        return Context(**kwargs)