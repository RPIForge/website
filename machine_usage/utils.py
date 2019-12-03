import os
import urllib

#email imports
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

#google calendar imports
from googleapiclient.discovery import build
from datetime import datetime, timedelta

def send_email(to_email, subject, html_string):
    message = Mail(
        from_email = 'no_reply@rpiforge.dev',
        to_emails = to_email,
        subject = subject,
        html_content = html_string
    )

    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
    except Exception as e:
        print(f"Error while sending email: {str(e)}")

def send_verification_email(user):
    subject = "Forge Email Verification"

    params = {
        "token":user.userprofile.email_verification_token
    }

    params_string = urllib.parse.urlencode(params)

    verification_url = f"https://www.rpiforge.dev/verify_email?{params_string}" # TODO replace URL with config value
    body = f"Thanks for signing up for the Forge! Click <a clicktracking=off href='{verification_url}'>this link</a> to verify your email."
    send_email(user.email, subject, body)


class google_calendar():
    
    calendar_service = None
    calendar_id = None

    def __init__(self):
        api_key = os.getenv('GOOGLE_API_KEY')                
        if(not api_key):
            raise ValueError("No GOOGLE_API_KEY enviromental variable")
        
        self.calendar_service = build('calendar', 'v3', developerKey=api_key)
    
        #will be by enviromental variable later
        self.calendar_id = "k2r6osjjms6lqt41bi5a7j48n0@group.calendar.google.com"
        if(not self.calendar_id):
            raise ValueError("No CALENDAR_ID enviromental variable")
    #handle events
    def recurrence_time(self,calendar_time):
        return datetime.strptime(calendar_time[:8],'%Y%m%d')

 
    def handle_event(self,event_dict):
        #if event is not all day
        if('dateTime' in event_dict['start']):
            output_dict = {
                'start':datetime.fromisoformat(event_dict['start']['dateTime']).replace(tzinfo=None),
                'end':datetime.fromisoformat(event_dict['end']['dateTime']).replace(tzinfo=None)
            }
        else:
            output_dict = {
                'start':  datetime.strptime(event_dict['start']['date'],'%Y-%m-%d'),
                'end': datetime.strptime(event_dict['start']['date'],'%Y-%m-%d')
            }
        #get event description
        output_dict['description'] = event_dict['summary']
        return [output_dict]
        
        
                
    def list_events(self, time_min=datetime.min,time_max=datetime.max):
        #handle objects that are not the right type 
        if(not isinstance(time_min, datetime)):
            raise ValueError("Invalid Paramaters: must be datetime objects")
        if(not isinstance(time_max, datetime)):
            raise ValueError("Invalid Paramaters: must be datetime objects")
    
        #set time to string 
        time_min_str = time_min.isoformat("T") + "Z"
        time_max_str = time_max.isoformat("T") + "Z"  
        
        #get the events
        event_list = self.calendar_service.events().list(calendarId=self.calendar_id, singleEvents = True, showDeleted=False, timeMax = time_max_str, timeMin = time_min_str).execute()
        
        #loop through and put events in an easier format
        current_event_list = []
        for event in event_list['items']:
            current_event_list.extend(self.handle_event(event)) 
    
        return current_event_list

    def get_hours(self, week=datetime.now()):
        if(not isinstance(week,datetime)):
            raise ValueError("Invalid Paramaters: must be datetime objects")
        
        #get week start day and end day
        start_week = week - timedelta(days=week.weekday())
        end_week = start_week + timedelta(days=6)
        start_week = datetime.combine(start_week, datetime.min.time())
        end_week = datetime.combine(end_week,datetime.max.time())
        
        #get events during the week
        week_events = self.list_events(start_week,end_week)
        for event in week_events:
            print(event['description']) 
        
         #sort each event by day 
        day_events =  [[] for j in range(7)]
        for event in week_events:
            day_events[int(event['start'].strftime('%w'))].append((event['start'],event['end']))

        output_events = [[] for i in range(7)]
        for day in range(7): 
            if(day_events[day] == []):
                continue
            day_events[day].sort(key = lambda x: x[0])
            output_events[day].append(day_events[day][0])
            for event in day_events[day]:
                current_event = output_events[day][-1]
                
                if(event[0]<= current_event[1] and event[1]<= current_event[1]):
                    pass
                elif(event[0]<= current_event[1] and event[1]>= current_event[1]):
                    current_event = (current_event[0], event[1])
                elif(event[0] > current_event[1]):
                    output_events[day].append((event[0],event[1]))
                    
        return output_events                
                   
