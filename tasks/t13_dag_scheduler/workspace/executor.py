"""Task executor — runs tasks sequentially or in parallel."""


class Executor:
    """Executes pipeline tasks.

    For this implementation, parallel execution is simulated by
    running tasks sequentially but tracking which could have run
    concurrently.
    """

    def __init__(self, parallel=False):
        self.parallel = parallel

    def run(self, task, context=None):
        """Run a single task's action."""
        if context is None:
            context = {}
        return task.action(context)