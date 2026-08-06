"""Model base class — the declarative base for defining table schemas."""

from fields import Field


class ModelMeta(type):
    """Metaclass that collects Field instances into a table schema."""

    def __new__(mcs, name, bases, namespace):
        cls = super().__new__(mcs, name, bases, namespace)
        if name == "Model":
            return cls
        fields = {}
        for key, value in namespace.items():
            if isinstance(value, Field):
                value.name = key
                fields[key] = value
        cls._fields = fields
        cls._tablename = name.lower()
        return cls


class Model(metaclass=ModelMeta):
    """Base class for all model definitions.

    Example:
        class User(Model):
            id = IntegerField()
            name = StringField()
            age = IntegerField()
    """

    _fields = {}
    _tablename = ""

    def __init__(self, **kwargs):
        for key, field in self._fields.items():
            setattr(self, key, kwargs.get(key, field.default))

    def to_dict(self):
        return {key: getattr(self, key) for key in self._fields}

    def __repr__(self):
        attrs = ", ".join(f"{k}={getattr(self, k)!r}" for k in self._fields)
        return f"{self.__class__.__name__}({attrs})"