
import streamlit as st
from supabase import create_client
from datetime import date, datetime

st.set_page_config(
    page_title="My Study & Group Hub",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Mobile-friendly styling
st.markdown("""
<style>
.block-container {
    padding-top: 1.5rem;
    padding-bottom: 3rem;
    max-width: 1100px;
}
.stButton button {
    min-height: 44px;
    border-radius: 10px;
}
[data-testid="stMetric"] {
    padding: 12px;
    border: 1px solid rgba(128,128,128,0.25);
    border-radius: 12px;
}
@media (max-width: 768px) {
    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }
}
</style>
""", unsafe_allow_html=True)


# Connect to Supabase using Streamlit secrets
@st.cache_resource
def connect_supabase():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)


st.title("📚 My Study & Group Hub")
st.caption("Your MBA assignments, deadlines, and group activities — all in one place.")

try:
    supabase = connect_supabase()
except Exception:
    st.error(
        "Supabase connection settings are missing or invalid. "
        "Check your Streamlit secrets and try again."
    )
    st.stop()


STATUS_OPTIONS = [
    "Not Started",
    "In Progress",
    "Waiting on Group",
    "Completed",
]

TYPE_OPTIONS = [
    "Individual Assignment",
    "Group Assignment",
    "Presentation",
    "Case Study",
    "Exam",
    "Reading",
    "Other",
]


def load_assignments():
    result = (
        supabase.table("assignments")
        .select("*")
        .order("due_date", desc=False)
        .execute()
    )
    return result.data or []


def days_remaining(due_date):
    if not due_date:
        return None
    try:
        due = date.fromisoformat(str(due_date)[:10])
        return (due - date.today()).days
    except (ValueError, TypeError):
        return None


def deadline_label(due_date):
    days = days_remaining(due_date)
    if days is None:
        return "No due date"
    if days < 0:
        return f"Overdue by {abs(days)} day(s)"
    if days == 0:
        return "Due today"
    if days == 1:
        return "Due tomorrow"
    return f"{days} days left"


def show_error(action, error):
    st.error(f"Could not {action}. Please try again.")
    st.caption(str(error))


# Load saved records
try:
    assignments = load_assignments()
except Exception as error:
    st.error("Couldn't load assignments from Supabase.")
    st.info(
        "Check that your assignments table exists and that your "
        "Supabase API key and database policies are configured."
    )
    st.caption(str(error))
    st.stop()


# Dashboard metrics
today = date.today()
overdue = [
    a for a in assignments
    if days_remaining(a.get("due_date")) is not None
    and days_remaining(a.get("due_date")) < 0
    and a.get("status") != "Completed"
]
upcoming = [
    a for a in assignments
    if days_remaining(a.get("due_date")) is not None
    and 0 <= days_remaining(a.get("due_date")) <= 7
    and a.get("status") != "Completed"
]
completed = [
    a for a in assignments if a.get("status") == "Completed"
]

m1, m2, m3, m4 = st.columns(4)
m1.metric("📋 Total", len(assignments))
m2.metric("⏰ Due in 7 days", len(upcoming))
m3.metric("⚠️ Overdue", len(overdue))
m4.metric("✅ Completed", len(completed))

st.divider()

page = st.selectbox(
    "📍 Where would you like to go?",
    [
        "Dashboard & Assignments",
        "Add Assignment",
        "Manage Assignments",
    ],
    key="page_navigation",
)


if page == "Add Assignment":
    st.subheader("➕ Add an assignment or activity")

    with st.form("add_assignment_form", clear_on_submit=True):
        course = st.text_input(
            "Course *",
            placeholder="e.g. Strategy, Finance, Marketing",
        )

        col1, col2 = st.columns(2)

        with col1:
            assignment_type = st.selectbox("Type", TYPE_OPTIONS)
            status = st.selectbox("Status", STATUS_OPTIONS)
            due_date = st.date_input(
                "Due date (optional)",
                value=None,
            )

        with col2:
            group_name = st.text_input(
                "Group name",
                placeholder="e.g. Group 3",
            )
            group_members = st.text_input(
                "Group members",
                placeholder="Names separated by commas",
            )
            remark = st.text_input(
                "Remark",
                placeholder="e.g. Waiting for professor feedback",
            )

        notes = st.text_area(
            "Notes",
            placeholder="Instructions, action items, meeting notes...",
        )

        submitted = st.form_submit_button(
            "💾 Save Assignment",
            type="primary",
            use_container_width=True,
        )

        if submitted:
            if not course.strip():
                st.warning("Please enter a course name.")
            else:
                record = {
                    "course": course.strip(),
                    "type": assignment_type,
                    "status": status,
                    "due_date": (
                        due_date.isoformat() if due_date else None
                    ),
                    "group_name": group_name.strip() or None,
                    "group_members": group_members.strip() or None,
                    "remark": remark.strip() or None,
                    "notes": notes.strip() or None,
                }

                try:
                    supabase.table("assignments").insert(record).execute()
                    st.success("Assignment saved successfully!")
                    st.rerun()
                except Exception as error:
                    show_error("save the assignment", error)


elif page == "Manage Assignments":
    st.subheader("✏️ Manage assignments")

    if not assignments:
        st.info("No assignments yet. Add your first assignment!")
    else:
        chosen = st.selectbox(
            "Select an assignment",
            assignments,
            format_func=lambda a: (
                f"{a.get('course', 'Untitled')} — "
                f"{a.get('type', 'Other')} "
                f"({deadline_label(a.get('due_date'))})"
            ),
            key="manage_assignment",
        )

        if chosen:
            with st.form("edit_assignment_form"):
                st.write(f"**Editing:** {chosen.get('course', '')}")

                course = st.text_input(
                    "Course",
                    value=chosen.get("course") or "",
                )

                col1, col2 = st.columns(2)

                with col1:
                    current_type = chosen.get("type")
                    type_index = (
                        TYPE_OPTIONS.index(current_type)
                        if current_type in TYPE_OPTIONS else 0
                    )
                    assignment_type = st.selectbox(
                        "Type",
                        TYPE_OPTIONS,
                        index=type_index,
                    )

                    current_status = chosen.get("status")
                    status_index = (
                        STATUS_OPTIONS.index(current_status)
                        if current_status in STATUS_OPTIONS else 0
                    )
                    status = st.selectbox(
                        "Status",
                        STATUS_OPTIONS,
                        index=status_index,
                    )

                    saved_due = chosen.get("due_date")
                    try:
                        parsed_due = (
                            date.fromisoformat(str(saved_due)[:10])
                            if saved_due else None
                        )
                    except ValueError:
                        parsed_due = None

                    due_date = st.date_input(
                        "Due date",
                        value=parsed_due,
                    )

                with col2:
                    group_name = st.text_input(
                        "Group name",
                        value=chosen.get("group_name") or "",
                    )
                    group_members = st.text_input(
                        "Group members",
                        value=chosen.get("group_members") or "",
                    )
                    remark = st.text_input(
                        "Remark",
                        value=chosen.get("remark") or "",
                    )

                notes = st.text_area(
                    "Notes",
                    value=chosen.get("notes") or "",
                )

                save_changes = st.form_submit_button(
                    "💾 Save Changes",
                    type="primary",
                    use_container_width=True,
                )

                if save_changes:
                    if not course.strip():
                        st.warning("Course cannot be empty.")
                    else:
                        updates = {
                            "course": course.strip(),
                            "type": assignment_type,
                            "status": status,
                            "due_date": (
                                due_date.isoformat() if due_date else None
                            ),
                            "group_name": group_name.strip() or None,
                            "group_members": group_members.strip() or None,
                            "remark": remark.strip() or None,
                            "notes": notes.strip() or None,
                            "updated_at": datetime.now().astimezone().isoformat(),
                        }
                        try:
                            supabase.table("assignments").update(
                                updates
                            ).eq("id", chosen["id"]).execute()
                            st.success("Changes saved!")
                            st.rerun()
                        except Exception as error:
                            show_error("update the assignment", error)

            st.divider()
            st.markdown("**Delete this assignment**")
            confirm_delete = st.checkbox(
                "I confirm I want to permanently delete this assignment.",
                key=f"confirm_delete_{chosen['id']}",
            )

            if st.button(
                "🗑️ Delete Assignment",
                disabled=not confirm_delete,
                key=f"delete_{chosen['id']}",
            ):
                try:
                    supabase.table("assignments").delete().eq(
                        "id", chosen["id"]
                    ).execute()
                    st.success("Assignment deleted.")
                    st.rerun()
                except Exception as error:
                    show_error("delete the assignment", error)


else:
    st.subheader("🗓️ Your assignments")

    search = st.text_input(
        "🔎 Search",
        placeholder="Search course, group, or assignment type...",
    )

    status_filter = st.selectbox(
        "Filter by status",
        ["All statuses"] + STATUS_OPTIONS,
    )

    filtered = assignments.copy()

    if status_filter != "All statuses":
        filtered = [
            a for a in filtered if a.get("status") == status_filter
        ]

    if search.strip():
        term = search.strip().lower()
        filtered = [
            a for a in filtered
            if term in str(a.get("course") or "").lower()
            or term in str(a.get("group_name") or "").lower()
            or term in str(a.get("type") or "").lower()
            or term in str(a.get("group_members") or "").lower()
        ]

    if not filtered:
        st.info("No matching assignments found. Try another filter or add one.")
    else:
        for assignment in filtered:
            with st.container(border=True):
                title_col, status_col = st.columns([3, 1])

                with title_col:
                    st.markdown(
                        f"### {assignment.get('course', 'Untitled')}"
                    )
                    st.caption(assignment.get("type", "Other"))

                with status_col:
                    st.write(assignment.get("status", "Not Started"))

                due = assignment.get("due_date")
                st.write(f"**📅 Deadline:** {due or 'Not set'}")

                days = days_remaining(due)
                if days is not None and assignment.get("status") != "Completed":
                    if days < 0:
                        st.warning(deadline_label(due))
                    elif days <= 3:
                        st.warning(deadline_label(due))
                    else:
                        st.caption(deadline_label(due))

                if assignment.get("group_name"):
                    st.write(f"**👥 Group:** {assignment['group_name']}")

                if assignment.get("group_members"):
                    st.write(f"**Members:** {assignment['group_members']}")

                if assignment.get("remark"):
                    st.write(f"**Remark:** {assignment['remark']}")

                if assignment.get("notes"):
                    with st.expander("📝 View notes"):
                        st.write(assignment["notes"])

    st.divider()
    st.caption(
        "Your assignments are stored in Supabase. "
        "Use Manage Assignments to edit or delete a record."
    )

