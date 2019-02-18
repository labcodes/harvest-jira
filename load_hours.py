from datetime import date, datetime
from decouple import config
from harvest_api import HarvestClient
from jira_api import (
    format_hours, format_notes, extract_task_code, format_date,
    JiraClient
)


harvest_client = HarvestClient()
jira_client = JiraClient()

date_from = date.today().isoformat()
date_to = date.today().isoformat()

harvest_filters = {
    'user_id': config('HARVEST_USER_ID'),
    'client_id': config('HARVEST_CLIENT_ID'),
    'from': date_from,
    'to': date_to
}

time_entries = harvest_client.filter_resource(
    'time_entries', **harvest_filters)

for entry in time_entries:
    entry_date = format_date(entry['created_at'])
    entry_hours = format_hours(entry['hours'])
    notes = format_notes(entry['notes'])

    if 'external_reference' in entry:
        if not entry.get('external_reference'):
            continue

        task_code = extract_task_code(
            entry['external_reference']['permalink'])

        response = jira_client.add_worklog(
            task_code, entry_date, entry_hours, notes)

        if response.status_code == 201:
            print("{task} - Worklog {hours} created on {date}".format(
                task=task_code,
                hours=entry_hours,
                date=entry_date
            ))
        else:
            print("{task} - Error {status_code} when creating worklog {hours} on {date}".format(
                task=task_code,
                status_code=response.status_code,
                hours=entry_hours,
                date=entry_date
            ))
