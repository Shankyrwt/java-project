import os
import sys
import requests
from jira import JIRA
from notion_client import Client
from jira.exceptions import JIRAError

def get_jira_tickets(sprint_name):
    try:
        # Connect to JIRA
        jira = JIRA(server=os.environ['JIRA_URL'], basic_auth=(os.environ['JIRA_EMAIL'], os.environ['JIRA_API_TOKEN']))
        
        # Define JQL query
        jql_query = f'sprint = "{sprint_name}" AND project = "CER"'
        
        # Execute JQL query
        issues = jira.search_issues(jql_query)
        return issues
    except Exception as e:  # Catch any exception
        print(f"Failed to retrieve JIRA tickets: {e}")
        return None

def get_merged_prs():
    # Implement GitHub API call to get merged PRs
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
    
    print(f"Notion page created: {new_page['url']}")

def generate_release_notes(sprint_name):
    tickets = get_jira_tickets(sprint_name)
    if tickets is None:
        print("Failed to retrieve JIRA tickets.")
        return
    
    prs = get_merged_prs()
    
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
    
    with open("release_notes.md", "w") as f:
        f.write(content)
    
    create_notion_page(sprint_name, content)

if __name__ == "__main__":
    sprint_name = sys.argv[1]
    generate_release_notes(sprint_name)
