import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pawpal_system import Pet, Task


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
