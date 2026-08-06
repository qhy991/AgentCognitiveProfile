"""Field types for model definitions."""


class Field:
    """Base field descriptor."""

    def __init__(self, default=None, nullable=True):
        self.name = None
        self.default = default
        self.nullable = nullable

    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name!r})"


class IntegerField(Field):
    """Integer column."""
    def __init__(self, default=0, **kwargs):
        super().__init__(default=default, **kwargs)


class StringField(Field):
    """String column."""
    def __init__(self, default="", max_length=255, **kwargs):
        super().__init__(default=default, **kwargs)
        self.max_length = max_length


class FloatField(Field):
    """Float column."""
    def __init__(self, default=0.0, **kwargs):
        super().__init__(default=default, **kwargs)


class BooleanField(Field):
    """Boolean column."""
    def __init__(self, default=False, **kwargs):
        super().__init__(default=default, **kwargs)