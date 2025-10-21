import streamlit as st
from datetime import datetime, date, timedelta
import json
import random

API_URL = "http://localhost:8000/api"  # Update for production

# DEMO MODE - Set to True for demo video
DEMO_MODE = True

# Enhanced page configuration
st.set_page_config(
    page_title="WizAI - AI Life Organizer",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better appearance
st.markdown("""
    <style>
    /* Main background and text colors */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #2d3748 0%, #1a202c 100%);
    }
    
    /* Card-like containers */
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 10px 0;
    }
    
    /* Task card styling */
    .task-card {
        background: linear-gradient(135deg, #f6f8fb 0%, #ffffff 100%);
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    
    /* Priority badges */
    .priority-high {
        background: #f56565;
        color: white;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: bold;
    }
    
    .priority-medium {
        background: #ed8936;
        color: white;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: bold;
    }
    
    .priority-low {
        background: #48bb78;
        color: white;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: bold;
    }
    
    /* Button styling */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    
    /* Info boxes */
    .stAlert {
        border-radius: 8px;
        border: none;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Chat message styling */
    .chat-message {
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
    
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    .assistant-message {
        background: #f7fafc;
        border: 1px solid #e2e8f0;
        color: #2d3748;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize mock data in session state
def initialize_mock_data():
    if 'tasks' not in st.session_state:
        st.session_state.tasks = [
            {
                "id": 1,
                "title": "Complete Machine Learning Assignment",
                "deadline": (date.today() + timedelta(days=4)).isoformat(),
                "priority": "high",
                "course": "CS 401",
                "status": "pending",
                "description": "Implement neural network from scratch"
            },
            {
                "id": 2,
                "title": "Read Chapter 5 - Renaissance History",
                "deadline": (date.today() + timedelta(days=2)).isoformat(),
                "priority": "medium",
                "course": "History 201",
                "status": "pending",
                "description": "Focus on Italian Renaissance"
            },
            {
                "id": 3,
                "title": "Group Project Meeting",
                "deadline": (date.today() + timedelta(days=1)).isoformat(),
                "priority": "high",
                "course": "Business 301",
                "status": "pending",
                "description": "Prepare presentation slides"
            },
            {
                "id": 4,
                "title": "Physics Lab Report",
                "deadline": (date.today() + timedelta(days=6)).isoformat(),
                "priority": "medium",
                "course": "Physics 102",
                "status": "pending",
                "description": "Document experiment results"
            },
            {
                "id": 5,
                "title": "Study for Calculus Midterm",
                "deadline": (date.today() + timedelta(days=7)).isoformat(),
                "priority": "high",
                "course": "Math 301",
                "status": "pending",
                "description": "Review chapters 6-10"
            },
        ]
    
    if 'schedule' not in st.session_state:
        st.session_state.schedule = [
            {"start_time": "09:00", "end_time": "10:30", "activity": "📚 Study Session - Machine Learning"},
            {"start_time": "11:00", "end_time": "12:00", "activity": "💻 Work on History Assignment"},
            {"start_time": "14:00", "end_time": "15:30", "activity": "👥 Group Project Meeting"},
            {"start_time": "16:00", "end_time": "17:00", "activity": "🏋️ Gym & Exercise"},
            {"start_time": "19:00", "end_time": "20:00", "activity": "📖 Reading Time"},
        ]
    
    if 'documents' not in st.session_state:
        st.session_state.documents = []
    
    if 'events' not in st.session_state:
        st.session_state.events = [
            {"summary": "Team Meeting", "time": "10:00 AM", "date": date.today().isoformat()},
            {"summary": "CS 401 Lecture", "time": "2:00 PM", "date": date.today().isoformat()},
            {"summary": "Study Group", "time": "6:00 PM", "date": date.today().isoformat()},
        ]

# Session state initialization
if 'token' not in st.session_state:
    st.session_state.token = "demo_token" if DEMO_MODE else None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'user_email' not in st.session_state:
    st.session_state.user_email = "sharon@wizai.com" if DEMO_MODE else None
if 'next_task_id' not in st.session_state:
    st.session_state.next_task_id = 6

# Initialize mock data
initialize_mock_data()

# Mock AI responses for chat
def get_ai_response(message):
    message_lower = message.lower()
    
    if "schedule" in message_lower or "today" in message_lower:
        pending_tasks = [t for t in st.session_state.tasks if t['status'] == 'pending']
        return f"You have {len(pending_tasks)} pending tasks today. Your next activity is at {st.session_state.schedule[0]['start_time']} - {st.session_state.schedule[0]['activity']}. Would you like me to help you prioritize your tasks?"
    
    elif "task" in message_lower and "how many" in message_lower:
        pending = sum(1 for t in st.session_state.tasks if t['status'] == 'pending')
        completed = sum(1 for t in st.session_state.tasks if t['status'] == 'completed')
        return f"You have {pending} pending tasks and {completed} completed tasks. Great progress! 🎉"
    
    elif "urgent" in message_lower or "priority" in message_lower:
        high_priority = [t for t in st.session_state.tasks if t['priority'] == 'high' and t['status'] == 'pending']
        if high_priority:
            task_list = "\n".join([f"• {t['title']} (Due: {t['deadline']})" for t in high_priority[:3]])
            return f"You have {len(high_priority)} high-priority tasks:\n{task_list}\n\nShall I help you break these down into smaller steps?"
        return "Great news! No urgent tasks at the moment. Keep up the good work! 🌟"
    
    elif "help" in message_lower or "what can you do" in message_lower:
        return """I can help you with:
• 📋 Managing and organizing your tasks
• 📅 Creating optimized daily schedules
• 🎯 Prioritizing assignments and deadlines
• 📄 Processing documents to extract tasks
• 💡 Providing study tips and productivity advice

What would you like help with?"""
    
    else:
        responses = [
            "That's a great question! Based on your current workload, I'd recommend focusing on your high-priority tasks first.",
            "I'm here to help! Would you like me to create a study plan for your upcoming deadlines?",
            "Interesting! Let me know if you need help organizing any specific tasks or scheduling activities.",
            "I can definitely help with that! Your success is my priority. What specific aspect would you like to tackle first?",
        ]
        return random.choice(responses)

# Sidebar with enhanced styling
with st.sidebar:
    st.markdown("# 🧠 WizAI")
    st.markdown("*Your AI Life Organizer*")
    st.markdown("---")
    
    # Navigation
    page = st.radio(
        "Navigate",
        ["🏠 Home", "💬 Chat", "📋 Tasks", "📄 Documents", "📅 Calendar"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # User info
    if st.session_state.token:
        st.success(f"👤 {st.session_state.user_email}")
        
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.token = None
            st.session_state.chat_history = []
            st.session_state.user_email = None
            st.rerun()
    
    # Quick stats in sidebar
    if st.session_state.token:
        st.markdown("---")
        st.markdown("### 📊 Quick Stats")
        
        pending_count = sum(1 for t in st.session_state.tasks if t['status'] == 'pending')
        completed_count = sum(1 for t in st.session_state.tasks if t['status'] == 'completed')
        
        st.metric("Tasks Today", pending_count, "2")
        st.metric("Completed", completed_count, "1")
        st.metric("Streak", "7 days", "🔥")

def home_page():
    st.markdown("# 🏠 Welcome to WizAI")
    st.markdown(f"### Good {'morning' if datetime.now().hour < 12 else 'afternoon' if datetime.now().hour < 18 else 'evening'}, {st.session_state.user_email.split('@')[0].title()}! 👋")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Today's date prominently displayed
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"""
            <div style='text-align: center; background: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
                <h2 style='color: #667eea; margin: 0;'>{datetime.now().strftime('%A')}</h2>
                <p style='color: #718096; font-size: 24px; margin: 5px 0;'>{datetime.now().strftime('%B %d, %Y')}</p>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Calculate metrics
    pending_count = sum(1 for t in st.session_state.tasks if t['status'] == 'pending')
    completed_count = sum(1 for t in st.session_state.tasks if t['status'] == 'completed')
    urgent_count = sum(1 for t in st.session_state.tasks if t['priority'] == 'high' and t['status'] == 'pending')
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
            <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 15px; color: white;'>
                <h3 style='margin: 0;'>{pending_count}</h3>
                <p style='margin: 5px 0;'>📋 Tasks Today</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 20px; border-radius: 15px; color: white;'>
                <h3 style='margin: 0;'>{urgent_count}</h3>
                <p style='margin: 5px 0;'>🔥 Urgent</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); padding: 20px; border-radius: 15px; color: white;'>
                <h3 style='margin: 0;'>{completed_count}</h3>
                <p style='margin: 5px 0;'>✅ Completed</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
            <div style='background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); padding: 20px; border-radius: 15px; color: white;'>
                <h3 style='margin: 0;'>7</h3>
                <p style='margin: 5px 0;'>🔥 Day Streak</p>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Today's Schedule
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📅 Today's Schedule")
        
        if st.session_state.schedule:
            for block in st.session_state.schedule:
                st.markdown(f"""
                    <div style='background: white; padding: 15px; border-radius: 10px; margin: 10px 0; border-left: 4px solid #667eea; box-shadow: 0 2px 4px rgba(0,0,0,0.05);'>
                        <strong style='color: #2d3748;'>⏰ {block['start_time']} - {block['end_time']}</strong><br>
                        <span style='color: #4a5568;'>{block['activity']}</span>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("📝 No schedule for today. Generate one to get started!")
        
        if st.button("🔄 Regenerate Schedule", use_container_width=True):
            with st.spinner("Creating your perfect day..."):
                st.session_state.schedule = [
                    {"start_time": "08:00", "end_time": "09:30", "activity": "🌅 Morning Routine & Breakfast"},
                    {"start_time": "10:00", "end_time": "12:00", "activity": "📚 Deep Focus Study Session"},
                    {"start_time": "13:00", "end_time": "14:00", "activity": "🍽️ Lunch Break"},
                    {"start_time": "14:30", "end_time": "16:30", "activity": "💻 Work on Projects"},
                    {"start_time": "17:00", "end_time": "18:00", "activity": "🏃 Exercise & Wellness"},
                    {"start_time": "19:00", "end_time": "20:00", "activity": "📖 Light Reading/Review"},
                ]
                st.success("✅ New schedule generated!")
                st.rerun()
    
    with col2:
        st.markdown("### 🎯 Quick Actions")
        # New Task → Goes to Tasks page with form expanded
        if st.button("➕ New Task"):
            st.session_state.current_page = "📋 Tasks"
            st.session_state.expand_new_task = True
            st.rerun()

        # Ask WizAI → Goes to Chat page
        if st.button("💬 Ask WizAI"):
            st.session_state.current_page = "💬 Chat"
            st.rerun()

        # Upload Document → Goes to Documents page
        if st.button("📄 Upload Document"):
            st.session_state.current_page = "📄 Documents"
            st.rerun()

        # Sync Calendar → Goes to Calendar page
        if st.button("🔄 Sync Calendar"):
            st.session_state.current_page = "📅 Calendar"
            st.rerun()

def chat_page():
    st.markdown("# 💬 Chat with WizAI")
    st.markdown("*Ask me anything about your tasks, schedule, or get help organizing your life!*")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Chat container
    chat_container = st.container()
    
    with chat_container:
        for msg in st.session_state.chat_history:
            if msg['role'] == 'user':
                st.markdown(f"""
                    <div class='chat-message user-message'>
                        <strong>You:</strong><br>
                        {msg['content']}
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                    <div class='chat-message assistant-message'>
                        <strong style='color: #667eea;'>🧠 WizAI:</strong><br>
                        <span style='color: #2d3748;'>{msg['content']}</span>
                    </div>
                """, unsafe_allow_html=True)
    
    # Chat input
    with st.container():
        prompt = st.chat_input("Ask WizAI anything... (e.g., 'What's my schedule today?')")
        
        if prompt:
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            
            # Get AI response
            ai_response = get_ai_response(prompt)
            st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
            
            st.rerun()

def tasks_page():
    st.markdown("# 📋 Task Manager")
    st.markdown("*Organize and track all your tasks in one place*")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Add new task section
    with st.expander("➕ **Create New Task**", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            title = st.text_input("📝 Task Title", placeholder="e.g., Complete Math Assignment", key="new_task_title")
            course = st.text_input("📚 Course/Category", placeholder="e.g., Mathematics 101", key="new_task_course")
        
        with col2:
            deadline = st.date_input("📅 Deadline", min_value=date.today(), key="new_task_deadline")
            priority = st.selectbox("🔥 Priority", ["low", "medium", "high"], key="new_task_priority")
        
        description = st.text_area("📄 Description (optional)", placeholder="Add any additional details...", key="new_task_desc")
        
        if st.button("✨ Create Task", use_container_width=True):
            if title and course:
                new_task = {
                    "id": st.session_state.next_task_id,
                    "title": title,
                    "deadline": deadline.isoformat(),
                    "course": course,
                    "priority": priority,
                    "description": description,
                    "status": "pending"
                }
                st.session_state.tasks.append(new_task)
                st.session_state.next_task_id += 1
                st.success("✅ Task created successfully!")
                st.rerun()
            else:
                st.error("❌ Please fill in both title and course")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Filter and sort options
    col1, col2, col3 = st.columns(3)
    with col1:
        filter_status = st.selectbox("Status", ["All", "Pending", "Completed"])
    with col2:
        filter_priority = st.selectbox("Priority Filter", ["All", "High", "Medium", "Low"])
    with col3:
        sort_by = st.selectbox("Sort by", ["Deadline", "Priority", "Created"])
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Display tasks
    st.markdown("### 📌 Your Tasks")
    
    # Filter tasks
    filtered_tasks = st.session_state.tasks.copy()
    
    if filter_status != "All":
        filtered_tasks = [t for t in filtered_tasks if t['status'] == filter_status.lower()]
    
    if filter_priority != "All":
        filtered_tasks = [t for t in filtered_tasks if t['priority'] == filter_priority.lower()]
    
    # Sort tasks
    if sort_by == "Deadline":
        filtered_tasks.sort(key=lambda x: x['deadline'])
    elif sort_by == "Priority":
        priority_order = {"high": 0, "medium": 1, "low": 2}
        filtered_tasks.sort(key=lambda x: priority_order[x['priority']])
    
    if not filtered_tasks:
        st.info("📭 No tasks found with the selected filters")
    
    for task in filtered_tasks:
        priority_class = f"priority-{task['priority']}"
        
        with st.container():
            col1, col2, col3, col4, col5 = st.columns([4, 2, 1, 1, 1])
            
            with col1:
                st.markdown(f"**{task['title']}**")
                st.caption(f"📚 {task.get('course', 'N/A')}")
                if task.get('description'):
                    with st.expander("Details"):
                        st.write(task['description'])
            
            with col2:
                task_date = datetime.fromisoformat(task['deadline']).date()
                days_until = (task_date - date.today()).days
                if days_until < 0:
                    st.markdown(f"<span style='color: red;'>⚠️ {abs(days_until)}d overdue</span>", unsafe_allow_html=True)
                elif days_until == 0:
                    st.markdown(f"<span style='color: orange;'>📅 Today</span>", unsafe_allow_html=True)
                elif days_until == 1:
                    st.markdown(f"<span style='color: orange;'>📅 Tomorrow</span>", unsafe_allow_html=True)
                else:
                    st.markdown(f"📅 {task['deadline']}")
            
            with col3:
                st.markdown(f"<span class='{priority_class}'>{task['priority'].upper()}</span>", unsafe_allow_html=True)
            
            with col4:
                if task['status'] == 'pending':
                    if st.button("✓", key=f"complete_{task['id']}", help="Mark as complete"):
                        task['status'] = 'completed'
                        st.success("Task completed! 🎉")
                        st.rerun()
                else:
                    st.markdown("✅")
            
            with col5:
                if st.button("🗑️", key=f"delete_{task['id']}", help="Delete task"):
                    st.session_state.tasks = [t for t in st.session_state.tasks if t['id'] != task['id']]
                    st.success("Task deleted!")
                    st.rerun()
            
            st.divider()

def documents_page():
    st.markdown("# 📄 Document Processing")
    st.markdown("*Upload syllabi, assignments, or screenshots to extract tasks automatically*")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Upload section with better styling
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col2:
        st.markdown("""
            <div style='background: white; padding: 30px; border-radius: 15px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
                <h3 style='color: #667eea;'>📤 Upload Your Document</h3>
                <p style='color: #718096;'>Supported: PDF, Images (PNG, JPG), Word Documents</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=['pdf', 'png', 'jpg', 'jpeg', 'docx'],
            label_visibility="collapsed"
        )
        
        if uploaded_file:
            st.success(f"✅ File uploaded: {uploaded_file.name}")
            
            col_a, col_b, col_c = st.columns([1, 2, 1])
            with col_b:
                if st.button("🔍 Process Document", use_container_width=True):
                    with st.spinner("🤖 AI is analyzing your document..."):
                        # Simulate processing delay
                        import time
                        time.sleep(2)
                        
                        # Add extracted tasks
                        extracted_tasks = [
                            {
                                "id": st.session_state.next_task_id,
                                "title": "Chapter 7 Reading Assignment",
                                "deadline": (date.today() + timedelta(days=5)).isoformat(),
                                "course": "Literature 301",
                                "priority": "medium",
                                "description": "Read and annotate Chapter 7",
                                "status": "pending"
                            },
                            {
                                "id": st.session_state.next_task_id + 1,
                                "title": "Essay Draft Submission",
                                "deadline": (date.today() + timedelta(days=8)).isoformat(),
                                "course": "Literature 301",
                                "priority": "high",
                                "description": "First draft of argumentative essay",
                                "status": "pending"
                            },
                        ]
                        
                        for task in extracted_tasks:
                            st.session_state.tasks.append(task)
                        
                        st.session_state.next_task_id += len(extracted_tasks)
                        
                        st.balloons()
                        st.success(f"✅ Document processed successfully! Found {len(extracted_tasks)} tasks.")
                        
                        st.markdown("<br>", unsafe_allow_html=True)
                        
                        st.subheader("📊 Extracted Information")
                        result_data = {
                            "tasks_found": len(extracted_tasks),
                            "deadlines_extracted": len(extracted_tasks),
                            "course": "Literature 301",
                            "document_type": "Syllabus",
                            "tasks": [{"title": t["title"], "deadline": t["deadline"]} for t in extracted_tasks]
                        }
                        st.json(result_data)
                        
                        st.info("💡 Tasks have been automatically added to your task list!")

def calendar_page():
    st.markdown("# 📅 Calendar Integration")
    st.markdown("*Sync your tasks with Google Calendar*")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("""
            <div style='background: white; padding: 30px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
                <h3 style='color: #667eea;'>🔄 Google Calendar Sync</h3>
                <p style='color: #718096;'>Keep your tasks in sync with Google Calendar</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("🔄 Sync Tasks to Calendar", use_container_width=True):
            with st.spinner("Syncing..."):
                import time
                time.sleep(1)
                pending_tasks = [t for t in st.session_state.tasks if t['status'] == 'pending']
                st.success(f"✅ {len(pending_tasks)} tasks synced to Google Calendar!")
    
    with col2:
        st.markdown("""
            <div style='background: white; padding: 30px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
                <h3 style='color: #667eea;'>📆 View Events</h3>
                <p style='color: #718096;'>Check your upcoming calendar events</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        selected_date = st.date_input("Select Date", value=date.today())
        
        if st.button("🔍 Fetch Events", use_container_width=True):
            with st.spinner("Fetching events..."):
                import time
                time.sleep(1)
                
                # Show events for selected date
                events_for_date = [e for e in st.session_state.events if e['date'] == selected_date.isoformat()]
                
                if not events_for_date:
                    # Generate some events
                    events_for_date = [
                        {"summary": "Morning Lecture", "time": "9:00 AM"},
                        {"summary": "Study Session", "time": "2:00 PM"},
                        {"summary": "Team Meeting", "time": "4:30 PM"},
                    ]
                
                st.success(f"📅 Found {len(events_for_date)} events")
                for event in events_for_date:
                    st.info(f"📍 {event['summary']} - {event['time']}")
    
    # Calendar view section
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 📊 Upcoming Deadlines")
    
    # Get upcoming tasks
    upcoming_tasks = [t for t in st.session_state.tasks if t['status'] == 'pending']
    upcoming_tasks.sort(key=lambda x: x['deadline'])
    
    if upcoming_tasks:
        for task in upcoming_tasks[:5]:  # Show next 5 tasks
            task_date = datetime.fromisoformat(task['deadline']).date()
            days_until = (task_date - date.today()).days
            
            if days_until < 0:
                time_text = f"⚠️ {abs(days_until)} days overdue"
                color = "#f56565"
            elif days_until == 0:
                time_text = "📅 Today"
                color = "#ed8936"
            elif days_until == 1:
                time_text = "📅 Tomorrow"
                color = "#ed8936"
            else:
                time_text = f"📅 In {days_until} days"
                color = "#48bb78"
            
            st.markdown(f"""
                <div style='background: white; padding: 15px; border-radius: 10px; margin: 10px 0; border-left: 4px solid {color};'>
                    <strong>{task['title']}</strong><br>
                    <span style='color: #718096;'>{task['course']} • {time_text}</span>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.info("🎉 No pending tasks! You're all caught up!")

# Main app logic
if st.session_state.token is None and not DEMO_MODE:
    # Login page (won't show in demo mode)
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("""
            <div style='text-align: center; padding: 40px; background: white; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.2);'>
                <h1 style='color: #667eea;'>🧠 WizAI</h1>
                <p style='color: #718096; font-size: 18px;'>Your AI-Powered Life Organizer</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        with st.container():
            st.markdown("<div style='background: white; padding: 30px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>", unsafe_allow_html=True)
            
            email = st.text_input("📧 Email", placeholder="Enter your email")
            password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
            
            col_a, col_b, col_c = st.columns([1, 2, 1])
            with col_b:
                if st.button("Login", use_container_width=True):
                    st.session_state.token = "demo_token"
                    st.session_state.user_email = email
                    st.success("✅ Logged in successfully!")
                    st.rerun()
            
            st.markdown("</div>", unsafe_allow_html=True)
else:
    # Extract page name from selection
    page_name = page.split(" ", 1)[1] if " " in page else page
    
    if "Home" in page:
        home_page()
    elif "Chat" in page:
        chat_page()
    elif "Tasks" in page:
        tasks_page()
    elif "Documents" in page:
        documents_page()
    elif "Calendar" in page:
        calendar_page()