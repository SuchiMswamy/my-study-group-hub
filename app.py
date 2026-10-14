
import streamlit as st
import streamlit.components.v1 as components
from supabase import create_client
from datetime import date, datetime
import pandas as pd
import random
import html

st.set_page_config(
    page_title="My Study Planner",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# =========================================================
# THEMES: 5 LIGHT + 5 DARK
# =========================================================
THEMES = {
    "Sky Blue": {
        "bg": "#F3F8FF", "card": "#FFFFFF", "text": "#203C68",
        "muted": "#647A9C", "primary": "#4B91F1", "soft": "#DFEDFF",
        "border": "#D8E6FA", "accent": "#B8D9FF",
    },
    "Lavender": {
        "bg": "#F8F5FF", "card": "#FFFFFF", "text": "#40345F",
        "muted": "#81739D", "primary": "#9175E8", "soft": "#EAE2FF",
        "border": "#E3D9FA", "accent": "#D4C6FF",
    },
    "Mint": {
        "bg": "#F1FAF5", "card": "#FFFFFF", "text": "#245343",
        "muted": "#688B7D", "primary": "#38A77C", "soft": "#DDF5E9",
        "border": "#CDEBDD", "accent": "#B5E8D0",
    },
    "Peach": {
        "bg": "#FFF7F1", "card": "#FFFFFF", "text": "#704534",
        "muted": "#A17D6B", "primary": "#E99568", "soft": "#FFE7D9",
        "border": "#F5DDCE", "accent": "#FFD0B4",
    },
    "Ocean Blue": {
        "bg": "#EDF8FC", "card": "#FFFFFF", "text": "#123C59",
        "muted": "#587D96", "primary": "#1687B5", "soft": "#D5F0FA",
        "border": "#C6E7F3", "accent": "#9AD9EF",
    },
    "Dark Sky Blue": {
        "bg": "#101827", "card": "#1B2638", "text": "#E5EEFF",
        "muted": "#A1B2CE", "primary": "#70A9FF", "soft": "#263B59",
        "border": "#35445C", "accent": "#8CC5FF",
    },
    "Dark Lavender": {
        "bg": "#191426", "card": "#251D35", "text": "#F0E8FF",
        "muted": "#B9A9D4", "primary": "#B49AFF", "soft": "#38294F",
        "border": "#4B3A64", "accent": "#D1BFFF",
    },
    "Dark Mint": {
        "bg": "#101F1B", "card": "#1B3029", "text": "#E1F8EB",
        "muted": "#A2C7B4", "primary": "#62D3A3", "soft": "#25493A",
        "border": "#355C4A", "accent": "#9CEBC4",
    },
    "Dark Peach": {
        "bg": "#251914", "card": "#35251F", "text": "#FFE9DE",
        "muted": "#D1AA98", "primary": "#FFAB80", "soft": "#50352A",
        "border": "#694638", "accent": "#FFC5A7",
    },
    "Dark Ocean Blue": {
        "bg": "#0D1D2A", "card": "#162C3C", "text": "#E0F5FF",
        "muted": "#9DBDCE", "primary": "#42B9E8", "soft": "#1D3D52",
        "border": "#2B5269", "accent": "#83DEFF",
    },
}

if "theme" not in st.session_state:
    st.session_state.theme = "Sky Blue"

if "focus_end" not in st.session_state:
    st.session_state.focus_end = None

if "focus_task" not in st.session_state:
    st.session_state.focus_task = ""

# =========================================================
# HEADER
# =========================================================
header_left, header_right = st.columns([4, 1.5])

with header_left:
    st.markdown("## 📚 My Study Planner")
    st.caption(
        "Plan thoughtfully · Collaborate happily · Achieve your goals"
    )

with header_right:
    chosen_theme = st.selectbox(
        "🎨 Choose your theme",
        list(THEMES.keys()),
        index=list(THEMES.keys()).index(st.session_state.theme),
        key="theme_selector",
    )

    if chosen_theme != st.session_state.theme:
        st.session_state.theme = chosen_theme
        st.rerun()

theme = THEMES[st.session_state.theme]

# =========================================================
# STYLING AND ANIMATIONS
# =========================================================
st.markdown(
    f"""
    <style>
    :root {{
        --app-bg: {theme["bg"]};
        --app-card: {theme["card"]};
        --app-text: {theme["text"]};
        --app-muted: {theme["muted"]};
        --app-primary: {theme["primary"]};
        --app-soft: {theme["soft"]};
        --app-border: {theme["border"]};
        --app-accent: {theme["accent"]};
    }}

    .stApp {{
        background: var(--app-bg);
        color: var(--app-text);
        transition: background .35s ease;
    }}

    [data-testid="stHeader"] {{
        background: transparent;
    }}

    .block-container {{
        max-width: 1200px;
        padding-top: 1.5rem;
        padding-bottom: 3rem;
    }}

    h1, h2, h3, h4, p, label, .stMarkdown {{
        color: var(--app-text);
    }}

    [data-testid="stMetric"] {{
        background: var(--app-card);
        border: 1px solid var(--app-border);
        border-radius: 18px;
        padding: 16px 18px;
        box-shadow: 0 4px 15px rgba(55,90,130,.06);
        transition: transform .2s ease, box-shadow .2s ease;
    }}

    [data-testid="stMetric"]:hover {{
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(55,90,130,.12);
    }}

    [data-testid="stMetricLabel"] {{
        color: var(--app-muted) !important;
    }}

    [data-testid="stMetricValue"] {{
        color: var(--app-text) !important;
    }}

    .stButton > button, .stDownloadButton > button {{
        min-height: 43px;
        border-radius: 12px;
        border: 1px solid var(--app-border);
        transition: transform .18s ease, box-shadow .18s ease;
    }}

    .stButton > button:hover, .stDownloadButton > button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 5px 14px rgba(55,90,130,.12);
        border-color: var(--app-primary);
    }}

    div[data-testid="stForm"],
    div[data-testid="stExpander"] {{
        background: var(--app-card);
        border: 1px solid var(--app-border);
        border-radius: 18px;
    }}

    .hero {{
        background: linear-gradient(
            120deg, var(--app-soft), var(--app-card) 78%
        );
        border: 1px solid var(--app-border);
        border-radius: 24px;
        padding: 24px;
        margin-bottom: 20px;
        animation: fadeUp .65s ease both;
    }}

    .hero-row {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 18px;
    }}

    .hero h1 {{
        font-size: clamp(1.7rem, 4vw, 2.45rem);
        margin: 0 0 8px;
    }}

    .hero p {{
        color: var(--app-muted);
        margin: 0;
    }}

    .mascot {{
        font-size: 4rem;
        line-height: 1.1;
        display: inline-block;
        animation: buddyFloat 2.5s ease-in-out infinite;
        transform-origin: bottom center;
    }}

    .mascot.happy {{
        animation: happyBounce 1.5s ease-in-out infinite;
    }}

    .mascot.sad {{
        animation: gentleSway 3s ease-in-out infinite;
    }}

    .mascot-bubble {{
        background: var(--app-card);
        color: var(--app-text);
        border: 1px solid var(--app-border);
        border-radius: 16px;
        padding: 12px 15px;
        margin-top: 10px;
        font-weight: 600;
        max-width: 250px;
        box-shadow: 0 5px 18px rgba(55,90,130,.07);
    }}

    .section-card {{
        background: var(--app-card);
        border: 1px solid var(--app-border);
        border-radius: 18px;
        padding: 18px;
        margin-bottom: 12px;
        animation: fadeUp .5s ease both;
    }}

    .progress-track {{
        height: 10px;
        background: var(--app-soft);
        border-radius: 99px;
        overflow: hidden;
        margin-top: 9px;
    }}

    .progress-fill {{
        height: 100%;
        background: linear-gradient(
            90deg, var(--app-primary), var(--app-accent)
        );
        border-radius: 99px;
        transition: width .8s ease;
    }}

    .stTextInput input,
    .stTextArea textarea,
    .stNumberInput input,
    [data-baseweb="select"] > div {{
        background-color: var(--app-card);
        color: var(--app-text);
        border-color: var(--app-border);
    }}

    .small-muted {{
        color: var(--app-muted);
        font-size: .9rem;
    }}

    @keyframes buddyFloat {{
        0%, 100% {{ transform: translateY(0) rotate(-2deg); }}
        50% {{ transform: translateY(-9px) rotate(2deg); }}
    }}

    @keyframes happyBounce {{
        0%, 100% {{ transform: translateY(0) scale(1); }}
        50% {{ transform: translateY(-12px) scale(1.06); }}
    }}

    @keyframes gentleSway {{
        0%, 100% {{ transform: translateY(0) rotate(-3deg); }}
        50% {{ transform: translateY(-3px) rotate(3deg); }}
    }}

    @keyframes fadeUp {{
        from {{ opacity: 0; transform: translateY(12px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}

    @media (max-width: 768px) {{
        .block-container {{ padding: 1rem .8rem 2rem; }}
        .hero {{ padding: 17px; border-radius: 18px; }}
        .hero-row {{ align-items: flex-start; }}
        .mascot {{ font-size: 3rem; }}
        .mascot-bubble {{ font-size: .85rem; padding: 9px; }}
    }}

    @media (prefers-reduced-motion: reduce) {{
        .mascot, .hero, .section-card {{ animation: none !important; }}
        * {{ transition: none !important; }}
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================================================
# SUPABASE CONNECTION
# =========================================================
@st.cache_resource
def connect_supabase():
    url = st.secrets["SUPABASE_URL"].strip().rstrip("/")
    url = url.removesuffix("/rest/v1")
    key = st.secrets["SUPABASE_KEY"].strip()
    return create_client(url, key)


def show_error(action, error):
    st.error(f"Couldn't {action}. Please try again.")
    st.caption(str(error))


try:
    supabase = connect_supabase()
except Exception:
    st.error(
        "Supabase connection settings are missing or invalid. "
        "Check SUPABASE_URL and SUPABASE_KEY in Streamlit Secrets."
    )
    st.stop()

# =========================================================
# DATA HELPERS
# =========================================================
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

PRIORITY_OPTIONS = ["Low", "Medium", "High", "Urgent"]


def load_assignments():
    result = (
        supabase.table("assignments")
        .select("*")
        .order("due_date", desc=False)
        .execute()
    )
    return result.data or []


@st.cache_data(ttl=30)
def cached_load_assignments(_cache_key):
    return load_assignments()


def refresh_data():
    cached_load_assignments.clear()


def days_remaining(due_date):
    if not due_date:
        return None
    try:
        return (
            date.fromisoformat(str(due_date)[:10]) - date.today()
        ).days
    except (ValueError, TypeError):
        return None


def deadline_label(due_date):
    days = days_remaining(due_date)
    if days is None:
        return "No due date"
    if days < 0:
        return f"Overdue by {abs(days)} day(s)"
    if days == 0:
        return "Due today!"
    if days == 1:
        return "Due tomorrow"
    return f"{days} days left"


def priority_icon(priority):
    return {
        "Low": "🟢",
        "Medium": "🔵",
        "High": "🟠",
        "Urgent": "🔴",
    }.get(priority or "Medium", "🔵")


def safe_date(value):
    if not value:
        return None
    try:
        return date.fromisoformat(str(value)[:10])
    except (ValueError, TypeError):
        return None


try:
    assignments = cached_load_assignments("assignments")
except Exception as error:
    st.error("Couldn't load assignments from Supabase.")
    st.info(
        "Check that the assignments table exists and your API key "
        "and database policies are configured."
    )
    st.caption(str(error))
    st.stop()

# =========================================================
# METRICS AND MOTIVATIONAL STUDY BUDDY
# =========================================================
today = date.today()

incomplete = [
    a for a in assignments if a.get("status") != "Completed"
]
completed = [
    a for a in assignments if a.get("status") == "Completed"
]
overdue = [
    a for a in incomplete
    if days_remaining(a.get("due_date")) is not None
    and days_remaining(a.get("due_date")) < 0
]
due_soon = [
    a for a in incomplete
    if days_remaining(a.get("due_date")) is not None
    and 0 <= days_remaining(a.get("due_date")) <= 7
]

total = len(assignments)
completion_pct = round(len(completed) / total * 100) if total else 0

if overdue:
    buddy_face = "🥺"
    buddy_mood = "sad"
    buddy_message = (
        "It's okay, Suchi. Let's tackle one overdue task at a time. 💙"
    )
elif total > 0 and completion_pct == 100:
    buddy_face = "🥳"
    buddy_mood = "happy"
    buddy_message = (
        "You did it, Suchi! Everything is complete. Celebrate! 🎉"
    )
elif due_soon:
    buddy_face = "😮‍💨"
    buddy_mood = "sad"
    buddy_message = (
        "Deadlines are getting closer. Let's make a little plan together!"
    )
elif completed:
    buddy_face = "🤗"
    buddy_mood = "happy"
    buddy_message = random.choice([
        "Look at you go, Suchi! Every task is progress. ✨",
        "Your effort is adding up. Keep that momentum going!",
        "Proud of your progress! Remember to take breaks too. 💗",
    ])
else:
    buddy_face = "😊"
    buddy_mood = "happy"
    buddy_message = (
        "Hi Suchi! Every big achievement starts with one small step. 🌱"
    )

st.markdown(
    f"""
    <div class="hero">
      <div class="hero-row">
        <div>
          <h1>Hi Suchi! 👋</h1>
          <p>{today.strftime("%A, %d %B %Y")}</p>
          <p style="margin-top:8px">
            Your goals matter. Let's make today count.
          </p>
        </div>
        <div style="text-align:center;min-width:105px">
          <div class="mascot {buddy_mood}">{buddy_face}</div>
          <div class="mascot-bubble">
            {html.escape(buddy_message)}
          </div>
        </div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

m1, m2, m3, m4 = st.columns(4)
m1.metric("📚 Total tasks", total)
m2.metric("✅ Completed", len(completed))
m3.metric("⏰ Due in 7 days", len(due_soon))
m4.metric("🚨 Overdue", len(overdue))

st.markdown(
    f"""
    <div class="section-card">
      <div style="display:flex;justify-content:space-between;gap:12px">
        <strong>✨ Your overall progress</strong>
        <strong>{completion_pct}%</strong>
      </div>
      <div class="progress-track">
        <div class="progress-fill" style="width:{completion_pct}%"></div>
      </div>
      <p class="small-muted" style="margin-bottom:0;margin-top:8px">
        {len(completed)} of {total} assignments completed. Keep going!
      </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# =========================================================
# NAVIGATION
# =========================================================
page = st.selectbox(
    "📍 Where would you like to go?",
    [
        "🏡 Dashboard",
        "➕ Add Assignment",
        "📝 Manage Assignments",
        "🗓️ Deadline Planner",
        "⏳ Focus Timer",
        "👥 Group Hub",
        "📊 Analytics & Export",
    ],
    key="main_navigation",
)

# =========================================================
# ADD ASSIGNMENT
# =========================================================
if page == "➕ Add Assignment":
    st.subheader("➕ Add a new assignment")

    with st.form("add_assignment", clear_on_submit=True):
        course = st.text_input("Course *")

        c1, c2 = st.columns(2)
        with c1:
            assignment_type = st.selectbox("Assignment type", TYPE_OPTIONS)
            status = st.selectbox("Status", STATUS_OPTIONS)
            priority = st.select_slider(
                "Priority", options=PRIORITY_OPTIONS, value="Medium"
            )
            due_date = st.date_input(
                "Due date",
                value=None,
                help="Leave blank if no deadline has been set.",
            )

        with c2:
            category = st.text_input("Category / tag")
            group_name = st.text_input("Group name")
            group_members = st.text_input("Group members")
            estimated_hours = st.number_input(
                "Estimated study hours",
                min_value=0.0,
                max_value=500.0,
                value=2.0,
                step=0.5,
            )

        remark = st.text_input("Remark")
        notes = st.text_area("Notes / action items", height=120)

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
                    "priority": priority,
                    "category": category.strip() or None,
                    "due_date": due_date.isoformat() if due_date else None,
                    "group_name": group_name.strip() or None,
                    "group_members": group_members.strip() or None,
                    "estimated_hours": estimated_hours,
                    "remark": remark.strip() or None,
                    "notes": notes.strip() or None,
                }

                try:
                    supabase.table("assignments").insert(record).execute()
                    refresh_data()
                    st.success("Your assignment has been saved! 🌟")
                    st.toast("New goal added. You've got this! 🎯")
                    st.rerun()
                except Exception as error:
                    show_error("save the assignment", error)

# =========================================================
# MANAGE ASSIGNMENTS
# =========================================================
elif page == "📝 Manage Assignments":
    st.subheader("📝 Manage your assignments")

    if not assignments:
        st.info("No assignments yet. Add your first goal!")
    else:
        chosen = st.selectbox(
            "Choose an assignment",
            assignments,
            format_func=lambda a: (
                f"{a.get('course', 'Untitled')} · "
                f"{a.get('status', 'Not Started')} · "
                f"{deadline_label(a.get('due_date'))}"
            ),
            key="edit_choice",
        )

        if chosen:
            with st.form("edit_assignment"):
                st.markdown(f"### ✏️ {chosen.get('course', '')}")
                course = st.text_input(
                    "Course", value=chosen.get("course") or ""
                )

                c1, c2 = st.columns(2)
                with c1:
                    old_type = chosen.get("type")
                    assignment_type = st.selectbox(
                        "Type", TYPE_OPTIONS,
                        index=TYPE_OPTIONS.index(old_type)
                        if old_type in TYPE_OPTIONS else 0,
                    )

                    old_status = chosen.get("status")
                    status = st.selectbox(
                        "Status", STATUS_OPTIONS,
                        index=STATUS_OPTIONS.index(old_status)
                        if old_status in STATUS_OPTIONS else 0,
                    )

                    old_priority = chosen.get("priority") or "Medium"
                    priority = st.selectbox(
                        "Priority", PRIORITY_OPTIONS,
                        index=PRIORITY_OPTIONS.index(old_priority)
                        if old_priority in PRIORITY_OPTIONS else 1,
                    )

                    due_date = st.date_input(
                        "Due date", value=safe_date(chosen.get("due_date"))
                    )

                with c2:
                    category = st.text_input(
                        "Category / tag", value=chosen.get("category") or ""
                    )
                    group_name = st.text_input(
                        "Group name", value=chosen.get("group_name") or ""
                    )
                    group_members = st.text_input(
                        "Group members",
                        value=chosen.get("group_members") or "",
                    )
                    estimated_hours = st.number_input(
                        "Estimated study hours",
                        min_value=0.0,
                        max_value=500.0,
                        value=float(chosen.get("estimated_hours") or 1),
                        step=0.5,
                    )

                remark = st.text_input(
                    "Remark", value=chosen.get("remark") or ""
                )
                notes = st.text_area(
                    "Notes", value=chosen.get("notes") or "", height=120
                )

                save = st.form_submit_button(
                    "💾 Save Changes",
                    type="primary",
                    use_container_width=True,
                )

                if save:
                    if not course.strip():
                        st.warning("Course cannot be empty.")
                    else:
                        updates = {
                            "course": course.strip(),
                            "type": assignment_type,
                            "status": status,
                            "priority": priority,
                            "category": category.strip() or None,
                            "due_date": due_date.isoformat() if due_date else None,
                            "group_name": group_name.strip() or None,
                            "group_members": group_members.strip() or None,
                            "estimated_hours": estimated_hours,
                            "remark": remark.strip() or None,
                            "notes": notes.strip() or None,
                            "updated_at": datetime.now().astimezone().isoformat(),
                        }

                        try:
                            supabase.table("assignments").update(
                                updates
                            ).eq("id", chosen["id"]).execute()
                            refresh_data()

                            if status == "Completed":
                                st.balloons()
                                st.toast("Fantastic work! 🎉")
                            else:
                                st.success("Changes saved.")

                            st.rerun()
                        except Exception as error:
                            show_error("update the assignment", error)

            with st.expander("🗑️ Delete assignment"):
                st.warning("Deleting an assignment cannot be undone.")
                confirm = st.checkbox(
                    "I understand and want to delete this record.",
                    key=f"confirm_delete_{chosen['id']}",
                )

                if st.button(
                    "Delete permanently",
                    disabled=not confirm,
                    key=f"delete_btn_{chosen['id']}",
                ):
                    try:
                        supabase.table("assignments").delete().eq(
                            "id", chosen["id"]
                        ).execute()
                        refresh_data()
                        st.success("Assignment deleted.")
                        st.rerun()
                    except Exception as error:
                        show_error("delete the assignment", error)

# =========================================================
# DEADLINE PLANNER
# =========================================================
elif page == "🗓️ Deadline Planner":
    st.subheader("🗓️ Deadline Planner")
    st.caption("Plan ahead and avoid last-minute stress.")

    window = st.radio(
        "Show deadlines",
        ["Next 7 days", "Next 30 days", "All upcoming", "Overdue"],
        horizontal=True,
    )

    dated = [
        a for a in assignments
        if a.get("status") != "Completed" and a.get("due_date")
    ]

    if window == "Overdue":
        view = [
            a for a in dated
            if days_remaining(a["due_date"]) is not None
            and days_remaining(a["due_date"]) < 0
        ]
    elif window == "Next 7 days":
        view = [
            a for a in dated
            if days_remaining(a["due_date"]) is not None
            and 0 <= days_remaining(a["due_date"]) <= 7
        ]
    elif window == "Next 30 days":
        view = [
            a for a in dated
            if days_remaining(a["due_date"]) is not None
            and 0 <= days_remaining(a["due_date"]) <= 30
        ]
    else:
        view = [
            a for a in dated
            if days_remaining(a["due_date"]) is not None
            and days_remaining(a["due_date"]) >= 0
        ]

    view.sort(key=lambda a: a["due_date"])

    if not view:
        st.success("No deadlines in this view. Enjoy the breathing room! 🌿")
    else:
        for item in view:
            days = days_remaining(item["due_date"])

            with st.container(border=True):
                left, right = st.columns([3, 1])

                with left:
                    st.markdown(
                        f"**{'🚨' if days is not None and days < 0 else '📅'} "
                        f"{item.get('course', 'Untitled')}**"
                    )
                    st.caption(
                        f"{item.get('type', 'Other')} · "
                        f"{item.get('group_name') or 'Individual'}"
                    )
                    st.write(deadline_label(item["due_date"]))

                with right:
                    st.write(priority_icon(item.get("priority")))
                    st.caption(item.get("priority") or "Medium")

    st.divider()
    st.markdown("### 🧠 Plan your study time")

    remaining_hours = sum(
        float(a.get("estimated_hours") or 0) for a in incomplete
    )
    st.metric("Estimated hours remaining", f"{remaining_hours:g} hrs")

    if remaining_hours:
        st.write(
            f"At 2 hours per day, you'll need about "
            f"{max(1, round(remaining_hours / 2))} study days."
        )

# =========================================================
# FOCUS TIMER
# =========================================================
elif page == "⏳ Focus Timer":
    st.subheader("⏳ Focus Studio")
    st.write("Focus on one task, then give yourself a proper break.")

    task_options = ["General study session"] + [
        a.get("course", "Untitled") for a in incomplete
    ]
    focus_task = st.selectbox("What are you focusing on?", task_options)

    c1, c2 = st.columns(2)
    with c1:
        focus_minutes = st.select_slider(
            "Focus session (minutes)",
            options=[5, 10, 15, 20, 25, 30, 45, 60],
            value=25,
        )
    with c2:
        break_minutes = st.select_slider(
            "Break (minutes)", options=[3, 5, 10, 15], value=5
        )

    st.markdown(
        f"""
        <div class="section-card" style="text-align:center">
          <div style="font-size:3rem">🍅</div>
          <h2>{focus_minutes} min focus · {break_minutes} min break</h2>
          <p>{html.escape(focus_task)}</p>
          <p>You've got this, Suchi! One step at a time. 💙</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("▶️ Start focus timer", type="primary"):
        st.session_state.focus_end = (
            datetime.now().timestamp() + focus_minutes * 60
        )
        st.session_state.focus_task = focus_task
        st.rerun()

    if st.session_state.focus_end:
        remaining_seconds = max(
            0,
            int(st.session_state.focus_end - datetime.now().timestamp()),
        )
        mins, secs = divmod(remaining_seconds, 60)
        st.markdown(f"# ⏱️ {mins:02d}:{secs:02d}")

        if remaining_seconds == 0:
            st.balloons()
            st.success("Focus session complete! Time for a break. 🎉")
            st.session_state.focus_end = None
        else:
            components.html(
                """
                <script>
                setTimeout(() => window.parent.location.reload(), 1000);
                </script>
                """,
                height=0,
            )
            st.caption("Stay focused — your future self will thank you!")

            if st.button("Stop timer"):
                st.session_state.focus_end = None
                st.rerun()

# =========================================================
# GROUP HUB
# =========================================================
elif page == "👥 Group Hub":
    st.subheader("👥 Group Hub")
    st.caption("Your group assignments and collaborators.")

    group_assignments = [
        a for a in assignments
        if a.get("group_name") or a.get("type") == "Group Assignment"
    ]

    groups = {}
    for item in group_assignments:
        group = item.get("group_name") or "Group not specified"
        groups.setdefault(group, []).append(item)

    if not groups:
        st.info("Add a group name to an assignment to see it here.")
    else:
        for group_name, items in groups.items():
            with st.expander(
                f"👥 {group_name} · {len(items)} assignment(s)",
                expanded=True,
            ):
                members = sorted({
                    member.strip()
                    for item in items
                    for member in (
                        item.get("group_members") or ""
                    ).split(",")
                    if member.strip()
                })

                if members:
                    st.write("**Members:** " + ", ".join(members))
                else:
                    st.caption("No group members recorded yet.")

                for item in items:
                    st.markdown(
                        f"**{item.get('course', 'Untitled')}** — "
                        f"{item.get('status', 'Not Started')}"
                    )
                    st.caption(
                        f"Deadline: {item.get('due_date') or 'Not set'} · "
                        f"Priority: {item.get('priority') or 'Medium'}"
                    )

                    if item.get("remark"):
                        st.write(f"Remark: {item['remark']}")
                    if item.get("notes"):
                        st.write(f"Notes: {item['notes']}")

# =========================================================
# ANALYTICS AND EXPORT
# =========================================================
elif page == "📊 Analytics & Export":
    st.subheader("📊 Study Analytics")

    if assignments:
        df = pd.DataFrame(assignments)

        c1, c2 = st.columns(2)

        with c1:
            st.markdown("#### Assignments by status")
            st.bar_chart(
                df["status"].fillna("Not Started").value_counts()
            )

        with c2:
            st.markdown("#### Assignments by priority")
            if "priority" in df.columns:
                st.bar_chart(
                    df["priority"].fillna("Medium").value_counts()
                )

        st.markdown("#### Course workload")
        if "course" in df.columns:
            st.bar_chart(
                df["course"].fillna("Unspecified").value_counts()
            )

        st.markdown("#### Estimated study hours")
        if "estimated_hours" in df.columns:
            hours = pd.to_numeric(
                df["estimated_hours"], errors="coerce"
            ).fillna(0)
            st.metric("Total estimated hours", f"{hours.sum():g} hrs")
    else:
        st.info("Add assignments to unlock your analytics.")

    st.divider()
    st.markdown("### 📥 Export your data")

    if assignments:
        csv_data = pd.DataFrame(assignments).to_csv(
            index=False
        ).encode("utf-8-sig")

        st.download_button(
            "⬇️ Download assignments as CSV",
            data=csv_data,
            file_name=f"study_planner_{today.isoformat()}.csv",
            mime="text/csv",
            use_container_width=True,
        )
    else:
        st.button("⬇️ Download assignments as CSV", disabled=True)

# =========================================================
# DASHBOARD
# =========================================================
elif page == "🏡 Dashboard":
    st.subheader("✨ Your study space")
    st.caption("Choose one small action to move forward today.")

    quick1, quick2, quick3 = st.columns(3)

    with quick1:
        st.markdown("### ➕ Add a task")
        st.write("Capture a new assignment before you forget.")

        if st.button("Add assignment", use_container_width=True):
            st.session_state.main_navigation = "➕ Add Assignment"
            st.rerun()

    with quick2:
        st.markdown("### ⏳ Focus time")
        st.write("Set aside a quiet block for deep work.")

        if st.button("Open focus timer", use_container_width=True):
            st.session_state.main_navigation = "⏳ Focus Timer"
            st.rerun()

    with quick3:
        st.markdown("### 🗓️ Plan ahead")
        st.write("See deadlines before they become urgent.")

        if st.button("View deadlines", use_container_width=True):
            st.session_state.main_navigation = "🗓️ Deadline Planner"
            st.rerun()

    st.divider()
    st.markdown("### 🔔 Needs your attention")

    attention = overdue + [a for a in due_soon if a not in overdue]
    attention.sort(
        key=lambda a: (
            days_remaining(a.get("due_date"))
            if days_remaining(a.get("due_date")) is not None
            else 9999
        )
    )

    if attention:
        for item in attention[:6]:
            with st.container(border=True):
                c1, c2 = st.columns([3, 1])

                with c1:
                    st.markdown(
                        f"**{item.get('course', 'Untitled')}** "
                        f"{priority_icon(item.get('priority'))}"
                    )
                    st.caption(
                        f"{deadline_label(item.get('due_date'))} · "
                        f"{item.get('status', 'Not Started')}"
                    )

                with c2:
                    st.caption(item.get("priority") or "Medium")
    else:
        st.success("You're clear of urgent deadlines in the next week! 🌈")

    st.divider()
    st.markdown("### 📚 All assignments")

    f1, f2, f3 = st.columns(3)

    with f1:
        search = st.text_input("🔎 Search", placeholder="Course, group, notes...")
    with f2:
        status_filter = st.selectbox("Status", ["All"] + STATUS_OPTIONS)
    with f3:
        priority_filter = st.selectbox(
            "Priority", ["All"] + PRIORITY_OPTIONS
        )

    filtered = assignments.copy()

    if status_filter != "All":
        filtered = [
            a for a in filtered if a.get("status") == status_filter
        ]

    if priority_filter != "All":
        filtered = [
            a for a in filtered
            if a.get("priority", "Medium") == priority_filter
        ]

    if search.strip():
        term = search.strip().lower()
        filtered = [
            a for a in filtered
            if term in str(a.get("course") or "").lower()
            or term in str(a.get("group_name") or "").lower()
            or term in str(a.get("type") or "").lower()
            or term in str(a.get("group_members") or "").lower()
            or term in str(a.get("notes") or "").lower()
        ]

    if not filtered:
        st.info("No assignments match these filters.")
    else:
        for item in filtered:
            with st.container(border=True):
                title_col, status_col = st.columns([3, 1])

                with title_col:
                    st.markdown(f"**{item.get('course', 'Untitled')}**")
                    st.caption(
                        f"{item.get('type', 'Other')} · "
                        f"{item.get('category') or 'No category'}"
                    )

                with status_col:
                    st.caption(item.get("status", "Not Started"))

                detail1, detail2, detail3 = st.columns(3)
                detail1.write(
                    f"📅 {item.get('due_date') or 'No due date'}"
                )
                detail2.write(
                    f"{priority_icon(item.get('priority'))} "
                    f"{item.get('priority') or 'Medium'}"
                )
                detail3.write(
                    f"⏳ {float(item.get('estimated_hours') or 0):g} hrs"
                )

                if item.get("due_date") and item.get("status") != "Completed":
                    days = days_remaining(item["due_date"])

                    if days is not None and days < 0:
                        st.error(deadline_label(item["due_date"]))
                    elif days is not None and days <= 3:
                        st.warning(deadline_label(item["due_date"]))
                    else:
                        st.caption(deadline_label(item["due_date"]))

                if item.get("group_name"):
                    st.write(f"👥 **Group:** {item['group_name']}")
                if item.get("remark"):
                    st.write(f"💬 {item['remark']}")
                if item.get("notes"):
                    with st.expander("📝 View notes"):
                        st.write(item["notes"])

                if item.get("status") != "Completed":
                    if st.button(
                        "✅ Mark as completed",
                        key=f"complete_{item['id']}",
                        use_container_width=True,
                    ):
                        try:
                            supabase.table("assignments").update({
                                "status": "Completed",
                                "updated_at": datetime.now().astimezone().isoformat(),
                            }).eq("id", item["id"]).execute()

                            refresh_data()
                            st.balloons()
                            st.toast("Well done! Another goal achieved! 🎉")
                            st.rerun()
                        except Exception as error:
                            show_error("complete the assignment", error)

    st.divider()
    st.markdown("### 💌 A little encouragement")

    if st.button("✨ Give me a motivational message"):
        st.success(random.choice([
            "You don't have to do everything today. Just take the next step.",
            "Progress, not perfection. You're building something great.",
            "Future you will be glad you started today.",
            "One focused session is better than a day of worrying.",
            "You've handled hard things before. You can do this too.",
            "Small, consistent steps lead to big results.",
        ]))

# =========================================================
# FOOTER
# =========================================================
st.divider()

st.markdown(
    f"""
    <div style="text-align:center;padding:10px;color:{theme["muted"]}">
      Made for Suchi's study journey with 💙 · One step at a time
    </div>
    """,
    unsafe_allow_html=True,
)
