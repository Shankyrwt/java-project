import os
import requests
from jira import JIRA
from notion_client import Client

# Setup JIRA client
jira = JIRA(server=os.environ['JIRA_URL'], token=os.environ['JIRA_TOKEN'])

# Setup Notion client
notion = Client(auth=os.environ['NOTION_TOKEN'])

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

# If you want to include GitHub branch information, you'll need to use the GitHub API
# This part depends on how your JIRA issues are linked to GitHub branches
