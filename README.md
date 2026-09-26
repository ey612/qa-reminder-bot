# QA Reminder Bot

Slack 스레드의 QA 테스트 종료 댓글을 확인하고, 종료 공유가 누락된 티켓을 요약하여 알림을 보내는 Python 기반 QA 업무 자동화 프로젝트입니다.

## Background

QA 업무에서는 여러 티켓의 테스트 진행 상태와 종료 여부를 확인해야 합니다. 종료 댓글이 누락되면 관련 구성원이 QA 진행 상태를 파악하기 어려워지고, 담당자가 반복적으로 Slack 스레드를 확인해야 합니다.

이 프로젝트는 QA 담당자가 작성한 종료 댓글을 기준으로 공유 누락 여부를 확인하고, 확인이 필요한 티켓만 알림으로 전달하기 위해 개발했습니다. 실제 테스트 완료 여부를 시스템이 임의로 판단하지 않고, Slack에 기록된 종료 공유 상태를 확인하는 데 범위를 두었습니다.

## Features

- 환경변수에 설정한 여러 QA 티켓을 한 번에 확인
- Slack Web API를 이용해 티켓 키가 포함된 상위 메시지 탐색
- 각 티켓의 Slack 스레드에서 `테스트 종료` 댓글 확인
- 종료 댓글이 없는 티켓과 상위 메시지를 찾지 못한 티켓 구분
- 확인이 필요한 티켓이 있을 때 하나의 요약 메시지로 Slack 알림 전송
- 모든 대상 티켓의 종료 댓글이 확인되면 알림 미전송
- 봇이 전송한 이전 알림을 티켓의 상위 메시지로 잘못 인식하지 않도록 제외
- macOS `launchd`를 이용한 예약 실행 및 로그 기록

## Tech Stack

- Python
- requests
- python-dotenv
- Slack Web API
- Slack Incoming Webhook
- macOS launchd
- Git / GitHub

## Project Structure

```text
qa-reminder-bot/
├── main.py
├── slack_reader.py
├── .env.example
├── .gitignore
├── com.qa.reminder.plist.example
└── README.md
```

- `main.py`: 대상 티켓의 QA 종료 상태를 확인하고 필요한 경우 요약 알림 전송
- `slack_reader.py`: Slack 채널 및 스레드 조회, 티켓 상위 메시지 탐색, 종료 댓글 확인
- `.env.example`: 환경변수 설정 예시
- `.gitignore`: 인증정보, 가상환경, 로그 및 로컬 설정 파일의 Git 추적 제외
- `com.qa.reminder.plist.example`: macOS 예약 실행 설정 예시

실제 `.env`, 실행용 `.plist`, 가상환경 및 로그 파일은 로컬 환경에서 관리합니다.

## Execution Flow

```text
launchd 예약 시간 도달
        ↓
main.py 실행
        ↓
환경변수에서 대상 티켓 키 목록 로드
        ↓
Slack 채널에서 각 티켓의 상위 메시지 탐색
        ↓
각 티켓의 스레드 조회
        ↓
"테스트 종료" 댓글 확인
        ↓
티켓별 결과 분류
        ├─ 종료 댓글 확인
        ├─ 종료 댓글 없음
        └─ 상위 메시지를 찾지 못함
        ↓
확인이 필요한 티켓 존재 여부 판단
        ├─ 없음 → 알림 미전송
        └─ 있음 → 요약 메시지 한 번 전송
```

## Environment Variables

Slack 인증정보와 대상 티켓 목록은 코드에 직접 입력하지 않고 `.env` 파일로 관리합니다.

```dotenv
SLACK_WEBHOOK_URL=YOUR_SLACK_WEBHOOK_URL
SLACK_BOT_TOKEN=YOUR_SLACK_BOT_TOKEN
QA_TICKET_KEYS=CHAE-0001,CHAE-0002,CHAE-0003
```

실제 `.env` 파일은 Git 저장소에서 제외합니다. Slack 채널을 지정하는 환경변수 등 추가 설정은 로컬 환경에 맞게 구성합니다.

## Test Results

다음 시나리오를 직접 검증했습니다.

| 테스트 시나리오 | 기대 결과 | 결과 |
| --- | --- | --- |
| 대상 티켓의 상위 메시지 및 스레드 조회 | 해당 티켓의 댓글 조회 | PASS |
| `테스트 종료` 댓글이 있는 티켓 | 종료 확인 대상으로 분류 | PASS |
| 종료 댓글이 없는 티켓 | 알림 대상에 포함 | PASS |
| 여러 티켓에 확인이 필요한 항목이 있는 경우 | 요약 알림 한 번 전송 | PASS |
| 모든 대상 티켓의 종료 댓글이 확인된 경우 | 알림 미전송 | PASS |
| 봇의 이전 알림에 티켓 키가 포함된 경우 | 실제 티켓 상위 메시지로 오인하지 않음 | PASS |
| `launchd` 예약 시간 도달 | `main.py` 자동 실행 및 상태 확인 | PASS |

예약 실행 테스트에서는 지정한 시간에 프로그램이 자동 실행되어 QA 종료 상태를 확인했고, 모든 대상 티켓의 종료 댓글이 확인되어 알림을 보내지 않는 정상 동작을 로그로 확인했습니다.

## Future Improvements

- Jira API 연동을 통한 QA 대상 티켓 자동 조회
- Jira 담당자 및 티켓 상태를 기준으로 조회 조건 구성
- Jira 담당자와 Slack 사용자 매핑
- 종료 댓글 작성자의 Slack User ID 검증
- 요일 또는 QA/STG 단계에 따른 종료 확인 규칙 확장
