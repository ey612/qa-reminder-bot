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

    raise ValueError(
        f"'{target_keyword}' 키워드가 포함된 메시지를 찾을 수 없습니다."
    )


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
    target_keyword = "CHAE-0001"
    end_keyword = "테스트 종료"

    channel_id = get_channel_id()
    channel_history = get_channel_history(channel_id)
    parent_ts = find_parent_ts(channel_history, target_keyword)
    thread_messages = get_thread_messages(channel_id, parent_ts)

    if has_end_comment(thread_messages, end_keyword):
        print("QA 테스트 종료 댓글을 찾았습니다.")
    else:
        print("QA 테스트 종료 댓글을 찾지 못했습니다.")
        send_slack_reminder()



if __name__ == "__main__":
    check_qa_end_comment()