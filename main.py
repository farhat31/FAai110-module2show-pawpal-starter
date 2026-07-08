from pawpal_system import Owner, Pet, Scheduler, Task


def main() -> None:
    mochi = Pet(name="Mochi", type="dog", age=3, breed="Shiba Inu")
    whiskers = Pet(name="Whiskers", type="cat", age=5, breed="Tabby")

    mochi.add_task(Task(description="Morning walk", duration_minutes=30, priority="high"))
    mochi.add_task(Task(description="Feeding", duration_minutes=10, priority="high"))
    whiskers.add_task(Task(description="Litter box cleaning", duration_minutes=15, priority="medium"))
    whiskers.add_task(Task(description="Playtime", duration_minutes=20, priority="low"))

    owner = Owner(name="Jordan", pets=[mochi, whiskers])
    scheduler = Scheduler(owner)

    available_minutes = 60
    plan = scheduler.build_daily_plan(available_minutes)

    print(f"Today's Schedule for {owner.name} ({available_minutes} min available)")
    print("-" * 50)
    for line in scheduler.explain_plan(plan):
        print(f"- {line}")

    total_planned = sum(task.duration_minutes for task in plan)
    print("-" * 50)
    print(f"Total planned time: {total_planned} min")


if __name__ == "__main__":
    main()
