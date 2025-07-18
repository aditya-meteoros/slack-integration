import os
import requests

webhook_url = os.getenv("SLACK_WEBHOOK_URL")
repo = os.getenv("GITHUB_REPOSITORY", "unknown-repo")
sha = os.getenv("GITHUB_SHA", "0000000")
actor = os.getenv("GITHUB_ACTOR", "unknown")
run_id = os.getenv("GITHUB_RUN_ID", "0000")
workflow = os.getenv("GITHUB_WORKFLOW", "unknown")
status = os.getenv("JOB_STATUS", "").lower()
event = os.getenv("EVENT_NAME", "")
ref_name = os.getenv("REF_NAME", "")
ref_type = os.getenv("CREATED_REF_TYPE", "")  # 'branch' or 'tag'

if event == "create" and ref_type == "branch":
    # Branch creation message
    message = (
        f":seedling: *New Branch Created!* \n"
        f"> *Branch:* `{ref_name}`\n"
        f"> *By:* `{actor}`\n"
        f"> *Repo:* `{repo}`"
    )

elif event == "push":
    # Push message with commit summary
    try:
        with open("commit_summary.txt") as f:
            commit_list = f.read().strip()
    except FileNotFoundError:
        commit_list = "_No commit summary available._"

    message = (
        f":arrow_up: *Push to `{repo}` on branch `{ref_name}`*\n"
        f"> *By:* `{actor}`\n"
        f"> *Commit:* `{sha[:7]}`\n\n"
        f"*Changes:*\n{commit_list}\n\n"
    )

    # Append status if it's a build
    if status:
        status_emoji = ":white_check_mark:" if status == "success" else ":x:"
        status_text = "SUCCEEDED" if status == "success" else "FAILED"
        message += (
            f"{status_emoji} Build *{status_text}*\n"
            f"> *Workflow:* {workflow}\n"
            f"> *Run:* https://github.com/{repo}/actions/runs/{run_id}"
        )

else:
    # Fallback message
    message = f":information_source: Unknown event `{event}` triggered by `{actor}` in `{repo}`"

# Send to Slack
response = requests.post(webhook_url, json={"text": message})
if response.status_code != 200:
    print(f"Slack notification failed: {response.status_code} - {response.text}")
else:
    print("Slack message sent.")
