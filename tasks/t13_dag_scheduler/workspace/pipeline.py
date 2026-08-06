"""Pipeline DAG scheduler — executes tasks respecting dependency order.

A pipeline is a set of tasks with dependencies. Each task declares what it
depends on via `requires`. The scheduler builds a DAG, computes a topological
order, and executes tasks in that order (within each level, tasks can run
concurrently).

Example:
    pipeline = Pipeline()
    pipeline.add_task("fetch", requires=[], action=fetch_data)
    pipeline.add_task("clean", requires=["fetch"], action=clean_data)
    pipeline.add_task("analyze", requires=["clean"], action=analyze)
    pipeline.run()
"""

from dag import DAG
from task import Task
from executor import Executor
from errors import PipelineError


class Pipeline:
    """Orchestrates a set of tasks with dependencies."""

    def __init__(self):
        self._tasks = {}  # {name: Task}
        self._dag = DAG()

    def add_task(self, name, requires, action):
        """Add a task to the pipeline.

        Args:
            name: Unique task name.
            requires: List of task names this task depends on.
            action: A callable that performs the task.
        """
        task = Task(name=name, requires=list(requires), action=action)
        self._tasks[name] = task
        self._dag.add_node(name)
        for req in requires:
            self._dag.add_edge(req, name)

    def run(self, parallel=False):
        """Execute all tasks in dependency order.

        Args:
            parallel: If True, tasks at the same level run concurrently.
        """
        order = self._dag.topological_sort()
        executor = Executor(parallel=parallel)
        results = {}
        for task_name in order:
            task = self._tasks[task_name]
            # Check all dependencies completed successfully
            deps_ok = all(
                results.get(dep) == "ok"
                for dep in task.requires
            )
            if not deps_ok:
                raise PipelineError(
                    f"task '{task_name}': dependencies not satisfied"
                )
            # Execute and record result
            try:
                task.action()
                results[task_name] = "ok"
            except Exception as e:
                results[task_name] = "failed"
                raise PipelineError(
                    f"task '{task_name}' failed: {e}"
                ) from e
        return results

    def get_order(self):
        """Return the execution order (without actually running)."""
        return self._dag.topological_sort()