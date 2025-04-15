import streamlit as st
import requests
import datetime
from matplotlib import pyplot as plt
from io import BytesIO
import openai

client = openai.OpenAI(
    api_key=st.secrets["OPENROUTER_API_KEY"],
    base_url="https://openrouter.ai/api/v1"
)

def ask_gpt(context, user_question):
    response = client.chat.completions.create(
        model="mistralai/mixtral-8x7b-instruct",  # or "meta-llama/llama-3-8b-instruct"
        messages=[
            {"role": "system", "content": context},
            {"role": "user", "content": user_question}
        ],
        temperature=0.7
    )
    return response.choices[0].message.content


def get_deadline_badge(deadline_str):
    deadline = datetime.datetime.fromisoformat(deadline_str)
    days_remaining = (deadline.date() - datetime.date.today()).days

    if days_remaining > 2:
        return f"<span style='color: #4CAF50;'>Due in {days_remaining} days</span>"
    elif 1 <= days_remaining <= 2:
        return f"<span style='color: #FFC107;'>Due in {days_remaining} day{'s' if days_remaining > 1 else ''}</span>"
    elif days_remaining == 0:
        return f"<span style='color: #FF5722;'>Due Today!</span>"
    else:
        return f"<span style='color: #B71C1C;'>Overdue!</span>"


# Base URL of your FastAPI backend
BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Trackademics", layout="wide")

from theme import set_custom_theme
set_custom_theme()

st.markdown("<h1 style='text-align: center; color : #102E50'>🎓 Trackademics</h1>", unsafe_allow_html=True)

tabs = st.tabs(["📚 Submissions", "📝 Exams", "📊 Summary"])

# ================== SUBMISSIONS ==================
with tabs[0]:
    st.header("📚 Submissions")

    if "show_submission_form" not in st.session_state:
        st.session_state.show_submission_form = False

    if st.button("➕ Add Submission"):
        st.session_state.show_submission_form = True

    if st.session_state.show_submission_form:
        with st.form("submission_form"):
            st.subheader("New Submission")
            title = st.text_input("Title")
            subject = st.text_input("Subject")
            deadline = st.date_input("Deadline")
            description = st.text_area("Description")
            status = st.selectbox("Status", ["pending", "completed"])
            st.markdown(
                "<style>.stForm button { background-color: #F5C45E !important; color: white !important; }</style>",
                unsafe_allow_html=True
            )
            submit_btn = st.form_submit_button("Submit")

            if submit_btn:
                submission_data = {
                    "title": title,
                    "subject": subject,
                    "deadline": f"{deadline}T00:00:00",
                    "description": description,
                    "status": status
                }
                response = requests.post(f"{BASE_URL}/submission/add", json=submission_data)
                if response.status_code == 200:
                    st.success("✅ Submission added!")
                    st.session_state.show_submission_form = False
                    st.rerun()
                else:
                    st.error(f"❌ Failed to add submission: {response.text}")

    st.subheader("📋 Existing Submissions")
    filter_status = st.selectbox("Filter by Status", ["All", "pending", "completed"], key="sub_filter")

    response = requests.get(f"{BASE_URL}/submission/all")
    if response.status_code == 200:
        data = response.json().get("submissions", [])
        filtered = [item for item in data if filter_status == "All" or item["status"] == filter_status]
        if not filtered:
            st.info("No entries to display for the selected filter.")
        for item in filtered:
            with st.container():
                cols = st.columns([0.05, 0.75, 0.2])
                checked = item["status"] == "completed"
                new_status = cols[0].checkbox("", value=checked, key=f"check_{item['id']}")

                if new_status != checked:
                    updated_data = {**item, "status": "completed" if new_status else "pending"}
                    requests.delete(f"{BASE_URL}/submission/{item['id']}")
                    requests.post(f"{BASE_URL}/submission/add", json=updated_data)
                    st.rerun()

                with cols[1]:
                    st.markdown(f"""
                        <div style='padding: 0.5rem; margin-bottom: 10px; border-radius: 10px; background-color: #D1F8EF; box-shadow: 0 0 4px rgba(0,0,0,0.1);'>
                            <h4 style='margin: 0;'>{item["title"]}</h4>
                            <p><b>Subject:</b> {item["subject"]}</p>
                            <p><b>Deadline:</b> {item["deadline"]} — {get_deadline_badge(item["deadline"])}</p>
                            <p><b>Description:</b> {item["description"]}</p>
                            <span style='padding: 3px 8px; background-color: {"#FFA07A" if item["status"] == "pending" else "#38c95f"}; border-radius: 5px; font-size: 0.9em;'>
                                {item["status"].capitalize()}
                            </span>
                        </div>
                    """, unsafe_allow_html=True)

                with st.expander("❓ Need Help?"):
                    user_q = st.text_input(f"Ask something about '{item['title']}'", key=f"q_{item['id']}")
                    if st.button("Get Help", key=f"ask_{item['id']}"):
                     with st.spinner("Thinking..."):
                        context = f"Title: {item['title']}\nDescription: {item['description']}"
                        answer = ask_gpt(context, user_q)
                        st.markdown(f"**💡 GPT Suggestion:** {answer}")

                with cols[2]:
                    if st.button("🗑️", key=f"delete_{item['id']}"):
                        requests.delete(f"{BASE_URL}/submission/{item['id']}")
                        st.rerun()

            st.divider()
    else:
        st.warning("Failed to fetch submissions.")

# ================== EXAMS ==================
with tabs[1]:
    st.header("📝 Exams")

    if "show_exam_form" not in st.session_state:
        st.session_state.show_exam_form = False

    if st.button("➕ Add Exam"):
        st.session_state.show_exam_form = True

    if st.session_state.show_exam_form:
        with st.form("exam_form"):
            st.subheader("New Exam")
            title = st.text_input("Exam Title")
            subject = st.text_input("Subject", key="exam_subject")
            date = st.date_input("Date")
            description = st.text_area("Description", key="exam_desc")
            status = st.selectbox("Status", ["upcoming", "completed"], key="exam_status")
            exam_type = st.selectbox("Type", ["written", "practical"], key="exam_type")
            st.markdown(
                "<style>.stForm button { background-color: #F5C45E !important; color: white !important; }</style>",
                unsafe_allow_html=True
            )
            exam_submit_btn = st.form_submit_button("Submit")

            if exam_submit_btn:
                exam_data = {
                    "title": title,
                    "subject": subject,
                    "date": f"{date}T09:00:00",
                    "description": description,
                    "status": status,
                    "type": exam_type
                }
                response = requests.post(f"{BASE_URL}/exam/add", json=exam_data)
                if response.status_code == 200:
                    st.success("✅ Exam added!")
                    st.session_state.show_exam_form = False
                    st.rerun()
                else:
                    st.error(f"❌ Failed to add exam: {response.text}")

    st.subheader("📋 All Exams")
    filter_exam_status = st.selectbox("Filter by Status", ["All", "upcoming", "completed"])
    filter_exam_type = st.selectbox("Filter by Type", ["All", "written", "practical"])

    response = requests.get(f"{BASE_URL}/exam/all")
    if response.status_code == 200:
        data = response.json().get("exams", [])
        filtered = [
            item for item in data if
            (filter_exam_status == "All" or item["status"] == filter_exam_status) and
            (filter_exam_type == "All" or item["type"] == filter_exam_type)
        ]
        if not filtered:
            st.info("No entries to display for the selected filter.")
        for item in filtered:
            with st.container():
                cols = st.columns([0.05, 0.75, 0.2])
                checked = item["status"] == "completed"
                new_status = cols[0].checkbox("", value=checked, key=f"exam_check_{item['id']}")

                if new_status != checked:
                    updated_data = {**item, "status": "completed" if new_status else "upcoming"}
                    requests.delete(f"{BASE_URL}/exam/{item['id']}")
                    requests.post(f"{BASE_URL}/exam/add", json=updated_data)
                    st.rerun()

                with cols[1]:
                    st.markdown(f"""
                        <div style='padding: 0.5rem; margin-bottom: 10px; border-radius: 10px; background-color: #D1F8EF; box-shadow: 0 0 4px rgba(0,0,0,0.1);'>
                            <h4 style='margin: 0;'>{item["title"]}</h4>
                            <p><b>Subject:</b> {item["subject"]}</p>
                            <p><b>Date:</b> {item["date"]} — {get_deadline_badge(item["date"])}</p>
                            <p><b>Description:</b> {item["description"]}</p>
                            <p><b>Type:</b> {item["type"].capitalize()}</p>
                            <span style='padding: 3px 8px; background-color: {"#FFA07A" if item["status"] == "upcoming" else "#38c95f"}; border-radius: 5px; font-size: 0.9em;'>
                                {item["status"].capitalize()}
                            </span>
                        </div>
                    """, unsafe_allow_html=True)

                with cols[2]:
                    if st.button("🗑️", key=f"exam_delete_{item['id']}"):
                        requests.delete(f"{BASE_URL}/exam/{item['id']}")
                        st.rerun()

            st.divider()
    else:
        st.warning("Failed to fetch exams.")


# ================== SUMMARY ==================
with tabs[2]:
    st.header("📊 Summary Dashboard")

    # Fetch data
    sub_resp = requests.get(f"{BASE_URL}/submission/all")
    submissions = sub_resp.json().get("submissions", []) if sub_resp.status_code == 200 else []

    exam_resp = requests.get(f"{BASE_URL}/exam/all")
    exams = exam_resp.json().get("exams", []) if exam_resp.status_code == 200 else []


    from collections import defaultdict

    st.subheader("🧩 Status Overview")
    col1, col2 = st.columns(2)

    # ---------------------- SUBMISSION PIE CHART ----------------------
    with col1:
        pending_subjects = defaultdict(int)
        for s in submissions:
            if s["status"] == "pending":
                pending_subjects[s["subject"]] += 1

        if pending_subjects:
            sub_fig, sub_ax = plt.subplots()
            sub_fig.patch.set_alpha(0)
            sub_ax.pie(
                pending_subjects.values(),
                labels=pending_subjects.keys(),
                autopct='%1.1f%%',
                startangle=90
            )
            sub_ax.set_title("Pending Submissions by Subject")
            sub_buf = BytesIO()
            sub_fig.savefig(sub_buf, format="png")
            sub_buf.seek(0)
            st.image(sub_buf, use_container_width=True)
        else:
            st.info("No pending submissions to visualize.")


        # ----------- PRIORITY SCORING ------------

    def calculate_score(deadline_str, description):
        deadline = datetime.datetime.fromisoformat(deadline_str)
        days_left = (deadline.date() - datetime.date.today()).days
        urgency_score = max(0, 10 - days_left)  # Closer deadlines = higher score
        length_score = min(len(description) // 50, 5)  # Longer descriptions = harder tasks?
        return urgency_score + length_score

    priority_data = []

    for s in submissions:
        if s["status"] == "pending":
            score = calculate_score(s["deadline"], s["description"])
            priority_data.append((s["title"], s["subject"], s["deadline"], score))

    for e in exams:
        if e["status"] == "upcoming":
            score = calculate_score(e["date"], e["description"])
            priority_data.append((e["title"], e["subject"], e["date"], score))

    if priority_data:
        st.markdown("### 🎯 Sorted by Priority")
        sorted_items = sorted(priority_data, key=lambda x: x[-1], reverse=True)
        for title, subject, date, score in sorted_items:
            st.markdown(f"""
                <div style='padding:10px;background-color:#f4f4f4;border-radius:8px;margin-bottom:10px;'>
                    <b>{title}</b> — {subject}<br>
                    Deadline: {date}<br>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No tasks to prioritize right now.")

    # ---------------------- EXAM PIE CHART ----------------------
    with col2:
        upcoming_subjects = defaultdict(int)
        for e in exams:
            if e["status"] == "upcoming":
                upcoming_subjects[e["subject"]] += 1

        if upcoming_subjects:
            exam_fig, exam_ax = plt.subplots()
            exam_fig.patch.set_alpha(0)
            exam_ax.pie(
                upcoming_subjects.values(),
                labels=upcoming_subjects.keys(),
                autopct='%1.1f%%',
                startangle=90
            )
            exam_ax.set_title("Upcoming Exams by Subject")
            exam_buf = BytesIO()
            exam_fig.savefig(exam_buf, format="png")
            exam_buf.seek(0)
            st.image(exam_buf, use_container_width=True)
        else:
            st.info("No upcoming exams to visualize.")


# ----------- UPCOMING TASKS ------------
    st.subheader("⏳ Upcoming Submissions & Exams")

    today = datetime.date.today()

    def is_upcoming(date_str):
        date = datetime.datetime.fromisoformat(date_str).date()
        return date >= today

    upcoming_subs = [s for s in submissions if is_upcoming(s["deadline"]) and s["status"] == "pending"]
    upcoming_exams = [e for e in exams if is_upcoming(e["date"]) and e["status"] == "upcoming"]

    st.markdown("### 📚 Submissions")
    for s in sorted(upcoming_subs, key=lambda x: x["deadline"]):
        st.markdown(f"""
    <div style='padding: 10px; background-color: #fff4cc; border-radius: 10px; margin-bottom: 10px;'>
        <b>{s["title"]}</b> — {s["subject"]}<br>
        Deadline: {s["deadline"]} — {get_deadline_badge(s["deadline"])}
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 📝 Exams")
    for e in sorted(upcoming_exams, key=lambda x: x["date"]):
        st.markdown(f"""
    <div style='padding: 10px; background-color: #e2f7ff; border-radius: 10px; margin-bottom: 10px;'>
        <b>{e["title"]}</b> — {e["subject"]}<br>
        Date: {e["date"]} — {get_deadline_badge(e["date"])}
    </div>
    """, unsafe_allow_html=True)

# ----------- TIME TRACKER (NEXT DEADLINE) ------------
    st.subheader("⏱️ Time Tracker")

    all_dates = [datetime.datetime.fromisoformat(s["deadline"]) for s in upcoming_subs] + \
            [datetime.datetime.fromisoformat(e["date"]) for e in upcoming_exams]

    if all_dates:
        next_event = min(all_dates)
        time_remaining = next_event - datetime.datetime.now()
        days, seconds = time_remaining.days, time_remaining.seconds
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        st.success(f"🎯 Next deadline in **{days} days, {hours} hours, {minutes} minutes**")
    else:
        st.info("No upcoming deadlines!")


