import os
import urllib

#email imports
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


#google calendar imports
from googleapiclient.discovery import build
from datetime import datetime, timedelta
from dateutil.parser import isoparse
import os
from pytz import timezone
from django.conf import settings

#
# EMAIL FUNCTIONS
#
# ! type: Helper function
# ! function: Send email 
# ? required: destination, subject, message
# ? returns: response
# TODO: 
def send_email(to_email, subject, html_string):
    message = Mail(
        from_email = 'no_reply@rpiforge.dev',
        to_emails = to_email,
        subject = subject,
        html_content = html_string
    )

    try:
        sg = SendGridAPIClient(settings.EMAIL_HOST_PASSWORD)
        response = sg.send(message)
    except Exception as e:
        print(f"Error while sending email: {str(e)}")

# ! type: Helper function
# ! function: Send user email validation
# ? required: 
# ? returns: 
# TODO: 
def send_verification_email(user):
    subject = "Forge Email Verification"

    params = {
        "token":user.userprofile.email_verification_token
    }

    params_string = urllib.parse.urlencode(params)

    base_url = os.environ.get('SITE_URL')
    verification_url = f"https://{base_url}/verify_email?{params_string}" # TODO replace URL with config value
    body = f"Thanks for signing up for the Forge! Click <a clicktracking=off href='{verification_url}'>this link</a> to verify your email."
    send_email(user.email, subject, body)

# ! type: Helper function
# ! function: Send Usage failure email 
# ? required: 
# ? returns: 
# TODO: 
def send_failure_email(usage):
    user = usage.userprofile.user

    subject = f"Forge: Machine Failure"
    body = f"Dear {user.first_name},<br /><br />Unfortunately, your recent machine usage has failed. "
    body += f"You have one hour to return to The Forge and try again before the machine is freed for the next user.<br /><br />Details:<br /><br />"
    body += f"Machine Type: {usage.machine.machine_type.machine_type_name}<br />"
    body += f"Machine Name: {usage.machine.machine_name}<br />"
    body += f"Start Time: {usage.start_time}<br />"
    body += f"Fail Time: {usage.clear_time}"
    
    send_email(user.email, subject, body)
#
# CALENDAR FUNCTIONS
#
class google_calendar():
    # ! function: Connect with google calendar and get when volunteers are on duty.
    # !           This code should be synced with the front door bot.
    
    calendar_service = None
    calendar_id = None

    #initialize calendar with api key
    def __init__(self):
        api_key = os.getenv('GOOGLE_API_KEY')
        if(not api_key):
            raise ValueError("No GOOGLE_API_KEY enviromental variable")

        self.calendar_service = build('calendar', 'v3', developerKey=api_key)

        #will be by enviromental variable later
        self.calendar_id = "k2r6osjjms6lqt41bi5a7j48n0@group.calendar.google.com"
        if(not self.calendar_id):
            raise ValueError("No CALENDAR_ID enviromental variable")


    #format recurrence event
    def recurrence_time(self,calendar_time):
        return datetime.strptime(calendar_time[:8],'%Y%m%d')

    #read in google data and format
    def handle_event(self,event_dict):
    
        #if event is not all day
        if('dateTime' in event_dict['start']):
            output_dict = {
                'start':isoparse(event_dict['start']['dateTime']).replace(tzinfo=None),
                'end':isoparse(event_dict['end']['dateTime']).replace(tzinfo=None)
            }
        else:
            output_dict = {
                'start':  datetime.strptime(event_dict['start']['date'],'%Y-%m-%d'),
                'end': datetime.strptime(event_dict['start']['date'],'%Y-%m-%d')
            }
        #get event description
        if('summary' in event_dict):
            output_dict['description'] = event_dict['summary']
        else:
            output_dict['description'] = ""
           
        return [output_dict]


    #list events going on
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
        event_list = self.calendar_service.events().list(calendarId=self.calendar_id, singleEvents = True, showDeleted=True, timeMax = time_max_str, timeMin = time_min_str).execute()

        #loop through and put events in an easier format
        current_event_list = []
        for event in event_list['items']:
            if(event['status'] == 'cancelled'):
                continue
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

        #sort events by day
        day_events =  [[] for j in range(7)]
        for event in week_events:
            day_events[int(event['start'].strftime('%w'))].append((event['start'],event['end']))

        #initialize the output array
        output_events = [[] for i in range(7)]

        #loop through each event
        for day in range(7):
            #if day is empty then skip
            if(day_events[day] == []):
                continue

            #sort day's events by start time
            day_events[day].sort(key = lambda x: x[0])
            output_events[day].append(day_events[day][0])

            #for each event see if it adds onto the previous event
            for event in day_events[day]:
                current_event = output_events[day][-1]

                if(event[0]<= current_event[1] and event[1]<= current_event[1]):
                    pass
                elif(event[0]<= current_event[1] and event[1]>= current_event[1]):
                    output_events[day][-1] = (current_event[0], event[1])
                elif(event[0] > current_event[1]):
                    output_events[day].append((event[0],event[1]))

        #return event times
        return output_events

    def get_current_events(self):
        #get current time and adjust to est from whatever timezone
        current_time = datetime.now()
        
        #get start and end of day
        start_time = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
        end_time = current_time.replace(hour=23,minute=59, second=0, microsecond=0)
        
        #get list of events for today
        day_list = self.list_events(start_time,end_time)
        
        #find all current events
        current_events = []
        for event in day_list:
            print("START:",event['start'],"CURRENT:",current_time,"END:",event['end'])
            if(event['start']<current_time and event['end']>current_time):
                current_events.append(event)
        return current_events           
