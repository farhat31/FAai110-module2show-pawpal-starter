import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pawpal_system import Owner, Pet, Scheduler, Task


def test_mark_complete_changes_task_status():
    task = Task(description="Feeding", duration_minutes=10)
    assert task.is_complete is False

    task.mark_complete()

    assert task.is_complete is True


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Mochi", type="dog", age=3, breed="Shiba Inu")
    assert len(pet.tasks) == 0

    pet.add_task(Task(description="Morning walk", duration_minutes=30))

    assert len(pet.tasks) == 1


def test_sort_tasks_by_time_returns_chronological_order():
    """Sorting correctness: tasks come back ordered by scheduled_time, not insertion order."""
    pet = Pet(name="Mochi", type="dog", age=3, breed="Shiba Inu")
    evening_task = Task(description="Evening walk", duration_minutes=20, scheduled_time="18:00")
    morning_task = Task(description="Morning walk", duration_minutes=20, scheduled_time="07:30")
    midday_task = Task(description="Lunch", duration_minutes=10, scheduled_time="12:00")
    for task in (evening_task, morning_task, midday_task):
        pet.add_task(task)

    scheduler = Scheduler(Owner(name="Alex", pets=[pet]))
    ordered = scheduler.sort_tasks_by_time([evening_task, morning_task, midday_task])

    assert ordered == [morning_task, midday_task, evening_task]


def test_sort_tasks_by_time_places_untimed_tasks_last():
    """Edge case: a task with no scheduled_time must not break the sort or jump the queue."""
    pet = Pet(name="Mochi", type="dog", age=3, breed="Shiba Inu")
    timed_task = Task(description="Morning walk", duration_minutes=20, scheduled_time="07:30")
    untimed_task = Task(description="Brush coat", duration_minutes=10)
    pet.add_task(timed_task)
    pet.add_task(untimed_task)

    scheduler = Scheduler(Owner(name="Alex", pets=[pet]))
    ordered = scheduler.sort_tasks_by_time([untimed_task, timed_task])

    assert ordered == [timed_task, untimed_task]


def test_marking_daily_task_complete_spawns_next_day_occurrence():
    """Recurrence logic: completing a daily task creates the following day's occurrence."""
    pet = Pet(name="Mochi", type="dog", age=3, breed="Shiba Inu")
    today = date(2026, 7, 8)
    task = Task(description="Feeding", duration_minutes=10, frequency="daily", due_date=today)
    pet.add_task(task)

    next_task = task.mark_complete(today=today)

    assert task.is_complete is True
    assert next_task is not None
    assert next_task.is_complete is False
    assert next_task.due_date == today + timedelta(days=1)
    assert next_task in pet.tasks


def test_marking_once_task_complete_does_not_spawn_new_task():
    """Edge case: a non-recurring task must not create a follow-up occurrence."""
    pet = Pet(name="Mochi", type="dog", age=3, breed="Shiba Inu")
    task = Task(description="Vet visit", duration_minutes=30, frequency="once")
    pet.add_task(task)

    next_task = task.mark_complete()

    assert next_task is None
    assert len(pet.tasks) == 1


def test_find_conflicts_flags_tasks_at_duplicate_times():
    """Conflict detection: two tasks scheduled at the exact same time must be flagged."""
    pet_a = Pet(name="Mochi", type="dog", age=3, breed="Shiba Inu")
    pet_b = Pet(name="Whiskers", type="cat", age=2, breed="Tabby")
    task_a = Task(description="Walk", duration_minutes=30, scheduled_time="08:00")
    task_b = Task(description="Feed", duration_minutes=15, scheduled_time="08:00")
    pet_a.add_task(task_a)
    pet_b.add_task(task_b)

    scheduler = Scheduler(Owner(name="Alex", pets=[pet_a, pet_b]))
    conflicts = scheduler.find_conflicts([task_a, task_b])

    assert conflicts == [(task_a, task_b)]


def test_find_conflicts_ignores_back_to_back_tasks():
    """Edge case: a task ending exactly when the next starts is not a conflict."""
    pet = Pet(name="Mochi", type="dog", age=3, breed="Shiba Inu")
    task_a = Task(description="Walk", duration_minutes=30, scheduled_time="08:00")
    task_b = Task(description="Feed", duration_minutes=15, scheduled_time="08:30")
    pet.add_task(task_a)
    pet.add_task(task_b)

    scheduler = Scheduler(Owner(name="Alex", pets=[pet]))
    conflicts = scheduler.find_conflicts([task_a, task_b])

    assert conflicts == []
