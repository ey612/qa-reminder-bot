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


if __name__ == "__main__":
    channel_id = get_channel_id()
    print("qa-test 채널 ID 조회 성공")