import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Quick Demo Inputs (UI only)")
owner_name = st.text_input("Owner name", value="Jordan")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

if "owner" not in st.session_state:
    st.session_state.owner = Owner(name=owner_name)
owner = st.session_state.owner
owner.name = owner_name

if "pet" not in st.session_state:
    pet = Pet(name=pet_name, type=species, age=0, breed="Unknown")
    owner.add_pet(pet)
    st.session_state.pet = pet
pet = st.session_state.pet
pet.name = pet_name
pet.type = species

scheduler = Scheduler(owner)

st.markdown("### Tasks")
st.caption("Add a few tasks and they'll feed into the scheduler below.")

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

col4, col5 = st.columns(2)
with col4:
    frequency = st.selectbox("Recurs", ["once", "daily", "weekly"], index=1)
with col5:
    set_time = st.checkbox("Set a specific time")
    scheduled_time = None
    if set_time:
        scheduled_time = st.time_input("Scheduled time").strftime("%H:%M")

if st.button("Add task"):
    pet.add_task(
        Task(
            description=task_title,
            duration_minutes=int(duration),
            priority=priority,
            frequency=frequency,
            scheduled_time=scheduled_time,
        )
    )

col_filter, col_sort = st.columns(2)
with col_filter:
    status_filter = st.radio("Show", ["all", "incomplete", "complete"], horizontal=True)
with col_sort:
    sort_mode = st.radio("Sort by", ["time", "urgency"], horizontal=True)

tasks_to_show = scheduler.filter_tasks(pet=pet, status=status_filter)

if tasks_to_show:
    sorted_tasks = (
        scheduler.sort_tasks_by_time(tasks_to_show)
        if sort_mode == "time"
        else scheduler.sort_tasks(tasks_to_show)
    )
    st.write("Current tasks:")
    st.table(
        [
            {
                "title": task.description,
                "duration_minutes": task.duration_minutes,
                "priority": task.priority,
                "urgency_score": scheduler.priority_score(task),
                "recurs": task.frequency,
                "time": task.scheduled_time or "-",
                "complete": task.is_complete,
            }
            for task in sorted_tasks
        ]
    )

    conflict_warnings = scheduler.get_conflict_warnings(pet.tasks)
    if conflict_warnings:
        for warning in conflict_warnings:
            st.warning(warning)
    else:
        st.success("No time conflicts ✅")
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")

available_minutes = st.number_input(
    "Available minutes today", min_value=0, max_value=600, value=120
)
optimize_value = st.checkbox(
    "Optimize total priority value instead of splitting time fairly across pets"
)

if st.button("Generate schedule"):
    plan = (
        scheduler.build_optimal_plan(int(available_minutes))
        if optimize_value
        else scheduler.build_daily_plan(int(available_minutes))
    )

    if plan:
        total_planned = sum(task.duration_minutes for task in plan)
        st.success(f"Schedule built: {len(plan)} task(s), {total_planned} min planned.")

        st.table(
            [
                {
                    "pet": task.pet.name if task.pet else "-",
                    "title": task.description,
                    "time": task.scheduled_time or "-",
                    "duration_minutes": task.duration_minutes,
                    "priority": task.priority,
                }
                for task in plan
            ]
        )

        with st.expander("Why this plan?"):
            for line in scheduler.explain_plan(plan):
                st.write(f"- {line}")

        plan_conflicts = scheduler.get_conflict_warnings(plan)
        for warning in plan_conflicts:
            st.warning(warning)
    else:
        st.warning("No tasks fit in the available time. Add tasks or increase available minutes.")
