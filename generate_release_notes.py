import os
import sys
import requests
from jira import JIRA
from notion_client import Client

def get_jira_tickets(sprint_name):
    # Use basic authentication (email and API token)
    jira = JIRA(
        server=os.environ['JIRA_URL'],
        basic_auth=(os.environ['JIRA_EMAIL'], os.environ['JIRA_API_TOKEN'])
    )

    # Example JQL query to get issues from the specified sprint
    jql_query = f'sprint = "{sprint_name}"'
    issues = jira.search_issues(jql_query)

    # Convert issues to a list of ticket objects
    tickets = [
        {"key": issue.key, "summary": issue.fields.summary, "type": issue.fields.issuetype.name}
        for issue in issues
    ]
    
    return tickets

def get_merged_prs():
    # Implement GitHub API call to get merged PRs
    # Return a list of PR objects
    pass

def create_notion_page(sprint_name, content):
    notion = Client(auth=os.environ["NOTION_API_TOKEN"])
    
    new_page = notion.pages.create(
        parent={"type": "workspace", "workspace": True},
        properties={
            "title": [{"text": {"content": f"Release Notes for {sprint_name}"}}]
        },
        children=[
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": content}}]
                }
            }
        ]
    )
    
    print(f"Notion page created: {new_page.url}")

def generate_release_notes(sprint_name):
    tickets = get_jira_tickets(sprint_name)
    prs = get_merged_prs()
    
    # Generate release notes content
    content = f"Release Notes for {sprint_name}\n\n"
    content += "Features:\n"
    for ticket in tickets:
        if ticket["type"] == "Feature":
            content += f"- {ticket['key']} {ticket['summary']}\n"
    
    content += "\nBug Fixes:\n"
    for ticket in tickets:
        if ticket["type"] == "Bug":
            content += f"- {ticket['key']} {ticket['summary']}\n"
    
    content += "\nPull Requests:\n"
    for pr in prs:
        content += f"- {pr['title']} (#{pr['number']})\n"
    
    # Write content to a file for GitHub release
    with open("release_notes.md", "w") as f:
        f.write(content)
    
    # Create Notion page
    create_notion_page(sprint_name, content)

if __name__ == "__main__":
    sprint_name = sys.argv[1]
    generate_release_notes(sprint_name)
