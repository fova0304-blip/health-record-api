# health-record-api

개인 건강 데이터를 기록하고 분석하는 REST API 서버입니다.  
FastAPI + SQLAlchemy(Async) + MySQL 기반으로 구현되었으며, JWT 인증, ML 기분 예측, LLM 건강 분석 기능을 포함합니다.

---

## 기술 스택

| 항목 | 내용 |
|---|---|
| Language | Python 3.11+ |
| Framework | FastAPI |
| ORM | SQLAlchemy 2.0 (Async) |
| DB | MySQL |
| DB Driver | aiomysql |
| Validation | Pydantic v2 |
| Auth | JWT (python-jose) + bcrypt |
| ML | scikit-learn (RandomForestClassifier) |
| LLM | Google Gemini API |

---

## 주요 기능

- 회원가입 / 로그인 (JWT 인증)
- 건강 기록 CRUD (로그인한 사용자 본인 데이터만 접근)
- 최근 7일 요약(summary) + LLM 분석
- 최근 N일 추세(trend) + LLM 분석
- ML 기반 기분 예측 (good/bad)

---

## 실행 방법

### 1. 패키지 설치
```bash
pip install -r requirements.txt
```

### 2. 환경변수 설정
`.env` 파일 생성 후 아래 내용 입력:

```
DATABASE_URL=mysql+aiomysql://<user>:<password>@<host>:<port>/<dbname>
SECRET_KEY=<your_secret_key>
ALGORITHM=HS256
GEMINI_API_KEY=<your_gemini_api_key>
```

### 3. 서버 실행
```bash
fastapi dev main.py
```

Swagger UI: `http://127.0.0.1:8000/docs`

---

## API 명세

### Auth

| Method | URL | 설명 |
|---|---|---|
| POST | `/auth` | 회원가입 |
| POST | `/token` | 로그인 (JWT 발급) |

### HealthRecord CRUD

| Method | URL | 설명 |
|---|---|---|
| POST | `/health-records` | 건강 기록 생성 |
| GET | `/health-records` | 전체 기록 조회 |
| GET | `/health-records/{id}` | 단건 조회 |
| PATCH | `/health-records/{id}` | 부분 수정 |
| PUT | `/health-records/{id}` | 전체 교체 |
| DELETE | `/health-records/{id}` | 삭제 |

### 분석 API

| Method | URL | 설명 |
|---|---|---|
| GET | `/summary` | 최근 7일 평균 수면 / 총 걸음 수 + LLM 분석 |
| GET | `/trend` | 최근 N일 날짜별 수면 / 걸음 추세 + LLM 분석 |
| POST | `/predict` | 특정 날짜 건강 기록 기반 기분 예측 (good/bad) |

---

## 데이터 모델

### User

| 필드 | 타입 | 설명 |
|---|---|---|
| user_id | int | PK |
| user_name | str | 유저명 (unique) |
| email | str | 이메일 (unique) |
| hashed_password | str | bcrypt 해시 비밀번호 |
| is_active | bool | 활성 여부 |
| role | str | 역할 |

### HealthRecord

| 필드 | 타입 | 설명 |
|---|---|---|
| id | int | PK |
| user_id | int | FK (users.user_id) |
| record_date | date | 기록 날짜 (user_id + date 유니크) |
| wake_up_time | time | 기상 시각 |
| sleep_hours | float | 수면 시간 (0~24) |
| steps | int | 걸음 수 |
| calories_burned | int | 소모 칼로리 |
| water_intake_ml | int | 수분 섭취량 (ml) |
| study_hours | float | 공부 시간 (0~24) |
| memo | str \| None | 메모 |

---

## 디렉토리 구조

```
health-track-api/
├── main.py          # FastAPI 앱 진입점
├── models.py        # SQLAlchemy ORM 모델
├── schema.py        # Pydantic 요청/응답 스키마
├── orm.py           # DeclarativeBase
├── connection.py    # DB 연결 및 세션
├── routers/
│   ├── auth.py      # 회원가입 / 로그인
│   └── crud.py      # HealthRecord CRUD + 분석 API
├── ml/
│   ├── DailyHabitTracker_model.joblib  # 학습된 ML 모델
│   └── health_track_api.ipynb          # 모델 학습 노트북
├── llm/
│   └── llm.py       # Gemini API 연동
├── requirements.txt
└── README.md
```

---

## 데이터 출처

- [Daily Habit Tracker Dataset — Kaggle](https://www.kaggle.com/datasets/prince7489/daily-habit-tracker-dataset)

---

## 참고

- ML 모델: RandomForestClassifier, accuracy 0.88 (binary classification: good/bad mood)
- LLM: Google Gemini 2.0 Flash
- 인증이 필요한 모든 엔드포인트는 Bearer 토큰 필요
