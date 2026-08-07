"""Thread pool for executing tasks with dependency management.

Tasks can submit subtasks and wait for their completion.
The pool manages a fixed number of worker threads and prevents
deadlock when nested tasks are submitted.
"""

import threading
import queue
import time


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
        """Wait for this task to complete.

        If called from within a pool worker thread, helps execute
        pending tasks from the queue to prevent deadlock when
        waiting for subtasks that haven't been picked up yet.
        """
        pool = getattr(_current_pool, 'current', None)
        if pool is not None:
            return pool._wait_with_help(self, timeout)

        if not self.done_event.wait(timeout):
            raise TimeoutError("Task timed out")
        if self.exception:
            raise self.exception
        return self.result


# Thread-local storage to track which pool a thread belongs to.
_current_pool = threading.local()


class ThreadPool:
    """A fixed-size thread pool for executing tasks.

    Supports nested task submission: when a task running in the pool
    submits a subtask and waits for it, the worker thread either
    executes the subtask directly (via execute_and_wait) or helps
    execute pending tasks from the queue (via wait) to prevent
    deadlock.
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
        _current_pool.current = self
        while self._running:
            try:
                task = self.task_queue.get(timeout=0.1)
                task.run()
            except queue.Empty:
                continue
            except Exception:
                pass

    def _wait_with_help(self, task, timeout):
        """Wait for a task, helping execute pending tasks while waiting.

        This prevents deadlock when a pool worker thread is waiting
        for a subtask that hasn't been picked up yet. The worker
        executes other pending tasks from the queue while waiting,
        so the subtask (or another task that unblocks the wait) can
        make progress.
        """
        deadline = time.monotonic() + timeout if timeout is not None else None

        while not task.done_event.is_set():
            if deadline is not None and time.monotonic() >= deadline:
                raise TimeoutError("Task timed out")

            try:
                pending = self.task_queue.get(timeout=0.1)
                pending.run()
            except queue.Empty:
                continue

        if task.exception:
            raise task.exception
        return task.result

    def submit(self, func, *args, **kwargs):
        """Submit a task to the pool and return a Task handle."""
        task = Task(func, *args, **kwargs)
        self.task_queue.put(task)
        return task

    def execute_and_wait(self, func, *args, **kwargs):
        """Submit a task and wait for its result.

        Safe to call from within a pool task — if called from a pool
        worker thread, the subtask is executed directly to prevent
        deadlock when all workers are busy.
        """
        if getattr(_current_pool, 'current', None) is self:
            # Already in a pool worker thread — execute directly
            # to avoid deadlock (all workers may be busy).
            task = Task(func, *args, **kwargs)
            task.run()
            return task.wait()

        task = self.submit(func, *args, **kwargs)
        return task.wait(timeout=10)

    def shutdown(self):
        """Shutdown the pool."""
        self._running = False
        for t in self.workers:
            t.join(timeout=5)