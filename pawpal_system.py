"""Backend logic layer for PawPal+."""

from dataclasses import dataclass, field, replace
from datetime import date, datetime, timedelta
from typing import List, Optional, Tuple, Union

PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}
PRIORITY_VALUE = {"high": 3, "medium": 2, "low": 1}
RECURRING_INTERVALS = {"daily": timedelta(days=1), "weekly": timedelta(days=7)}


@dataclass
class Task:
    description: str
    duration_minutes: int
    frequency: str = "daily"
    priority: str = "medium"
    is_complete: bool = False
    pet: Optional["Pet"] = None
    scheduled_time: Optional[str] = None  # "HH:MM", 24-hour clock
    splittable: bool = False
    min_duration_minutes: Optional[int] = None
    created_at: date = field(default_factory=date.today)
    last_completed: Optional[date] = None
    due_date: date = field(default_factory=date.today)

    def mark_complete(self, today: Optional[date] = None) -> Optional["Task"]:
        """Mark this task as done. Daily/weekly tasks spawn their next occurrence,
        due today + the recurrence interval, so the series keeps going."""
        today = today or date.today()
        self.is_complete = True
        self.last_completed = today
        return self.spawn_next_occurrence(today)

    def mark_incomplete(self) -> None:
        """Mark this task as not done."""
        self.is_complete = False

    def spawn_next_occurrence(self, today: Optional[date] = None) -> Optional["Task"]:
        """Create the next occurrence of a recurring task, due one interval from today.

        "once" tasks have no entry in RECURRING_INTERVALS and never spawn a follow-up.
        The new Task is a copy of this one (dataclasses.replace) reset to incomplete,
        with created_at/due_date advanced, and is appended to the same pet's task list.

        Args:
            today: Date to measure the interval from; defaults to date.today().

        Returns:
            The newly created Task, or None if this task's frequency doesn't recur.
        """
        interval = RECURRING_INTERVALS.get(self.frequency)
        if interval is None:
            return None
        today = today or date.today()
        next_task = replace(
            self,
            is_complete=False,
            last_completed=None,
            created_at=today,
            due_date=today + interval,
        )
        if self.pet is not None:
            self.pet.add_task(next_task)
        return next_task

    def days_waiting(self, today: Optional[date] = None) -> int:
        """Days this task has been overdue past its due date, used to age up urgency."""
        if self.is_complete:
            return 0
        today = today or date.today()
        return max((today - self.due_date).days, 0)

    def time_range(self, today: Optional[date] = None) -> Optional[Tuple[datetime, datetime]]:
        """Return (start, end) datetimes for this task if it has a valid scheduled time.

        A malformed scheduled_time (not "HH:MM") is treated as unscheduled rather than
        raising, so a bad value can't crash conflict detection.
        """
        if not self.scheduled_time:
            return None
        anchor = today or date.today()
        try:
            start_time = datetime.strptime(self.scheduled_time, "%H:%M").time()
        except ValueError:
            return None
        start = datetime.combine(anchor, start_time)
        return start, start + timedelta(minutes=self.duration_minutes)

    def overlaps(self, other: "Task") -> bool:
        """Check whether this task's scheduled time overlaps another task's."""
        this_range = self.time_range()
        other_range = other.time_range()
        if not this_range or not other_range:
            return False
        return this_range[0] < other_range[1] and other_range[0] < this_range[1]


@dataclass
class Pet:
    name: str
    type: str
    age: int
    breed: str
    needs: str = ""
    vet: str = ""
    insurance: str = ""
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a task to this pet, linking it back to the pet."""
        task.pet = self
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Detach a task from this pet, if present."""
        if task in self.tasks:
            self.tasks.remove(task)

    def get_tasks(self, include_complete: bool = True) -> List[Task]:
        """Return this pet's tasks, optionally excluding completed ones."""
        if include_complete:
            return list(self.tasks)
        return [task for task in self.tasks if not task.is_complete]


class Owner:
    def __init__(
        self,
        name: str,
        pets: Optional[List[Pet]] = None,
        availability: Optional[List[str]] = None,
        preferences: Optional[List[str]] = None,
    ):
        self.name = name
        self.pets = pets or []
        self.availability = availability or []
        self.preferences = preferences or []

    @property
    def num_pets(self) -> int:
        """Return how many pets this owner has."""
        return len(self.pets)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's list of pets."""
        self.pets.append(pet)

    def remove_pet(self, pet: Pet) -> None:
        """Remove a pet from this owner's list of pets, if present."""
        if pet in self.pets:
            self.pets.remove(pet)

    def add_availability(self, slot: str) -> None:
        """Add a free time slot to this owner's availability."""
        self.availability.append(slot)

    def change_availability(self, old_slot: str, new_slot: str) -> None:
        """Replace an existing availability slot with a new one."""
        if old_slot in self.availability:
            self.availability[self.availability.index(old_slot)] = new_slot

    def add_preference(self, preference: str) -> None:
        """Add a scheduling preference for this owner."""
        self.preferences.append(preference)

    def get_all_tasks(self, include_complete: bool = True) -> List[Task]:
        """Return tasks across all of this owner's pets."""
        tasks: List[Task] = []
        for pet in self.pets:
            tasks.extend(pet.get_tasks(include_complete=include_complete))
        return tasks


class Scheduler:
    """Retrieves, organizes, and manages tasks across an owner's pets."""

    def __init__(self, owner: Owner):
        self.owner = owner

    def get_pending_tasks(self, pet: Optional[Pet] = None, today: Optional[date] = None) -> List[Task]:
        """Return tasks eligible to be scheduled today: incomplete and already due.

        A recurring task's next occurrence exists as soon as the current one is marked
        complete (see Task.spawn_next_occurrence), but is excluded here until its
        due_date arrives, so tomorrow's walk doesn't show up in today's plan.

        Args:
            pet: Restrict to one pet's tasks; defaults to every pet the owner has.
            today: Date to compare due_date against; defaults to date.today().

        Returns:
            Incomplete tasks with due_date <= today.
        """
        today = today or date.today()
        pets = [pet] if pet else self.owner.pets
        return [
            task
            for p in pets
            for task in p.get_tasks(include_complete=False)
            if task.due_date <= today
        ]

    def filter_tasks(self, pet: Optional[Union[Pet, str]] = None, status: str = "all") -> List[Task]:
        """Filter tasks by pet (a Pet instance or pet name) and/or status ('all', 'complete', 'incomplete')."""
        if isinstance(pet, str):
            pets = [p for p in self.owner.pets if p.name == pet]
        elif pet:
            pets = [pet]
        else:
            pets = self.owner.pets
        tasks = [task for p in pets for task in p.get_tasks()]
        if status == "complete":
            return [task for task in tasks if task.is_complete]
        if status == "incomplete":
            return [task for task in tasks if not task.is_complete]
        return tasks

    def priority_score(self, task: Task, today: Optional[date] = None) -> float:
        """Compute an urgency score for a task; lower means more urgent.

        Starts from the task's priority tier (high/medium/low), then adjusts:
        subtracts up to 5 points for how many days the task is overdue (aging, so a
        neglected low-priority task can eventually outrank a fresh high-priority one),
        and subtracts 3 more if the description matches one of the owner's preferences.

        Args:
            task: The task to score.
            today: Date to measure overdue-ness from; defaults to date.today().

        Returns:
            A numeric score usable as a sort key (see sort_tasks).
        """
        score = PRIORITY_ORDER.get(task.priority, 1) * 10
        score -= min(task.days_waiting(today), 5)  # aging: long-neglected tasks creep up in urgency
        if any(pref.lower() in task.description.lower() for pref in self.owner.preferences):
            score -= 3  # owner-preferred tasks jump ahead of same-tier peers
        return score

    def sort_tasks(self, tasks: Optional[List[Task]] = None) -> List[Task]:
        """Sort tasks by urgency score (priority + age + preference), then shortest duration."""
        tasks = self.get_pending_tasks() if tasks is None else tasks
        return sorted(tasks, key=lambda task: (self.priority_score(task), task.duration_minutes))

    def sort_tasks_by_time(self, tasks: Optional[List[Task]] = None) -> List[Task]:
        """Sort tasks chronologically by scheduled_time.

        scheduled_time is a zero-padded "HH:MM" string, so plain string comparison
        already sorts chronologically ("09:00" < "13:30" as strings, same order as times).
        Tasks with no scheduled_time are appended after all timed ones.

        Args:
            tasks: Tasks to sort; defaults to this owner's pending tasks.

        Returns:
            Timed tasks in chronological order, followed by untimed tasks.
        """
        tasks = self.get_pending_tasks() if tasks is None else tasks
        timed = sorted((t for t in tasks if t.scheduled_time), key=lambda t: t.scheduled_time)
        untimed = [t for t in tasks if not t.scheduled_time]
        return timed + untimed

    def find_conflicts(self, tasks: Optional[List[Task]] = None) -> List[Tuple[Task, Task]]:
        """Detect scheduling clashes: any two tasks whose time ranges overlap.

        Untimed tasks are ignored. Timed tasks are sorted by start time first so each
        pair is only compared once (not once as (a, b) and again as (b, a)); it works
        the same whether the two tasks belong to the same pet or different pets, since
        it only looks at scheduled_time and duration_minutes.

        Args:
            tasks: Tasks to check; defaults to this owner's pending tasks.

        Returns:
            A list of (task_a, task_b) pairs with overlapping time ranges.
        """
        tasks = self.get_pending_tasks() if tasks is None else tasks
        timed = sorted((t for t in tasks if t.scheduled_time), key=lambda t: t.scheduled_time)
        conflicts = []
        for i, task in enumerate(timed):
            for other in timed[i + 1 :]:
                if task.overlaps(other):
                    conflicts.append((task, other))
        return conflicts

    def get_conflict_warnings(self, tasks: Optional[List[Task]] = None) -> List[str]:
        """Turn find_conflicts pairs into printable warning strings.

        A thin formatting layer over find_conflicts: a scheduling clash always comes
        back as a message to display, never an exception, so callers (CLI or UI) can
        surface it without special-casing errors.

        Args:
            tasks: Tasks to check; defaults to this owner's pending tasks.

        Returns:
            One warning string per conflicting pair, e.g.
            "Warning: 'A' (Pet1 at 08:00) conflicts with 'B' (Pet2 at 08:00)".
        """
        warnings = []
        for task_a, task_b in self.find_conflicts(tasks):
            pet_a = task_a.pet.name if task_a.pet else "Unknown pet"
            pet_b = task_b.pet.name if task_b.pet else "Unknown pet"
            warnings.append(
                f"Warning: '{task_a.description}' ({pet_a} at {task_a.scheduled_time}) conflicts "
                f"with '{task_b.description}' ({pet_b} at {task_b.scheduled_time})"
            )
        return warnings

    def build_daily_plan(self, available_minutes: int) -> List[Task]:
        """Greedily fill available time round-robin across pets, so no pet is crowded out.

        Algorithm: each pet gets its own urgency-sorted queue (see sort_tasks). Then,
        in rounds, every pet with tasks left gets one turn: place its most urgent task
        that fits in the remaining time, or if none fits exactly, take a shortened slot
        from a splittable task (down to its min_duration_minutes) to use up the rest of
        the budget. A pet drops out once its queue is empty; the loop stops once a full
        round places nothing. This favors fairness across pets over maximum time
        utilization — see build_optimal_plan for the latter.

        Args:
            available_minutes: Total minutes to schedule today.

        Returns:
            The list of tasks placed into today's plan (partial tasks appear as short
            copies via dataclasses.replace, leaving the original task untouched).
        """
        remaining = available_minutes
        plan: List[Task] = []
        queues = {pet.name: self.sort_tasks(self.get_pending_tasks(pet)) for pet in self.owner.pets}
        pets_cycle = [pet for pet in self.owner.pets if queues[pet.name]]

        while pets_cycle and remaining > 0:
            progressed = False
            for pet in list(pets_cycle):
                queue = queues[pet.name]
                fit = next((t for t in queue if t.duration_minutes <= remaining), None)
                if fit is not None:
                    plan.append(fit)
                    remaining -= fit.duration_minutes
                    queue.remove(fit)
                    progressed = True
                else:
                    partial_source = next(
                        (
                            t
                            for t in queue
                            if t.splittable and t.min_duration_minutes and t.min_duration_minutes <= remaining
                        ),
                        None,
                    )
                    if partial_source is not None:
                        plan.append(replace(partial_source, duration_minutes=remaining, pet=pet))
                        queue.remove(partial_source)
                        remaining = 0
                        progressed = True
                if not queue and pet in pets_cycle:
                    pets_cycle.remove(pet)
                if remaining <= 0:
                    break
            if not progressed:
                break
        return plan

    def build_optimal_plan(self, available_minutes: int) -> List[Task]:
        """0/1 knapsack: pick the subset of tasks maximizing total priority-weighted value
        that fits within available_minutes, ignoring which pet each task belongs to.

        Standard bottom-up knapsack DP: dp[i][t] is the best value achievable using only
        the first i tasks with t minutes of capacity. Each task is either skipped
        (dp[i-1][t]) or, if it fits, taken (dp[i-1][t - duration] + its value), whichever
        is larger. The final row is then walked backwards to recover which tasks were
        selected. Runs in O(n * available_minutes) time and space, where n is the number
        of pending tasks. Use this over build_daily_plan when the goal is squeezing the
        most value out of limited time rather than spreading tasks fairly across pets.

        Args:
            available_minutes: Total minutes to schedule today.

        Returns:
            The list of tasks selected, in their original relative order.
        """
        tasks = self.get_pending_tasks()
        n = len(tasks)
        dp = [[0] * (available_minutes + 1) for _ in range(n + 1)]
        for i, task in enumerate(tasks, start=1):
            value = PRIORITY_VALUE.get(task.priority, 2)
            duration = task.duration_minutes
            for t in range(available_minutes + 1):
                dp[i][t] = dp[i - 1][t]
                if duration <= t:
                    dp[i][t] = max(dp[i][t], dp[i - 1][t - duration] + value)

        plan: List[Task] = []
        t = available_minutes
        for i in range(n, 0, -1):
            if dp[i][t] != dp[i - 1][t]:
                plan.append(tasks[i - 1])
                t -= tasks[i - 1].duration_minutes
        plan.reverse()
        return plan

    def mark_task_complete(self, task: Task) -> Optional[Task]:
        """Mark a task as complete; returns the newly spawned occurrence if the task recurs."""
        return task.mark_complete()

    def explain_plan(self, plan: List[Task]) -> List[str]:
        """Produce a human-readable reason string for each task in the plan."""
        explanations = []
        conflicted = {id(t) for pair in self.find_conflicts(plan) for t in pair}
        for task in plan:
            pet_name = task.pet.name if task.pet else "Unknown pet"
            when = f" at {task.scheduled_time}" if task.scheduled_time else ""
            flag = " [conflict: overlaps another scheduled task]" if id(task) in conflicted else ""
            explanations.append(
                f"{task.description} for {pet_name}{when} "
                f"({task.duration_minutes} min, priority: {task.priority}){flag}"
            )
        return explanations
