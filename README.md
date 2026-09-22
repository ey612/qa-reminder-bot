# QA Reminder Bot

QA 테스트 종료 공유 누락 방지를 위한 Slack 기반 QA 업무 리마인드 자동화 프로젝트

지정된 시간에 Python 프로그램을 자동 실행하여 Slack 채널에 QA 테스트 종료 여부 확인 메시지를 전송하는 기능 구현

## Background

* QA 테스트 시작 및 종료 상태 공유가 필요한 업무 환경
* 테스트 종료 공유 누락 시 관련 구성원의 QA 진행 상태 파악 지연 가능성
* 반복적인 종료 상태 확인 및 공유 누락 방지를 위한 자동화 필요
* 실제 테스트 종료 여부를 시스템이 임의로 판단하지 않고 QA 담당자의 확인을 유도하는 방식으로 V1 범위 설정

## V2 Features

* Slack Web API를 이용한 채널 및 메시지 조회
* 대상 티켓 키워드를 이용한 Slack Parent 메시지 탐색
* Slack Thread 메시지 조회
* QA 테스트 종료 코멘트 존재 여부 확인
* 종료 코멘트가 없는 경우에만 Slack Reminder 전송
* Slack Incoming Webhook을 이용한 메시지 전송
* 환경변수를 이용한 Webhook URL 관리
* macOS `launchd`를 이용한 예약 실행
* 실행 결과 및 오류 로그 기록

전송 메시지:

QA 테스트 종료 여부를 확인해주세요.

## Tech Stack

* Python
* requests
* python-dotenv
* Slack Incoming Webhook
* macOS launchd
* Git / GitHub

## Project Structure

```text id="mpp6vw"
qa-reminder-bot/
├── main.py
├── slack_reader.py
├── .env.example
├── .gitignore
├── com.qa.reminder.plist.example
├── reminder.log
└── reminder-error.log
```

* `.env.example`: 환경변수 구성 예시
* `.gitignore`: 인증정보, 가상환경, 로그 및 로컬 설정 파일 제외
* `com.qa.reminder.plist.example`: launchd 예약 실행 설정 예시
* `.venv`: 로컬 Python 가상환경
* `main.py`: Slack Reminder 메시지 전송
* `slack_reader.py`: Slack 채널 및 Thread 조회, QA 종료 코멘트 확인
* 로그 파일: 로컬 실행 결과 기록

## Execution Flow

```text
예약 시간 도달
    ↓
macOS launchd
    ↓
Python 가상환경 실행
    ↓
slack_reader.py 실행
    ↓
Slack Web API를 이용한 대상 채널 조회
    ↓
티켓 키워드가 포함된 Parent 메시지 탐색
    ↓
해당 Thread 메시지 조회
    ↓
QA 테스트 종료 코멘트 확인
    ↓
종료 코멘트 존재 여부 판단
    ├─ 있음 → Reminder 미전송
    └─ 없음 → main.py의 Reminder 전송 함수 실행
                    ↓
             Slack Incoming Webhook
                    ↓
             Reminder 메시지 전송
```

## Environment Variables

Slack 인증정보의 코드 직접 입력 대신 환경변수를 통한 관리

```text
SLACK_WEBHOOK_URL=YOUR_SLACK_WEBHOOK_URL
SLACK_BOT_TOKEN=YOUR_SLACK_BOT_TOKEN
```

실제 `.env` 파일의 Git 저장소 제외 및 `.env.example`을 통한 환경변수 구성 예시 제공

## Test Results

V2 주요 시나리오 검증

* Slack 채널 및 대상 Parent 메시지 조회 정상 동작
* 대상 Thread 메시지 조회 정상 동작
* QA 테스트 종료 코멘트 존재 시 Reminder 미전송
* QA 테스트 종료 코멘트 미존재 시 Reminder 자동 전송
* macOS `launchd` 예약 실행 환경에서 두 조건 분기 검증
* 정상 실행 후 launchd exit code `0` 확인

최종 결과: PASS

## Future Improvements

* 요일별 QA/STG 종료 코멘트 확인 규칙 적용
* 업무 채널과 Reminder 전송 채널 분리
* 다중 티켓 조회 및 담당자별 Reminder 지원
* 종료 코멘트 작성자 Slack User ID 검증
* Jira Assignee와 Slack 사용자 매핑
* Jira API 연동을 통한 티켓 상태 및 담당자 정보 활용
