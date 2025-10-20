from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from datetime import datetime, timedelta
from typing import List, Dict
import os.path
import pickle

SCOPES = ['https://www.googleapis.com/auth/calendar']

class CalendarService:
    def __init__(self):
        self.creds = None
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        """Handle OAuth authentication"""
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                self.creds = pickle.load(token)
        
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                self.creds = flow.run_local_server(port=0)
            
            with open('token.pickle', 'wb') as token:
                pickle.dump(self.creds, token)
        
        self.service = build('calendar', 'v3', credentials=self.creds)
    
    async def get_events_for_date(self, user_id: int, date: str) -> List[Dict]:
        """Fetch events for specific date"""
        start_time = datetime.fromisoformat(date)
        end_time = start_time + timedelta(days=1)
        
        events_result = self.service.events().list(
            calendarId='primary',
            timeMin=start_time.isoformat() + 'Z',
            timeMax=end_time.isoformat() + 'Z',
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        return events_result.get('items', [])
    async def create_event(self, title: str, start_time: str, end_time: str, description: str = "") -> Dict:
        """Create calendar event from WizAI task"""
        event = {
            'summary': title,
            'description': description,
            'start': {
                'dateTime': start_time,
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': end_time,
                'timeZone': 'UTC',
            },
        }
        
        created_event = self.service.events().insert(
            calendarId='primary',
            body=event
        ).execute()
        
        return created_event
    
    async def sync_tasks_to_calendar(self, user_id: int, tasks: List[Dict]):
        """Sync all user tasks to Google Calendar"""
        for task in tasks:
            # Check if already synced
            if not task.get('calendar_event_id'):
                # Create event
                event = await self.create_event(
                    title=f"[WizAI] {task['title']}",
                    start_time=task['deadline'] + 'T09:00:00',  # Default 9 AM
                    end_time=task['deadline'] + 'T10:00:00',
                    description=task.get('description', '')
                )
                
                # Store event ID in task
                # Update task in DB with event['id']
