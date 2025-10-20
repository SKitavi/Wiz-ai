import streamlit as st
import requests
from datetime import datetime
import json

API_URL = "http://localhost:8000/api"  # Update for production

st.set_page_config(page_title="WizAI", page_icon="🧠", layout="wide")

# Sidebar navigation
page = st.sidebar.selectbox("Navigate", ["Home", "Chat", "Tasks", "Documents", "Calendar"])

# Session state for auth
if 'token' not in st.session_state:
    st.session_state.token = None

def login_page():
    st.title("🧠 WizAI Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        response = requests.post(f"{API_URL}/auth/login", json={"email": email, "password": password})
        if response.status_code == 200:
            st.session_state.token = response.json()['access_token']
            st.success("Logged in!")
            st.rerun()
        else:
            st.error("Invalid credentials")

def home_page():
    st.title("🧠 WizAI - Your AI Life Organizer")
    st.subheader("Today's Schedule")
    
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    
    # Fetch today's plan
    response = requests.get(f"{API_URL}/plans/today", headers=headers)
    if response.status_code == 200:
        plan = response.json()
        for block in plan.get('schedule', []):
            st.info(f"⏰ {block['start_time']}-{block['end_time']}: {block['activity']}")
    else:
        st.warning("No plan for today. Generate one!")
        if st.button("Generate Today's Plan"):
            gen_response = requests.post(f"{API_URL}/plans/generate", headers=headers)
            if gen_response.status_code == 200:
                st.success("Plan generated!")
                st.rerun()
    
    # Quick stats
    col1, col2, col3 = st.columns(3)
    tasks_resp = requests.get(f"{API_URL}/tasks?status=pending", headers=headers)
    if tasks_resp.status_code == 200:
        tasks = tasks_resp.json()
        col1.metric("Pending Tasks", len(tasks))
        urgent = [t for t in tasks if t.get('priority') == 'high']
        col2.metric("Urgent Tasks", len(urgent))
        col3.metric("Completed Today", 5)  # Mock for now
def chat_page():
    st.title("💬 Chat with WizAI")
    
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    
    # Chat history
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Display chat messages
    for msg in st.session_state.chat_history:
        with st.chat_message(msg['role']):
            st.write(msg['content'])
    
    # Chat input
    if prompt := st.chat_input("Ask WizAI anything..."):
        # Add user message
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        # Get AI response
        with st.spinner("WizAI is thinking..."):
            response = requests.post(
                f"{API_URL}/chat",
                headers=headers,
                json={"message": prompt, "chat_history": st.session_state.chat_history}
            )
            
            if response.status_code == 200:
                ai_response = response.json()['response']
                st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
                st.rerun()

def tasks_page():
    st.title("📋 Task Manager")
    
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    
    # Add new task
    with st.expander("➕ Add New Task"):
        title = st.text_input("Task Title")
        deadline = st.date_input("Deadline")
        course = st.text_input("Course")
        priority = st.selectbox("Priority", ["low", "medium", "high"])
        
        if st.button("Create Task"):
            task_data = {
                "title": title,
                "deadline": deadline.isoformat(),
                "course": course,
                "priority": priority
            }
            response = requests.post(f"{API_URL}/tasks", headers=headers, json=task_data)
            if response.status_code == 200:
                st.success("Task created!")
                st.rerun()
    # Display tasks
    st.subheader("All Tasks")
    response = requests.get(f"{API_URL}/tasks", headers=headers)
    if response.status_code == 200:
        tasks = response.json()
        for task in tasks:
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
                col1.write(f"**{task['title']}**")
                col2.write(f"📅 {task['deadline']}")
                col3.write(f"🔥 {task['priority']}")
                if col4.button("✓", key=f"complete_{task['id']}"):
                    requests.put(f"{API_URL}/tasks/{task['id']}", 
                               headers=headers, 
                               json={"status": "completed"})
                    st.rerun()
                st.divider()

def documents_page():
    st.title("📄 Document Upload & Processing")
    
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    
    st.write("Upload your syllabus, assignment sheets, or screenshots to automatically extract tasks.")
    
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=['pdf', 'png', 'jpg', 'jpeg', 'docx'],
        help="Upload PDF, image, or Word document"
    )
    
    if uploaded_file and st.button("Process Document"):
        with st.spinner("🔍 Extracting information..."):
            files = {"file": uploaded_file}
            response = requests.post(f"{API_URL}/documents/upload", headers=headers, files=files)
            
            if response.status_code == 200:
                result = response.json()
                st.success("✅ Document processed successfully!")
                
                st.subheader("Extracted Information")
                st.json(result['structured_data'])
                
                st.info("Tasks have been automatically added to your task list!")
            else:
                st.error("Processing failed. Please try again.")
def calendar_page():
    st.title("📅 Calendar Sync")
    
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    
    st.subheader("Google Calendar Integration")
    
    if st.button("🔄 Sync Tasks to Google Calendar"):
        with st.spinner("Syncing..."):
            response = requests.post(f"{API_URL}/calendar/sync", headers=headers)
            if response.status_code == 200:
                st.success("✅ Tasks synced to Google Calendar!")
    
    st.divider()
    
    st.subheader("Upcoming Events")
    date = st.date_input("Select Date")
    
    if st.button("Fetch Events"):
        response = requests.get(
            f"{API_URL}/calendar/events?date={date.isoformat()}", 
            headers=headers
        )
        if response.status_code == 200:
            events = response.json()
            for event in events:
                st.info(f"📍 {event.get('summary', 'Untitled')} - {event.get('start', {}).get('dateTime', 'N/A')}")
# Main app logic
if st.session_state.token is None:
    login_page()
else:
    # Display selected page
    if page == "Home":
        home_page()
    elif page == "Chat":
        chat_page()
    elif page == "Tasks":
        tasks_page()
    elif page == "Documents":
        documents_page()
    elif page == "Calendar":
        calendar_page()
    
    # Logout button in sidebar
    if st.sidebar.button("Logout"):
        st.session_state.token = None
        st.session_state.chat_history = []
        st.rerun()
