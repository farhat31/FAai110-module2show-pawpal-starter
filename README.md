# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```
# e.g.:
# Daily plan for Biscuit (Golden Retriever):
#   08:00 — Morning walk (30 min) [priority: high]
#   09:00 — Feeding (10 min) [priority: high]
#   ...
```
Today's Schedule for Jordan (60 min available)
--------------------------------------------------
- Feeding for Mochi (10 min, priority: high)
- Morning walk for Mochi (30 min, priority: high)
- Litter box cleaning for Whiskers (15 min, priority: medium)
--------------------------------------------------
Total planned time: 55 min

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

python -m pytest
My test includes checking sorting, recurrence of tasks, finding conflicts and more. 

## Paste your pytest output here

<!-- ============================= test session starts ==============================
platform darwin -- Python 3.9.12, pytest-7.1.1, pluggy-1.0.0
rootdir: /Users/farhatahamed/Documents/CodePathAI110/FAai110-module2show-pawpal-starter
plugins: anyio-3.5.0
collected 8 items                                                              

tests/test_pawpal.py ........                                            [100%]

============================== 8 passed in 0.01s ===============================
``` -->

## ✨ Features

- **Sorting by time** — `Scheduler.sort_tasks_by_time()` orders tasks chronologically by `scheduled_time` ("HH:MM"), pushing untimed tasks to the end.
- **Sorting by urgency** — `Scheduler.sort_tasks()` ranks tasks by a computed `priority_score()`: priority tier (high/medium/low), aged up the longer a task sits overdue, and boosted further if it matches one of the owner's preferences.
- **Filtering** — `Scheduler.filter_tasks(pet, status)` narrows tasks by pet (instance or name) and status (`all` / `incomplete` / `complete`); `Scheduler.get_pending_tasks()` further restricts to tasks that are actually due today.
- **Conflict warnings** — `Task.overlaps()` / `Task.time_range()` detect overlapping time windows (even across different pets); `Scheduler.find_conflicts()` returns the clashing pairs and `Scheduler.get_conflict_warnings()` turns them into printable warning strings.
- **Daily recurrence** — `Task.mark_complete()` marks a task done and, based on its `frequency` (`daily`/`weekly`), calls `Task.spawn_next_occurrence()` to create the next instance due one interval later.
- **Fair daily planning** — `Scheduler.build_daily_plan()` round-robins across every pet's urgency-sorted queue so one pet's high-priority tasks can't crowd out another's; splittable tasks can be trimmed down to `min_duration_minutes` to use up leftover time.
- **Optimal daily planning** — `Scheduler.build_optimal_plan()` runs a 0/1 knapsack over all pending tasks to maximize total priority-weighted value packed into the available minutes.
- **Plan explanations** — `Scheduler.explain_plan()` produces a human-readable reason string per scheduled task, flagging any that still overlap another.

## 📐 Smarter Scheduling

| Task sorting | Scheduler.sort_tasks(), Scheduler.sort_tasks_by_time() | e.g., by priority, duration |
| Filtering | Scheduler.filter_tasks(pet, status), Scheduler.get_pending_tasks(pet, today) | e.g., skip tasks if time runs out |
| Conflict handling | Task.overlaps(), Task.time_range(), Scheduler.find_conflicts(), Scheduler.get_conflict_warnings() | e.g., overlapping time slots |
| Recurring tasks | Task.mark_complete(), Task.spawn_next_occurrence(), Task.frequency/due_date | e.g., daily vs. weekly |
| Fair daily planning | Scheduler.build_daily_plan()| Round-robins across pets by urgency so one pet's high-priority tasks can't crowd out another's|
| Optimal daily planning | Scheduler.build_optimal_plan() | maximizes total priority-weighted value packed into the available minutes| 

## 📸 Demo Walkthrough

### UI features

The Streamlit app (`app.py`) lets a user:

- Enter an **owner name**, **pet name**, and **species**.
- **Add tasks** to that pet with a description, duration (minutes), priority (low/medium/high), recurrence (once/daily/weekly), and an optional scheduled time.
- **Filter** the task list by status (all / incomplete / complete).
- **Sort** the task list by time or by urgency, with each task's computed urgency score shown alongside it.
- See **conflict warnings** highlighted automatically whenever two scheduled tasks overlap (or a success message when there are none).
- Set the **available minutes** for the day and choose between two scheduling strategies — a fair round-robin plan across pets, or an optimal (priority-value-maximizing) plan — then **generate a schedule**.
- View the generated schedule as a table, expand a "Why this plan?" section for the reasoning behind each task's placement, and see any conflicts still present in the final plan.

### Example workflow

1. Enter owner "Jordan" and add a pet, "Mochi" (dog).
2. Add a task: "Morning walk", 20 min, high priority, recurs daily, scheduled at 08:00.
3. Add a second task: "Vet checkup", 30 min, high priority, scheduled at 08:00 — the app immediately flags this as a **conflict** with the morning walk.
4. Switch "Sort by" to `urgency` to see which task the scheduler considers more pressing.
5. Set "Available minutes today" to 60 and click **Generate schedule** to see the fair daily plan, its total planned time, and the reasoning behind each pick.
6. Mark the walk complete (via the backend); because it recurs daily, a new occurrence is automatically spawned for tomorrow.

### Key Scheduler behaviors shown

- **Sorting** — toggling "Sort by" between `time` (`sort_tasks_by_time`) and `urgency` (`sort_tasks`) visibly reorders the task table.
- **Conflict warnings** — overlapping scheduled times surface as `st.warning` messages (or `st.success` when the schedule is clear), both in the raw task list and in the final generated plan.
- **Daily recurrence** — completing a `daily`/`weekly` task spawns its next occurrence, due one interval later, instead of disappearing for good.
- **Fair vs. optimal planning** — the same set of tasks produces a different schedule depending on whether "Optimize total priority value" is checked.

### Sample CLI output (`python main.py`)

```
Sorted by time:
- 07:00  Feeding (Mochi)
- 07:00  Medication (Mochi)
- 08:00  Morning walk (Mochi)
- 08:00  Vet checkup (Whiskers)
- 18:00  Evening walk (Mochi)
- --:--  Playtime (Whiskers)

Incomplete tasks only:
- Evening walk (Mochi)
- Feeding (Mochi)
- Morning walk (Mochi)
- Medication (Mochi)
- Playtime (Whiskers)
- Vet checkup (Whiskers)
- Litter box cleaning (Whiskers)

Tasks for Mochi by name:
- Evening walk
- Feeding
- Morning walk
- Medication

Conflicts:
- Warning: 'Feeding' (Mochi at 07:00) conflicts with 'Medication' (Mochi at 07:00)
- Warning: 'Morning walk' (Mochi at 08:00) conflicts with 'Vet checkup' (Whiskers at 08:00)

Today's Schedule for Jordan (60 min available)
--------------------------------------------------
- Medication for Mochi at 07:00 (5 min, priority: high) [conflict: overlaps another scheduled task]
- Vet checkup for Whiskers at 08:00 (30 min, priority: high)
- Feeding for Mochi at 07:00 (10 min, priority: high) [conflict: overlaps another scheduled task]
--------------------------------------------------
Total planned time: 45 min
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
