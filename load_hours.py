from cprint import cprint
from decouple import config
from harvest_api import HarvestClient
from jira_api import (
    format_hours, format_notes, validate_task_code, extract_task_code,
    extract_task_code_from_text, format_date, JiraClient, is_new_worklog
)
from hours_calendar import get_date_range, update_last_day, DATE_FORMAT


def format_harvest_url(entry_date):
    split_date = entry_date.split('-')
    return f"https://labcodes.harvestapp.com/time/day/{split_date[0]}/{split_date[1]}/{split_date[2][:2]}/"


harvest_client = HarvestClient()
jira_client = JiraClient()

date_from, date_to = get_date_range()

s_start, s_end = date_from.isoformat(), date_to.isoformat()
cprint.info(f"Updating worklog from {s_start} to {s_end}\n")

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
    notes = format_notes(entry.get('notes') or '')

    if 'external_reference' in entry:
        try:
            task_code = extract_task_code(
                entry['external_reference']['permalink'])
            is_valid = validate_task_code(task_code)
            if not is_valid:
                task_code = extract_task_code_from_text(entry['notes'])
        except TypeError:
            cprint.warn(f"Task {entry['id']} from {entry_date} has no permalink and was skipped. Make sure this task really should have no permalink: {format_harvest_url(entry_date)}")
            continue

        if not jira_worklogs.get(task_code):
            jira_worklogs[task_code] = jira_client.get_worklog(task_code).json()['worklogs']

        if is_new_worklog(jira_worklogs[task_code], entry_date, entry_hours):
            response = jira_client.add_worklog(
                task_code, entry_date, entry_hours, notes)

            status_code = response.status_code

            if response.status_code == 201:
                cprint.ok(f"{task_code} - Worklog {entry_hours} created on {entry_date} for task {task_code}")
            else:
                cprint.err(f"{task_code} - Error {status_code} when creating worklog {entry_hours} on {entry_date} for task {task_code}")
                cprint.err(f"{task_code} - Error message: {response.text}")
        else:
            cprint.info(f"Worklog for {task_code} already exists at {entry_date} during {entry_hours}")

print()
update_last_day(date_to)
