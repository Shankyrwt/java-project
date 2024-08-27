import os
from jira import JIRA
import sys

def get_jira_tickets(sprint_name):
    try:
        # Connect to JIRA
        jira = JIRA(server=os.environ['JIRA_URL'], basic_auth=(os.environ['JIRA_EMAIL'], os.environ['JIRA_API_TOKEN']))
        
        # Define JQL query
        jql_query = f'sprint = "{sprint_name}" AND project = "SCRUM" AND status = Done'
        
        # Execute JQL query
        issues = jira.search_issues(jql_query, maxResults=1000)
        return issues
    except Exception as e:
        print(f"An error occurred while fetching JIRA tickets: {str(e)}")
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

def generate_release_notes(sprint_name, version):
    tickets = get_jira_tickets(sprint_name)
    if tickets is None:
        print("Failed to retrieve JIRA tickets.")
        return

    features = []
    bug_fixes = []
    config_changes = []
    repo_notes = {}

    for ticket in tickets:
        categories = categorize_ticket(ticket)
        if 'bug' in categories:
            bug_fixes.append(f"- {ticket.key} {ticket.fields.summary}")
        if 'config' in categories:
            config_changes.append(f"- {ticket.key} {ticket.fields.summary}")
        if 'feature' in categories:
            features.append(f"- {ticket.key} {ticket.fields.summary}")

        # Extract repository information (assuming branches field contains relevant data)
        for branch in ticket.fields.branches:
            repo_name = branch['repository']['name']
            if repo_name not in repo_notes:
                repo_notes[repo_name] = []
            repo_notes[repo_name].append(f"- {ticket.key} {ticket.fields.summary}")

    # Create release notes content
    content = f"Release Notes for {sprint_name} (Version: {version})\n\n"
    
    if features:
        content += "Features:\n" + "\n".join(features) + "\n\n"
    if bug_fixes:
        content += "Bug Fixes:\n" + "\n".join(bug_fixes) + "\n\n"
    if config_changes:
        content += "Config Changes:\n" + "\n".join(config_changes) + "\n"

    print(content)
    
    # Write general release notes
    with open("release_notes.md", "w") as f:
        f.write(content)

    # Write repository-specific release notes
    for repo, notes in repo_notes.items():
        repo_file = f"{repo}_release_notes.md"
        with open(repo_file, "w") as f:
            f.write(f"Release Notes for {repo} (Version: {version})\n\n")
            f.write("\n".join(notes))

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python generate_release_notes.py <sprint_name> <version>")
        sys.exit(1)
    sprint_name = sys.argv[1]
    version = sys.argv[2]
    generate_release_notes(sprint_name, version)
