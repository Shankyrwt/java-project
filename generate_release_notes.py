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

def categorize_ticket(ticket):
    # Keywords for categorization
    bug_keywords = ['fix', 'error', 'issue', 'correct', 'repair', 'resolve', 'revert']
    config_keywords = ['config', 'configs']

    # Convert summary to lowercase for matching
    summary = ticket.fields.summary.lower()
    
    # Determine categories
    is_bug = any(keyword in summary for keyword in bug_keywords)
    is_config = any(keyword in summary for keyword in config_keywords)

    # Ensure "configure" is not in the summary for config changes
    if 'configure' in summary:
        is_config = False

    # Determine which category to assign
    categories = []
    if is_bug:
        categories.append('bug')
    if is_config:
        categories.append('config')
    
    # If no categories matched, classify as feature
    if not categories:
        categories.append('feature')
    
    return categories

def generate_release_notes(sprint_name):
    tickets = get_jira_tickets(sprint_name)
    if tickets is None:
        print("Failed to retrieve JIRA tickets.")
        return
    
    features = []
    bug_fixes = []
    config_changes = []

    for ticket in tickets:
        categories = categorize_ticket(ticket)
        if 'bug' in categories:
            bug_fixes.append(f"- {ticket.key} {ticket.fields.summary}")
        if 'config' in categories:
            config_changes.append(f"- {ticket.key} {ticket.fields.summary}")
        if 'feature' in categories:
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
