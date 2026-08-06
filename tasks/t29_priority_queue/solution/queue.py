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
        # Aging factor: wait time increases effective priority
        self.age_bonus = 0

    def effective_priority(self):
        return self.priority - self.age_bonus

    def __lt__(self, other):
        return self.effective_priority() < other.effective_priority()


class PriorityQueue:
    """Min-heap based priority queue with aging and size limit."""

    def __init__(self, max_size=10000):
        self._heap = []
        self.max_size = max_size

    def push(self, task):
        if len(self._heap) >= self.max_size:
            # Evict lowest priority task
            lowest = max(self._heap, key=lambda t: t.effective_priority())
            self._heap.remove(lowest)
            heapq.heapify(self._heap)
        heapq.heappush(self._heap, task)

    def pop(self):
        if not self._heap:
            return None
        return heapq.heappop(self._heap)

    def peek(self):
        return self._heap[0] if self._heap else None

    def size(self):
        return len(self._heap)

    def age_all(self):
        """Increase age bonus for all waiting tasks (starvation prevention)."""
        AGE_INCREMENT = 0.1
        for task in self._heap:
            task.age_bonus += AGE_INCREMENT
        heapq.heapify(self._heap)


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
        self.queue.age_all()
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
        }