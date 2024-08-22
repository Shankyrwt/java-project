import os
# from dotenv import load_dotenv
from jira import JIRA
from notion_client import Client
import sys
import requests
from jira.exceptions import JIRAError
# Load environment variables from .env file
# load_dotenv()

def get_jira_tickets(sprint_name):
    try:
        # Connect to JIRA
        jira = JIRA(server=os.environ['JIRA_URL'], basic_auth=(os.environ['JIRA_EMAIL'], os.environ['JIRA_API_TOKEN']))
        
        # Define JQL query
        jql_query = f'sprint = "{sprint_name}" AND project = "SCRUM"'
        
        # Execute JQL query
        issues = jira.search_issues(jql_query)
        return issues
    except Exception as e:
        print(f"Failed to retrieve JIRA tickets: {e}")
        return None

def find_pr_custom_field(ticket):
    # Iterate over all custom fields to find PR details
    for field_name, field_value in ticket.fields.__dict__.items():
        if 'customfield_' in field_name and isinstance(field_value, list):
            for item in field_value:
                # Check if the item has PR-related keys
                if isinstance(item, dict) and 'title' in item and 'url' in item:
                    return field_name
    return None

def extract_pr_details_from_jira_ticket(ticket):
    pr_details = []
    custom_field_id = find_pr_custom_field(ticket)
    
    if custom_field_id:
        for pr in ticket.fields.__dict__[custom_field_id]:
            pr_detail = {
                'title': pr.get('title', 'No Title'),
                'url': pr.get('url', 'No URL'),
                'status': pr.get('status', 'No Status'),
                'merged_by': pr.get('author', {}).get('displayName', 'Unknown'),
                'merged_at': pr.get('lastUpdate', 'Unknown Date')
            }
            pr_details.append(pr_detail)
    return pr_details

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
    
    content = f"Release Notes for {sprint_name}\n\n"
    content += "Features:\n"
    for ticket in tickets:
        if ticket.fields.issuetype.name == "Feature":
            content += f"- {ticket.key} {ticket.fields.summary}\n"
            pr_details = extract_pr_details_from_jira_ticket(ticket)
            for pr in pr_details:
                content += f"  - PR: {pr['title']} ({pr['url']}) merged by {pr['merged_by']} on {pr['merged_at']}\n"
    
    content += "\nBug Fixes:\n"
    for ticket in tickets:
        if ticket.fields.issuetype.name == "Bug":
            content += f"- {ticket.key} {ticket.fields.summary}\n"
            pr_details = extract_pr_details_from_jira_ticket(ticket)
            for pr in pr_details:
                content += f"  - PR: {pr['title']} ({pr['url']}) merged by {pr['merged_by']} on {pr['merged_at']}\n"
    # print content
    print(f"{content}")
    
    with open("release_notes.md", "w") as f:
        f.write(content)
    
    # create_notion_page(sprint_name, content)

if __name__ == "__main__":
    sprint_name = sys.argv[1]
    generate_release_notes(sprint_name)
