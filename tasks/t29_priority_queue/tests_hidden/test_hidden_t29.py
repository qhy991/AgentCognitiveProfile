import time, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from queue import TaskScheduler, PriorityQueue

def test_basic_execution():
    s = TaskScheduler()
    results = []
    s.submit("a", 1, lambda: results.append("a"))
    s.submit("b", 2, lambda: results.append("b"))
    s.run_all()
    assert results == ["a", "b"]

def test_priority_order():
    s = TaskScheduler()
    results = []
    s.submit("low", 10, lambda: results.append("low"))
    s.submit("high", 1, lambda: results.append("high"))
    s.run_all()
    assert results[0] == "high"

def test_starvation_prevention():
    s = TaskScheduler()
    results = []
    # Submit many high-priority tasks, then a low-priority one
    for i in range(100):
        s.submit(f"high{i}", 1, lambda i=i: results.append(f"h{i}"))
    s.submit("low", 10, lambda: results.append("low"))
    s.run_all()
    assert "low" in results, f"Low priority task starved! Results: {results[:5]}..."

def test_queue_size_limit():
    q = PriorityQueue(max_size=50)
    from queue import Task
    for i in range(100):
        q.push(Task(f"t{i}", i, lambda: None))
    assert q.size() <= 50

def test_aging():
    t1 = Task("a", 5, lambda: None)
    t2 = Task("b", 5, lambda: None)
    t2.age_bonus = 2
    assert t2.effective_priority() < t1.effective_priority()
