from cprint import cprint
from decouple import config
from harvest_api import HarvestClient
from jira_api import (
    format_hours, format_notes, extract_task_code, format_date,
    JiraClient, get_project_bucket, is_new_worklog
)
from hours_calendar import get_date_range, update_last_day, DATE_FORMAT


harvest_client = HarvestClient()
jira_client = JiraClient()

# Track the last day it ran


date_from, date_to = get_date_range()

cprint.info("Updating worklog from {date_from.strptime(DATE_FORMAT)} to {date_to.strptime(DATE_FORMAT}\n")

harvest_filters = {
    'user_id': config('HARVEST_USER_ID'),
    'client_id': config('HARVEST_CLIENT_ID'),
    'from': date_from.isoformat(),
    'to': date_to.isoformat()
}

time_entries = harvest_client.filter_resource(
    'time_entries', **harvest_filters)

jira_worklogs = {}

for entry in time_entries:
    entry_date = format_date(entry['created_at'])
    entry_hours = format_hours(entry['hours'])
    notes = format_notes(entry['notes'])

    if 'external_reference' in entry:
        task_code = extract_task_code(
            entry['external_reference']['permalink'])

        if task_code != 'SA-15876':  # We are skipping scrum task since we are adding worklog manually
            project_bucket = get_project_bucket(task_code)

            if not jira_worklogs.get(project_bucket):
                jira_worklogs[project_bucket] = jira_client.get_worklog(project_bucket).json()['worklogs']

            if is_new_worklog(jira_worklogs[project_bucket], entry_date, entry_hours):
                response = jira_client.add_worklog(
                    project_bucket, entry_date, entry_hours, notes)

                status_code = response.status_code

                if response.status_code == 201:
                    print(f"{project_bucket} - Worklog {entry_hours} created on {entry_date} for task {task_code}")
                else:
                    print(f"{project_bucket} - Error {status_code} when creating worklog {entry_hours} on {entry_date} for task {task_code}")
            else:
                print(f"Worklog for {task_code} already exists at {entry_date} during {entry_hours}")

update_last_day(date_to)
