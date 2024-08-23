import os
from jira import JIRA
import sys
from jira.exceptions import JIRAError

def get_jira_tickets(sprint_name):
    try:
        # Connect to JIRA
        jira = JIRA(server=os.environ['JIRA_URL'], basic_auth=(os.environ['JIRA_EMAIL'], os.environ['JIRA_API_TOKEN']))
        
        # Define JQL query
        jql_query = f'sprint = "{sprint_name}" AND project = "SCRUM" AND status = Done'
        
        # Execute JQL query
        issues = jira.search_issues(jql_query, maxResults=1000)
        return issues
    except JIRAError as e:
        print(f"JIRA Error: {str(e)}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        return None

def generate_release_notes(sprint_name):
    tickets = get_jira_tickets(sprint_name)
    if tickets is None:
        print("Failed to retrieve JIRA tickets.")
        return
    
    features = []
    bugfixes = []
    config_changes = []

    for ticket in tickets:
        summary = ticket.fields.summary.lower()
        if ticket.fields.issuetype.name.lower() == 'bug':
            bug_fixes.append(f"- {ticket.key} {ticket.fields.summary}")
        elif "config" in summary:
            config_changes.append(f"- {ticket.key} {ticket.fields.summary}")
        else:
            features.append(f"- {ticket.key} {ticket.fields.summary}")

    content = f"Release Notes for {sprint_name}\n\n"
    
    if features:
        content += "Features:\n"
        content += "\n".join(features) + "\n\n"
    
    if bug_fixes:
        content += "Bug Fixes:\n"
        content += "\n".join(bug_fixes) + "\n\n"

    if config_changes:
        content += "Config Changes:\n"
        content += "\n".join(config_changes) + "\n"
    
    print(content)
    
    with open("release_notes.md", "w") as f:
        f.write(content)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate_release_notes.py <sprint_name>")
        sys.exit(1)
    sprint_name = sys.argv[1]
    generate_release_notes(sprint_name)
