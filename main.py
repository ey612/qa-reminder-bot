import os
import requests
from dotenv import load_dotenv
from slack_reader import check_qa_end_comment

def send_slack_reminder(message_text):
    load_dotenv()
    slack_webhook_url = os.environ.get("SLACK_WEBHOOK_URL")
    if not slack_webhook_url:
        raise ValueError("SLACK_WEBHOOK_URL이 설정되지 않았습니다.")

    message = {
        "text": message_text
    }
    response = requests.post(slack_webhook_url, json=message)

    if response.status_code == 200:
        print("Slack 메시지 전송 성공")
    else:
        print("Slack 메시지 전송 실패", response.status_code, response.text)

if __name__ == "__main__":
    message_text = check_qa_end_comment()

    if message_text:
        send_slack_reminder(message_text)