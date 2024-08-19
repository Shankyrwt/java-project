import os
import sys
import requests
from jira import JIRA
from notion_client import Client

def get_jira_tickets(sprint_name):
    # Setup JIRA client
    jira = JIRA(server=os.environ['JIRA_URL'], token_auth=os.environ['JIRA_API_TOKEN'])
    
    # JQL query to find issues in the specified sprint
    jql_query = f'sprint = "{sprint_name}"'
    
    # Search for issues in the sprint
    issues = jira.search_issues(jql_query)
    
    # Create a list of ticket objects with relevant data
    tickets = []
    for issue in issues:
        tickets.append({
            'key': issue.key,
            'summary': issue.fields.summary,
            'type': issue.fields.issuetype.name
        })
    
    return tickets

def get_merged_prs():
    # Placeholder implementation returning an empty list
    # Replace this with an actual API call to GitHub
    return []

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

# Setup JIRA client
jira = JIRA(server=os.environ['JIRA_URL'], token_auth=os.environ['JIRA_API_TOKEN'])

# Setup Notion client
notion = Client(auth=os.environ['NOTION_API_TOKEN'])

# Fetch closed issues from JIRA sprint board
jql_query = 'project = YOUR_PROJECT AND sprint in openSprints() AND status = Closed'
issues = jira.search_issues(jql_query)

# Process issues and update Notion
for issue in issues:
    # Create a new page in Notion for each closed issue
    notion.pages.create(
        parent={"database_id": os.environ['NOTION_DATABASE_ID']},
        properties={
            "Title": {"title": [{"text": {"content": issue.fields.summary}}]},
            "JIRA Key": {"rich_text": [{"text": {"content": issue.key}}]},
            "Status": {"select": {"name": "Closed"}},
            "Type": {"select": {"name": issue.fields.issuetype.name}},
            # Add more properties as needed
        }
    )
