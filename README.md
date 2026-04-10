# health-record-api

개인 건강 데이터를 기록하고 분석하는 REST API 서버입니다.  
FastAPI + SQLAlchemy(Async) + MySQL 기반으로 구현하며, 단계적으로 ML inference와 LLM 요약 기능을 추가합니다.

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

---

## 프로젝트 로드맵

### Stage 2 — HealthRecord CRUD + 집계 API (현재)
- HealthRecord 테이블 설계 및 CRUD 구현
- user_id 기준 개인화 조회
- 최근 7일 요약(summary) API
- 최근 N일 추세(trend) API

### Stage 3 — ML + LLM 연결
- ML endpoint: 최근 N일 데이터 기반 risk score 예측
- Ollama endpoint: summary/trend/ML 결과를 자연어로 설명

### Stage 4 — 운영형 확장
- users 테이블 + 인증(auth/login)
- Docker, Redis, 백그라운드 태스크
- 환경 분리, 로깅, 예외 처리 고도화

---

## 실행 방법

### 1. 패키지 설치
```bash
pip install -r requirements.txt
```

### 2. DB 설정
`connection.py`의 `DATABASE_URL`을 본인 MySQL 환경에 맞게 수정합니다.

```python
DATABASE_URL = "mysql+aiomysql://<user>:<password>@<host>:<port>/<dbname>"
```

### 3. 테이블 생성
```bash
python orm.py
```

### 4. 서버 실행
```bash
uvicorn crud:app --reload
```

Swagger UI: `http://127.0.0.1:8000/docs`

---

## API 명세 (Stage 2)

### HealthRecord CRUD

| Method | URL | 설명 |
|---|---|---|
| POST | `/health-records` | 건강 기록 생성 |
| GET | `/health-records` | 전체 기록 조회 (user_id 필터) |
| GET | `/health-records/{id}` | 단건 조회 |
| PATCH | `/health-records/{id}` | 부분 수정 |
| PUT | `/health-records/{id}` | 전체 교체 |
| DELETE | `/health-records/{id}` | 삭제 |

### 집계 API (구현 예정)

| Method | URL | 설명 |
|---|---|---|
| GET | `/health-records/summary` | 최근 7일 평균 수면 / 총 운동량 |
| GET | `/health-records/trend` | 최근 N일 sleep / study 추세 |

---

## 데이터 모델

### HealthRecord

| 필드 | 타입 | 설명 |
|---|---|---|
| id | int | PK |
| user_id | int | 사용자 식별자 (로그인 없이 ID로 구분) |
| record_date | date | 기록 날짜 (user_id + date 유니크) |
| wake_up_time | time | 기상 시각 |
| sleep_hours | float | 수면 시간 (0~24) |
| steps | int | 걸음 수 |
| calories_burned | int | 소모 칼로리 |
| water_intake_ml | int | 수분 섭취량 (ml) |
| study_hours | float | 공부 시간 (0~24) |
| memo | str \| None | 메모 |

---

## 검증 항목 (Swagger / Postman 기준)

- [ ] POST → 201 정상 생성
- [ ] POST 중복 날짜 → 500 (IntegrityError 처리 예정)
- [ ] GET /{id} 존재 → 200
- [ ] GET /{id} 없음 → 404
- [ ] GET ?user_id= → 목록 반환
- [ ] PATCH → 변경 필드만 수정
- [ ] PUT → 전체 교체
- [ ] DELETE → 204
- [ ] 잘못된 타입 요청 → 422

---

## 디렉토리 구조

```
health-record-api/
├── crud.py          # FastAPI 앱 + 라우터 (main.py로 이동 예정)
├── models.py        # SQLAlchemy ORM 모델
├── schema.py        # Pydantic 요청/응답 스키마
├── orm.py           # Base 및 테이블 생성
├── connection.py    # DB 연결 설정
├── requirements.txt
└── README.md
```

---

## 데이터 출처

- [Daily Habit Tracker Dataset — Kaggle](https://www.kaggle.com/datasets/prince7489/daily-habit-tracker-dataset)

---

## 참고

- AI는 코드 리뷰 / 에러 해석 / 설계 점검 용도로만 사용
- 구현은 직접 작성 후 Swagger로 실행 검증 필수
- Stage 2 완료 기준: CRUD 6개 + summary + trend 모두 Swagger에서 동작 확인
