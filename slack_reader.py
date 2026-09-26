import os
import requests
from dotenv import load_dotenv
from main import send_slack_reminder

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

    print(f"종료 댓글이 없는 티켓: {missing_tickets}")
    print(f"스레드를 찾지 못한 티켓: {not_found_tickets}")


if __name__ == "__main__":
    check_qa_end_comment()