import os
from datetime import datetime
from zoneinfo import ZoneInfo

import requests
from dotenv import load_dotenv


def get_jira_issues():
    load_dotenv()

    base_url = os.environ.get("JIRA_BASE_URL")
    email = os.environ.get("JIRA_EMAIL")
    api_token = os.environ.get("JIRA_API_TOKEN")

    if not all([base_url, email, api_token]):
        raise ValueError("Jira 환경변수 설정을 확인해 주세요.")

    today = datetime.now(ZoneInfo("Asia/Seoul")).date().isoformat()

    url = f"{base_url.rstrip('/')}/rest/api/3/search/jql"

    params = {
        "jql": (
            "project = QAW "
            "AND assignee = currentUser() "
            "AND ("
            f'"QA End Date" = "{today}" '
            f'OR "STG End Date" = "{today}" '
            f'OR "Release Date" = "{today}"'
            ")"
        ),
        "fields": (
            "summary,"
            "customfield_10044,"
            "customfield_10046,"
            "customfield_10047"
        ),
        "maxResults": 50,
    }

    response = requests.get(
        url,
        params=params,
        auth=(email, api_token),
        headers={"Accept": "application/json"},
        timeout=15,
    )
    response.raise_for_status()

    data = response.json()
    results = []

    date_fields = {
        "QA": "customfield_10044",
        "STG": "customfield_10046",
        "RELEASE": "customfield_10047",
    }

    for issue in data.get("issues", []):
        fields = issue.get("fields", {})

        for stage, field_id in date_fields.items():
            if fields.get(field_id) == today:
                results.append({
                    "issue_key": issue["key"],
                    "stage": stage,
                })

    return results


if __name__ == "__main__":
    print("Jira 조회 결과:", get_jira_issues())