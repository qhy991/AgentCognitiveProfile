"""Thread pool for executing tasks with dependency management.

Tasks can submit subtasks and wait for their completion.
The pool manages a fixed number of worker threads.
"""

import threading
import queue


class Task:
    """A unit of work that can be submitted to the thread pool."""

    def __init__(self, func, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.result = None
        self.exception = None
        self.done_event = threading.Event()

    def run(self):
        try:
            self.result = self.func(*self.args, **self.kwargs)
        except Exception as e:
            self.exception = e
        finally:
            self.done_event.set()

    def wait(self, timeout=None):
        """Wait for this task to complete."""
        if not self.done_event.wait(timeout):
            raise TimeoutError("Task timed out")
        if self.exception:
            raise self.exception
        return self.result


class ThreadPool:
    """A fixed-size thread pool for executing tasks.

    BUG: When a task running in the pool submits a subtask and waits
    for it, the system can deadlock if all workers are busy. The pool
    has no mechanism to detect or prevent this deadlock.
    """

    def __init__(self, num_workers):
        self.num_workers = num_workers
        self.task_queue = queue.Queue()
        self.workers = []
        self._running = True

    def start(self):
        """Start worker threads."""
        for _ in range(self.num_workers):
            t = threading.Thread(target=self._worker_loop, daemon=True)
            t.start()
            self.workers.append(t)

    def _worker_loop(self):
        """Main worker loop."""
        while self._running:
            try:
                task = self.task_queue.get(timeout=0.1)
                task.run()
            except queue.Empty:
                continue
            except Exception:
                pass

    def submit(self, func, *args, **kwargs):
        """Submit a task to the pool and return a Task handle.

        BUG: If called from within a running task and the caller
        calls task.wait(), it can deadlock because all workers
        may be busy, including the caller.
        """
        task = Task(func, *args, **kwargs)
        self.task_queue.put(task)
        return task

    def execute_and_wait(self, func, *args, **kwargs):
        """Submit a task and wait for its result.

        Convenience method that combines submit and wait.
        BUG: Can deadlock if called from within a pool task.
        """
        task = self.submit(func, *args, **kwargs)
        return task.wait(timeout=10)

    def shutdown(self):
        """Shutdown the pool."""
        self._running = False
        for t in self.workers:
            t.join(timeout=5)