import os
import urllib
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

#
# FORM JSON FUNCTIONS
#

def validate_json(fields, json):
    for f in fields:
        if f not in json:
            return False
    return True

def validate_slot_usage(slot_name, resource_name):
    ...

#
# EMAIL FUNCTIONS
#

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
