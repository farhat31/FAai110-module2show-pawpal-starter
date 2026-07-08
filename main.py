from pawpal_system import Owner, Pet, Scheduler, Task


def main() -> None:
    mochi = Pet(name="Mochi", type="dog", age=3, breed="Shiba Inu")
    whiskers = Pet(name="Whiskers", type="cat", age=5, breed="Tabby")

    # Added out of order and with mixed times/priorities/status on purpose,
    # to exercise sorting and filtering rather than relying on insertion order.
    mochi.add_task(Task(description="Evening walk", duration_minutes=25, priority="medium", scheduled_time="18:00"))
    mochi.add_task(Task(description="Feeding", duration_minutes=10, priority="high", scheduled_time="07:00"))
    mochi.add_task(Task(description="Morning walk", duration_minutes=30, priority="high", scheduled_time="08:00"))
    # Same-pet conflict: overlaps Mochi's 07:00 Feeding.
    mochi.add_task(Task(description="Medication", duration_minutes=5, priority="high", scheduled_time="07:00"))
    whiskers.add_task(Task(description="Litter box cleaning", duration_minutes=15, priority="medium"))
    whiskers.add_task(Task(description="Playtime", duration_minutes=20, priority="low"))
    # Cross-pet conflict: overlaps Mochi's 08:00 Morning walk.
    whiskers.add_task(Task(description="Vet checkup", duration_minutes=30, priority="high", scheduled_time="08:00"))

    owner = Owner(name="Jordan", pets=[mochi, whiskers])
    scheduler = Scheduler(owner)

    whiskers.tasks[0].mark_complete()

    print("Sorted by time:")
    for task in scheduler.sort_tasks_by_time():
        print(f"- {task.scheduled_time or '--:--'}  {task.description} ({task.pet.name})")

    print("\nIncomplete tasks only:")
    for task in scheduler.filter_tasks(status="incomplete"):
        print(f"- {task.description} ({task.pet.name})")

    print("\nTasks for Mochi by name:")
    for task in scheduler.filter_tasks(pet="Mochi"):
        print(f"- {task.description}")

    print("\nConflicts:")
    warnings = scheduler.get_conflict_warnings()
    if warnings:
        for warning in warnings:
            print(f"- {warning}")
    else:
        print("- none")

    available_minutes = 60
    plan = scheduler.build_daily_plan(available_minutes)

    print(f"\nToday's Schedule for {owner.name} ({available_minutes} min available)")
    print("-" * 50)
    for line in scheduler.explain_plan(plan):
        print(f"- {line}")

    total_planned = sum(task.duration_minutes for task in plan)
    print("-" * 50)
    print(f"Total planned time: {total_planned} min")


if __name__ == "__main__":
    main()
