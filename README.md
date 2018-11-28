# Harvest-Jira Script
This project implements a script that gets the hours of a client from Harvest and adds them as a worklog on Jira issues. This script assumes that the user is using the [Harvest Time Tracking (Official)](https://marketplace.atlassian.com/apps/1211628/harvest-time-tracking-official?hosting=cloud&tab=overview) plugin on Jira, since it takes the Jira issue ID from the permalink added by this plugin into Harvest time entry.

## Usage
To run the script:
1. Install python requirementes `pip install -r requirements.txt`
2. Create an `.env` by creating a copy of `.env.example` and filling with the correct credentials
3. Run the script `python load_hours.py`
    - Note that the script is setup to only log your time entries for the current date. If you wish to log time for a longer period of time, make sure to change the values for `date_from` and `date_to` variables on `load_hours.py` script.