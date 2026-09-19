# QA Reminder Bot

QA 테스트 종료 공유 누락 방지를 위한 Slack 기반 QA 업무 리마인드 자동화 프로젝트

지정된 시간에 Python 프로그램을 자동 실행하여 Slack 채널에 QA 테스트 종료 여부 확인 메시지를 전송하는 기능 구현

## Background

* QA 테스트 시작 및 종료 상태 공유가 필요한 업무 환경
* 테스트 종료 공유 누락 시 관련 구성원의 QA 진행 상태 파악 지연 가능성
* 반복적인 종료 상태 확인 및 공유 누락 방지를 위한 자동화 필요
* 실제 테스트 종료 여부를 시스템이 임의로 판단하지 않고 QA 담당자의 확인을 유도하는 방식으로 V1 범위 설정

## V1 Features

* Slack Incoming Webhook을 이용한 메시지 전송
* 환경변수를 이용한 Webhook URL 관리
* Slack API 요청 결과 확인
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
├── .env
├── .gitignore
├── com.qa.reminder.plist
├── reminder.log
└── reminder-error.log
```

`.env`, 가상환경, 로그 파일 및 실제 launchd 설정 파일의 Git 저장소 제외

* `.env`: Slack Webhook URL 등 환경변수 관리
* `.venv`: 로컬 Python 가상환경
* 로그 파일: 로컬 실행 결과 기록
* 실제 plist: 사용자별 절대경로 등 로컬 환경 정보 포함

## Execution Flow

```text id="5uslyj"
예약 시간 도달
    ↓
macOS launchd
    ↓
Python 가상환경 실행
    ↓
main.py 실행
    ↓
.env에서 Slack Webhook URL 로드
    ↓
Slack Incoming Webhook으로 HTTP POST 요청
    ↓
Slack 리마인드 메시지 전송
```

## Environment Variables

Slack Webhook URL의 코드 직접 입력 대신 환경변수를 통한 관리

```text id="ukrprj"
SLACK_WEBHOOK_URL=YOUR_SLACK_WEBHOOK_URL
```

실제 `.env` 파일의 Git 저장소 제외

## Test Results

V1 주요 시나리오 검증

* Python 스크립트 직접 실행 시 Slack 메시지 정상 전송
* launchd를 통한 수동 실행 시 Slack 메시지 정상 전송
* 지정된 예약 시간에 별도 조작 없이 Slack 메시지 자동 전송
* 정상 실행 후 launchd exit code `0` 확인

최종 결과: PASS

## Troubleshooting

### 현상

* launchd 예약 시간 도달 후 Slack 메시지 미전송
* 초기 확인 시 실행 및 오류 로그 미생성

### 원인 분석

* `launchctl` 실행 상태 확인
* `EX_CONFIG (78)` 확인
* 실제 등록된 `ProgramArguments` 점검
* Python 실행 파일과 `main.py` 경로의 잘못된 구성 확인

### 해결

* Python 실행 파일과 실행 대상 스크립트 경로 분리
* plist 수정 후 문법 및 실제 등록 설정 재확인
* launchd 수동 실행을 통한 정상 동작 확인
* 예약 실행 E2E 재테스트
* Slack 메시지 정상 수신 및 exit code `0` 확인

## Future Improvements

* 공개 가능한 `.env.example` 및 launchd plist example 제공
* Slack에서 QA 종료 공유 여부 확인
* 종료 공유가 없는 경우에만 리마인드 전송
* Slack 스레드 자동 탐색
* Jira 연동 검토
