from datetime import datetime
import json
import requests
from decouple import config


class JiraClient:

    def __init__(self):
        username = config('JIRA_USERNAME')
        api_token = config('JIRA_API_TOKEN')
        self.basic_auth = requests.auth.HTTPBasicAuth(username, api_token)
        self.base_url = 'https://{jira_domain}.atlassian.net/rest/api/3'.format(
            jira_domain=config('JIRA_DOMAIN')
        )

    def add_worklog(self, task_code, date_started, time_spent, comments):
        worklog_url = '{base_url}/issue/{task_code}/worklog?notifyUsers=false'.format(
            base_url=self.base_url,
            task_code=task_code)

        worklog_payload = {
            "started": date_started,
            "timeSpent": time_spent
        }

        if comments:
            worklog_payload["comment"] = {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": comments
                            }
                        ]
                    }
                ]
            }

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        response = requests.post(
            worklog_url,
            auth=self.basic_auth,
            data=json.dumps(worklog_payload),
            headers=headers
        )

        return response


def format_notes(entry_notes):
    notes_row = entry_notes.split('\n')
    return notes_row[1:len(notes_row)] if len(notes_row) > 1 else ""


def format_date(entry_date):
    date_obj = datetime.strptime(entry_date, "%Y-%m-%dT%H:%M:%SZ")
    date_formatted = '{}+0000'.format(date_obj.isoformat(
        timespec='milliseconds'))
    return date_formatted


def format_hours(entry_hours):
    hours_decimal = float(entry_hours)
    hours = int(hours_decimal)
    minutes = int((hours_decimal - hours) * 60)
    formatted_hours = '{hours}h {minutes}m'.format(
        hours=hours,
        minutes=minutes
    )
    return formatted_hours


def extract_task_code(external_permalink):
    task_code = external_permalink.split('/')[-1]

    if '?' in task_code:
        task_code = task_code.split('?')[0]

    if '#' in task_code:
        task_code = task_code.replace('#', '')

    return task_code