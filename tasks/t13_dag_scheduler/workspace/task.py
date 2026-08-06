"""Task definition — a single unit of work in the pipeline."""


class Task:
    """A pipeline task with dependencies and an action.

    Attributes:
        name: Unique task identifier.
        requires: List of task names that must complete before this one.
        action: A callable that performs the task's work.
    """

    def __init__(self, name, requires, action):
        self.name = name
        self.requires = list(requires)
        self.action = action

    def __repr__(self):
        return (f"Task(name={self.name!r}, "
                f"requires={self.requires!r})")