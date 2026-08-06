"""Priority-based task queue with starvation prevention."""

import heapq
import time
from collections import defaultdict


class Task:
    def __init__(self, name, priority, func):
        self.name = name
        self.priority = priority
        self.func = func
        self.created_at = time.time()

    def __lt__(self, other):
        return self.priority < other.priority


class PriorityQueue:
    """Min-heap based priority queue. Lower number = higher priority.

    BUG 1: No starvation prevention — low-priority tasks can wait forever.
    BUG 2: No size limit — memory can grow unbounded.
    """

    def __init__(self):
        self._heap = []

    def push(self, task):
        heapq.heappush(self._heap, task)

    def pop(self):
        if not self._heap:
            return None
        return heapq.heappop(self._heap)

    def peek(self):
        return self._heap[0] if self._heap else None

    def size(self):
        return len(self._heap)


class TaskScheduler:
    """Schedules and executes tasks from a priority queue."""

    def __init__(self):
        self.queue = PriorityQueue()
        self.completed = 0
        self.wait_times = defaultdict(float)

    def submit(self, name, priority, func):
        task = Task(name, priority, func)
        self.queue.push(task)

    def run_one(self):
        task = self.queue.pop()
        if task is None:
            return None
        self.wait_times[task.priority] += time.time() - task.created_at
        task.func()
        self.completed += 1
        return task.name

    def run_all(self):
        while self.queue.size() > 0:
            self.run_one()

    def stats(self):
        return {
            "completed": self.completed,
            "pending": self.queue.size(),
            "avg_wait": {p: t / max(1, self.completed)
                         for p, t in self.wait_times.items()},
        }