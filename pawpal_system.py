"""Backend logic layer for PawPal+."""

from dataclasses import dataclass, field
from typing import List, Optional

PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


@dataclass
class Task:
    description: str
    duration_minutes: int
    frequency: str = "daily"
    priority: str = "medium"
    is_complete: bool = False
    pet: Optional["Pet"] = None

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.is_complete = True

    def mark_incomplete(self) -> None:
        """Mark this task as not done."""
        self.is_complete = False


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

    def get_pending_tasks(self) -> List[Task]:
        """Return all not-yet-complete tasks across the owner's pets."""
        return [task for task in self.owner.get_all_tasks() if not task.is_complete]

    def sort_tasks(self, tasks: Optional[List[Task]] = None) -> List[Task]:
        """Sort tasks by priority (high first), then by shortest duration."""
        tasks = self.get_pending_tasks() if tasks is None else tasks
        return sorted(
            tasks,
            key=lambda task: (PRIORITY_ORDER.get(task.priority, 1), task.duration_minutes),
        )

    def build_daily_plan(self, available_minutes: int) -> List[Task]:
        """Greedily fill the available time with the highest-priority tasks that fit."""
        plan: List[Task] = []
        remaining = available_minutes
        for task in self.sort_tasks():
            if task.duration_minutes <= remaining:
                plan.append(task)
                remaining -= task.duration_minutes
        return plan

    def mark_task_complete(self, task: Task) -> None:
        """Mark a task as complete."""
        task.mark_complete()

    def explain_plan(self, plan: List[Task]) -> List[str]:
        """Produce a human-readable reason string for each task in the plan."""
        explanations = []
        for task in plan:
            pet_name = task.pet.name if task.pet else "Unknown pet"
            explanations.append(
                f"{task.description} for {pet_name} "
                f"({task.duration_minutes} min, priority: {task.priority})"
            )
        return explanations
