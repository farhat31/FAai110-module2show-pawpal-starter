"""Backend logic layer for PawPal+.

Classes here mirror diagrams/uml.mmd. Method bodies are stubs to be
implemented as scheduling logic is built out.
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Pet:
    name: str
    type: str
    age: int
    breed: str
    needs: str
    vet: str
    insurance: str

    def insert_info(self, info: dict) -> None:
        pass

    def edit_info(self, field: str, value: object) -> None:
        pass


@dataclass
class Task:
    pet: Pet
    description: str
    priority: str
    frequency: str
    status: str = "pending"

    def add_task(self, task: "Task") -> None:
        pass

    def remove_task(self, task: "Task") -> None:
        pass

    def change_status(self, status: str) -> None:
        pass

    def assign_task(self, owner: "Owner") -> None:
        pass


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
        return len(self.pets)

    def add_pet(self, pet: Pet) -> None:
        pass

    def remove_pet(self, pet: Pet) -> None:
        pass

    def add_availability(self, slot: str) -> None:
        pass

    def change_availability(self, slot: str) -> None:
        pass

    def add_preference(self, preference: str) -> None:
        pass


class Schedule:
    def __init__(
        self,
        days_of_week: Optional[List[str]] = None,
        time_blocked: Optional[List[str]] = None,
        tasks: Optional[List[Task]] = None,
    ):
        self.days_of_week = days_of_week or []
        self.time_blocked = time_blocked or []
        self.tasks = tasks or []

    def add_availability(self, day: str, time: str) -> None:
        pass

    def add_times(self, times: List[str]) -> None:
        pass

    def add_tasks(self, task: Task) -> None:
        pass
