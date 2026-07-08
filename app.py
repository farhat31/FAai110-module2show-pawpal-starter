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

status_filter = st.radio("Show", ["all", "incomplete", "complete"], horizontal=True)
tasks_to_show = scheduler.filter_tasks(pet=pet, status=status_filter)

if tasks_to_show:
    st.write("Current tasks:")
    st.table(
        [
            {
                "title": task.description,
                "duration_minutes": task.duration_minutes,
                "priority": task.priority,
                "recurs": task.frequency,
                "time": task.scheduled_time or "-",
                "complete": task.is_complete,
            }
            for task in scheduler.sort_tasks_by_time(tasks_to_show)
        ]
    )
    conflicts = scheduler.find_conflicts(pet.tasks)
    for task_a, task_b in conflicts:
        st.warning(
            f"Time conflict: '{task_a.description}' ({task_a.scheduled_time}) overlaps "
            f"'{task_b.description}' ({task_b.scheduled_time})"
        )
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
        st.write("### Today's Schedule")
        for line in scheduler.explain_plan(plan):
            st.write(f"- {line}")
        total_planned = sum(task.duration_minutes for task in plan)
        st.caption(f"Total planned time: {total_planned} min")
    else:
        st.warning("No tasks fit in the available time. Add tasks or increase available minutes.")
