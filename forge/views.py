# Importing Django Utils
from django.shortcuts import render, redirect
from django.http import HttpResponse
from  django.utils import timezone
# Importing Models
from machine_management.models import Machine
from django.contrib.auth.models import User, Group

#general imports
from datetime import datetime, timedelta  

#
#   Pages/Login
#

def render_equipment(request):
    return render(request, 'forge/equipment.html', {})

def render_hours(request):
    return render(request, 'forge/hours.html', {})

def render_index(request):
    return render(request, 'forge/index.html', {})

def render_news(request):
    return render(request, 'forge/news.html', {}) # TO-DO: Implement the "News" page.

def render_our_space(request):
    return render(request, 'forge/index.html', {}) # TO-DO: Implement the "Our Space" page.

def render_status(request):
    machines = Machine.objects.filter(enabled=True).order_by('machine_name')
    output = []

    for m in machines:
        if m.in_use or m.current_print_information:
            p = m.current_print_information
            u = m.current_job
            
            if(not u and not p):
                continue
            
            if(not u):
                end_time = "Unknown"
                if(p.end_time):
                    end_time = p.end_time
                
                output.append({
                    "id": m.id,
                    "name": m.machine_name,
                    "bar_type": "bar_in_progress",
                    "text_type": "text_in_progress",
                    "bar_progress":round(p.percentage()),
                    "type":m.machine_type.machine_type_name,
                    "user":"[Unknown]",
                    "status_message": p.status_message,
                    "time_remaining_text": "Estimated Completion:",
                    "estimated_completion": (end_time),
                    "time_remaining": ""
                })
                continue
            
            if u.failed:
                bar_type = "bar_failed"
                text_type = "text_failed"
            elif u.complete:
                bar_type = "bar_complete"
                text_type = "text_complete"
            elif u.error:
                bar_type = "bar_error"
                text_type = "text_error"
            else:
                bar_type = "bar_in_progress"
                text_type = "text_in_progress"

            if u.complete:
                bar_progress = 100
                time_remaining_text = "Time of Completion:"
                time_remaining = f""
                
                end_time = u.end_time
                if(p and p.end_time):
                    end_time = p.end_time
                    
                estimated_completion = end_time
                
            elif u.failed:

                fail_time = u.clear_time
                expiration_time = u.clear_time + timedelta(hours=1)

                percent_expired = (timezone.now() - fail_time).total_seconds() / (60 * 60)
                bar_progress = int(100 * percent_expired)

                time_remaining_text = "Restart By:"
                time_remaining = ""
                estimated_completion = u.clear_time + timedelta(hours=1)
            else:
                
                start_time = u.start_time
                end_time = u.end_time
                if(p):
                    start_time = p.start_time
                    print(p.end_time)
                    if(p.end_time):
                        end_time = p.end_time
                
                duration = end_time - start_time
                elapsed = timezone.now() - start_time
                percent_complete = elapsed.total_seconds() / duration.total_seconds()
                bar_progress = int(100 * percent_complete)

                time_remaining_text = "Estimated Completion:"
                time_remaining = f""
                estimated_completion = end_time

            if u.userprofile.anonymous_usages:
                user_name = "[hidden]"
            else:
                user_name = f"{u.userprofile.user.first_name} {u.userprofile.user.last_name[:1].capitalize()}."
            
            status_message = u.status_message
            if (p and p.status_message):
                status_message = p.status_message
                
            output.append({
                "id": m.id,
                "name": m.machine_name,
                "bar_type": bar_type,
                "text_type": text_type,
                "bar_progress":bar_progress,
                "type":m.machine_type.machine_type_name,
                "user":user_name,
                "status_message": status_message,
                "time_remaining_text": time_remaining_text,
                "estimated_completion": estimated_completion,
                "time_remaining": time_remaining
            })
        else:
            output.append({
                "id": m.id,
                "name": m.machine_name,
                "bar_type": "bar_in_progress",
                "text_type": "text_in_progress",
                "bar_progress": 0,
                "type":m.machine_type.machine_type_name,
                "user":f"No User",
                "status_message":"Not In Use",
                "time_remaining_text": "",
                "estimated_completion": "",
                "time_remaining": ""
                })

    return render(request, 'forge/status.html', {"machines":output})