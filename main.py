import os
import requests
from dotenv import load_dotenv

def send_slack_reminder():
    load_dotenv()
    slack_webhook_url = os.environ.get("SLACK_WEBHOOK_URL")
    if not slack_webhook_url:
        raise ValueError("SLACK_WEBHOOK_URL이 설정되지 않았습니다.")

    message = {
        "text": "QA 테스트 종료 여부를 확인해주세요."
    }
    response = requests.post(slack_webhook_url, json=message)

    if response.status_code == 200:
        print("Slack 메시지 전송 성공")
    else:
        print("Slack 메시지 전송 실패", response.status_code, response.text)

if __name__ == "__main__":
    send_slack_reminder()