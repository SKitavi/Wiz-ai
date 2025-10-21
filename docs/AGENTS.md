# WizAI Multi-Agent System Documentation

## Agent Philosophy

Each agent in WizAI is designed as an autonomous specialist with:
- Clear role and expertise
- Specific set of tools
- Decision-making capabilities
- Ability to collaborate with other agents

## Agent Hierarchy


Agent Coordinator (Orchestrator) │ ├── Extraction Agent (Information Extraction) ├── Planner Agent (Schedule Optimization) └── Chat Agent (User Interaction)

## Agent Specifications

### 1. Extraction Agent

**Identity:**
- Name: "DocumentExtractor"
- Role: Information Extraction Specialist
- Backstory: Expert at parsing documents and extracting structured data

**Capabilities:**
- Parse PDFs, images, and Word documents
- Extract assignments with deadlines
- Identify events and dates
- Normalize date formats
- Classify task priority

**Tools:**
- `extract_assignments(text)` - Identify assignment patterns
- `extract_dates(text)` - Parse and normalize dates
- `classify_priority(task)` - Determine urgency

**Workflow:**

1. Receive document text from OCR
2. Apply NLP techniques to identify entities
3. Use LLM for structured extraction
4. Validate extracted data
5. Return JSON with confidence scores

**Example Prompt:**

You are DocumentExtractor, an expert at parsing academic documents.
Extract all assignments from this syllabus: [DOCUMENT TEXT]
Use chain-of-thought:
Identify phrases indicating assignments ("homework", "project", "due")
Extract associated dates
Determine course information
Assign priority based on proximity to deadline
Return structured JSON.

### 2. Planner Agent

**Identity:**
- Name: "ScheduleMaster"
- Role: Intelligent Schedule Optimizer
- Backstory: Expert at creating balanced, productive schedules

**Capabilities:**
- Generate daily schedules
- Optimize task allocation
- Detect calendar conflicts
- Consider user preferences
- Adjust plans dynamically

**Tools (via MCP):**
- `get_user_tasks(user_id)` - Fetch pending tasks
- `get_calendar_events(user_id, date)` - Retrieve calendar
- `calculate_priority(task)` - Priority scoring
- `estimate_duration(task)` - Time estimation

**Algorithm:**
```python
def generate_plan(tasks, calendar, preferences):
    # 1. Sort tasks by priority and deadline
    sorted_tasks = prioritize(tasks)
    
    # 2. Identify available time blocks
    free_slots = find_free_time(calendar, preferences.study_hours)
    
    # 3. Allocate tasks to slots
    schedule = []
    for task in sorted_tasks:
        best_slot = find_optimal_slot(task, free_slots, preferences)
        schedule.append(allocate(task, best_slot))
    
    # 4. Add breaks (every 90 minutes)
    schedule = insert_breaks(schedule)
    
    # 5. Validate and resolve conflicts
    schedule = resolve_conflicts(schedule, calendar)
    
    return schedule
