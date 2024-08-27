import os
import json
from jira import JIRA

def get_jira_tickets(sprint_name):
    """Fetch JIRA tickets for a specific sprint."""
    try:
        jira_url = os.getenv('JIRA_URL')
        jira_email = os.getenv('JIRA_EMAIL')
        jira_api_token = os.getenv('JIRA_API_TOKEN')
        
        jira = JIRA(server=jira_url, basic_auth=(jira_email, jira_api_token))
        jql_query = f'sprint = "{sprint_name}" AND project = "SCRUM" AND status = Done'
        tickets = jira.search_issues(jql_query, maxResults=1000)
        
        return tickets
    except Exception as e:
        print(f"Error fetching JIRA tickets: {e}")
        return None

def categorize_ticket(ticket):
    """Categorize tickets based on custom field values."""
    categories = set()

    # Example of categorizing tickets; adjust based on your ticket structure
    if hasattr(ticket.fields, 'repository'):  # Replace with your actual custom field
        if "config" in ticket.fields.repository.lower():
            categories.add("config")
        elif "bug" in ticket.fields.repository.lower():
            categories.add("bug")
        elif "feature" in ticket.fields.repository.lower():
            categories.add("feature")

    return categories

def generate_release_notes(sprint_name, version):
    """Generate release notes based on JIRA tickets."""
    tickets = get_jira_tickets(sprint_name)
    if tickets is None:
        print("Failed to retrieve JIRA tickets.")
        return

    features = []
    bug_fixes = []
    config_changes = []
    repos = set()

    for ticket in tickets:
        categories = categorize_ticket(ticket)
        if 'bug' in categories:
            bug_fixes.append(f"- {ticket.key} {ticket.fields.summary}")
        if 'config' in categories:
            config_changes.append(f"- {ticket.key} {ticket.fields.summary}")
        if 'feature' in categories:
            features.append(f"- {ticket.key} {ticket.fields.summary}")

        # Extract repository from custom field
        if hasattr(ticket.fields, 'customfield_12345'):  # Replace with your actual custom field
            repo_name = ticket.fields.customfield_12345
            repos.add(repo_name)

    content = f"Release Notes for {sprint_name} (Version: {version})\n\n"
    
    if features:
        content += "Features:\n" + "\n".join(features) + "\n\n"
    if bug_fixes:
        content += "Bug Fixes:\n" + "\n".join(bug_fixes) + "\n\n"
    if config_changes:
        content += "Config Changes:\n" + "\n".join(config_changes) + "\n"
    
    content += "\nRepositories involved: " + ", ".join(repos) + "\n"

    print(content)
    
    with open("release_notes.md", "w") as f:
        f.write(content)

if __name__ == "__main__":
    sprint_name = os.getenv('SPRINT_NAME')
    version = os.getenv('VERSION')
    generate_release_notes(sprint_name, version)
