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
    bug_keywords = ['fix', 'error', 'issue', 'correct', 'repair', 'resolve', 'revert']
    config_keywords = ['config', 'configs']

    summary = ticket.fields.summary.lower()
    
    is_bug = any(keyword in summary for keyword in bug_keywords)
    is_config = any(keyword in summary for keyword in config_keywords)
    if 'configure' in summary:
        is_config = False

    categories = []
    if is_bug:
        categories.append('bug')
    if is_config:
        categories.append('config')
    if not categories:
        categories.append('feature')
    
    return categories

def get_repository_name(ticket):
    # Extract repository name from the GitHub information linked to the Jira ticket
    if hasattr(ticket.fields, 'branches') and ticket.fields.branches:
        # Assuming the repository name can be derived from the first branch
        return ticket.fields.branches[0]['repository']['name']
    else:
        # Fallback if no branch information is available
        return 'unknown-repo'

def generate_release_notes(sprint_name):
    tickets = get_jira_tickets(sprint_name)
    if tickets is None:
        print("Failed to retrieve JIRA tickets.")
        return
    
    repo_tickets = {}

    for ticket in tickets:
        repo_name = get_repository_name(ticket)
        categories = categorize_ticket(ticket)

        if repo_name not in repo_tickets:
            repo_tickets[repo_name] = {'features': [], 'bug_fixes': [], 'config_changes': []}

        if 'bug' in categories:
            repo_tickets[repo_name]['bug_fixes'].append(f"- {ticket.key} {ticket.fields.summary}")
        if 'config' in categories:
            repo_tickets[repo_name]['config_changes'].append(f"- {ticket.key} {ticket.fields.summary}")
        if 'feature' in categories:
            repo_tickets[repo_name]['features'].append(f"- {ticket.key} {ticket.fields.summary}")

    for repo, tickets in repo_tickets.items():
        content = f"Release Notes for {sprint_name}\n\n"
        
        if tickets['features']:
            content += "Features:\n"
            content += "\n".join(tickets['features']) + "\n\n"
        
        if tickets['bug_fixes']:
            content += "Bug Fixes:\n"
            content += "\n".join(tickets['bug_fixes']) + "\n\n"

        if tickets['config_changes']:
            content += "Config Changes:\n"
            content += "\n".join(tickets['config_changes']) + "\n"
        
        with open(f"release_notes_{repo}.md", "w") as f:
            f.write(content)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate_release_notes.py <sprint_name>")
        sys.exit(1)
    sprint_name = sys.argv[1]
    generate_release_notes(sprint_name)
