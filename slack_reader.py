import os
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

        # 봇이 보낸 QA 종료 상태 알림은 Parent 검색에서 제외
        if text.startswith("QA 종료 상태 확인 결과"):
            continue

        if target_keyword in text:
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


def has_end_comment(thread_messages, end_keyword):
    for message in thread_messages:
        text = message.get("text", "")

        if end_keyword in text:
            return True

    return False


def check_qa_end_comment():
    ticket_keys = ["CHAE-0001", "CHAE-0002", "CHAE-0003"]
    end_keyword = "테스트 종료"

    missing_tickets = []
    not_found_tickets = []

    channel_id = get_channel_id()
    channel_history = get_channel_history(channel_id)

    for ticket_key in ticket_keys:
        parent_ts = find_parent_ts(channel_history, ticket_key)

        if not parent_ts:
            not_found_tickets.append(ticket_key)
            continue

        thread_messages = get_thread_messages(channel_id, parent_ts)

        if not has_end_comment(thread_messages, end_keyword):
            missing_tickets.append(ticket_key)

        # 두 목록이 모두 비어 있으면 알림을 보내지 않음
    if not missing_tickets and not not_found_tickets:
        print("모든 티켓의 QA 종료 상태 확인 완료. 알림을 보내지 않습니다.")
        return

    message_lines = ["QA 종료 상태 확인 결과"]

    if missing_tickets:
        message_lines.append(
            f"종료 댓글이 없는 티켓: {', '.join(missing_tickets)}"
        )

    if not_found_tickets:
        message_lines.append(
            f"Parent를 찾지 못한 티켓: {', '.join(not_found_tickets)}"
        )

    message_text = "\n".join(message_lines)
    return message_text
