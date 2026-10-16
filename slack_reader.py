import os
import re
import requests
from dotenv import load_dotenv


def get_slack_bot_token():
    load_dotenv()

    slack_bot_token = os.environ.get("SLACK_BOT_TOKEN")

    if not slack_bot_token:
        raise ValueError("SLACK_BOT_TOKEN이 설정되지 않았습니다.")

    return slack_bot_token


def get_channel_id():
    slack_bot_token = get_slack_bot_token()

    headers = {
        "Authorization": f"Bearer {slack_bot_token}"
    }

    response = requests.get(
        "https://slack.com/api/conversations.list",
        headers=headers
    )

    data = response.json()
    

    if not data.get("ok"):
        raise ValueError(
            f"Slack API 호출 실패: {data.get('error', '알 수 없는 오류')}"
        )

    channels = data.get("channels", [])
    channel_id = None

    for channel in channels:
        if channel.get("name") == "qa-bot-test":
            channel_id = channel.get("id")
            break

    if not channel_id:
        raise ValueError("qa-bot-test 채널을 찾을 수 없습니다.")

    return channel_id


def get_channel_history(channel_id):
    response = requests.get(
        "https://slack.com/api/conversations.history",
        params={"channel": channel_id},
        headers={"Authorization": f"Bearer {get_slack_bot_token()}"}
    )   

    data = response.json()

    if not data.get("ok"):
        raise ValueError(
            f"Slack API 호출 실패: {data.get('error', '알 수 없는 오류')}"
        )
    return data.get("messages", [])

def find_parent_ts(channel_history, target_keyword):
    for message in channel_history:
        text = message.get("text", "")

        # 봇이 전송한 리마인드/상태 확인 메시지는 Parent 후보에서 제외
        if "종료 댓글이 없는 티켓:" in text:
            continue

        if "종료 코멘트가 없는 티켓이 있습니다." in text:
            continue

        # 티켓 키를 독립된 값으로 매칭 (QAW-5와 QAW-50 구분)
        pattern = rf"(?<![A-Za-z0-9-]){re.escape(target_keyword)}(?![A-Za-z0-9-])"

        if re.search(pattern, text):
            return message.get("ts")

    return None


def get_thread_messages(channel_id, parent_ts):
    response = requests.get(
        "https://slack.com/api/conversations.replies",
        params={
            "channel": channel_id,
            "ts": parent_ts
        },
        headers={"Authorization": f"Bearer {get_slack_bot_token()}"}
    )

    data = response.json()

    if not data.get("ok"):
        raise ValueError(
            f"Slack API 호출 실패: {data.get('error', '알 수 없는 오류')}"
        )

    return data.get("messages", [])


END_PATTERNS = {
    "QA": r"QA.*종료(?!\s*(?:예정|불가))",
    "STG": r"STG.*종료(?!\s*(?:예정|불가))",
    "RELEASE": r"운영\s*모니터링.*종료(?!\s*(?:예정|불가))",
}


def has_end_comment(thread_messages, stage, parent_ts):
    pattern = END_PATTERNS[stage]

    for message in thread_messages:
        # Parent 메시지는 종료 코멘트 검사에서 제외
        if message.get("ts") == parent_ts:
            continue

        text = message.get("text", "")

        if re.search(pattern, text, re.IGNORECASE):
            return True

    return False


def check_qa_end_comment(jira_issues):
    if not jira_issues:
        print("오늘 종료 확인 대상 티켓이 없습니다.")
        return None

    missing_tickets = []
    not_found_tickets = []

    channel_id = get_channel_id()
    channel_history = get_channel_history(channel_id)

    for issue in jira_issues:
        ticket_key = issue["issue_key"]
        stage = issue["stage"]

        parent_ts = find_parent_ts(channel_history, ticket_key)

        if not parent_ts:
            not_found_tickets.append(f"{ticket_key} ({stage})")
            continue

        thread_messages = get_thread_messages(channel_id, parent_ts)

        if not has_end_comment(thread_messages, stage, parent_ts):
            missing_tickets.append(f"{ticket_key} ({stage})")

    if not missing_tickets and not not_found_tickets:
        print("모든 티켓의 종료 코멘트 확인 완료. 알림을 보내지 않습니다.")
        return None

    message_lines = ["종료 코멘트가 없는 티켓이 있습니다. 확인 후 종료 코멘트를 남겨주세요."]

    if missing_tickets:
        message_lines.append(
            f"종료 댓글이 없는 티켓: {', '.join(missing_tickets)}"
        )

    if not_found_tickets:
        message_lines.append(
            f"스레드를 찾지 못한 티켓: {', '.join(not_found_tickets)}"
        )

    return "\n".join(message_lines)


if __name__ == "__main__":
    test_cases = [
        ("QA 종료", "QA", True),
        ("QA종료", "QA", True),
        ("QA 테스트 종료", "QA", True),
        ("STG5 서버 종료", "STG", True),
        ("stg 종료", "STG", True),
        ("운영모니터링 종료", "RELEASE", True),
        ("운영 모니터링 종료", "RELEASE", True),
        ("QA 종료", "STG", False),
        ("STG 테스트 진행 중", "STG", False),
    ]

    for text, stage, expected in test_cases:
        thread_messages = [{"text": text}]
        actual = has_end_comment(thread_messages, stage)

        result = "PASS" if actual == expected else "FAIL"
        print(f"[{result}] {stage} | {text} | 결과: {actual}")