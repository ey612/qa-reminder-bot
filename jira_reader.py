
import os

import requests
from dotenv import load_dotenv


def get_jira_issues():
    load_dotenv()

    base_url = os.environ.get("JIRA_BASE_URL")
    email = os.environ.get("JIRA_EMAIL")
    api_token = os.environ.get("JIRA_API_TOKEN")

    if not all([base_url, email, api_token]):
        raise ValueError("Jira 환경변수 설정을 확인해 주세요.")

    url = f"{base_url.rstrip('/')}/rest/api/3/search/jql"

    params = {
        "jql": "project = QAW AND assignee = currentUser()",
        "fields": "summary,assignee",
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

    return [issue["key"] for issue in data.get("issues", [])]


if __name__ == "__main__":
    issue_keys = get_jira_issues()
    print("Jira 조회 결과:", issue_keys)
