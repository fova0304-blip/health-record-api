from fastapi import APIRouter, HTTPException, Depends, Query
from connection import get_async_session
from schema import HealthRecordCreateRequest, HealthRecordReplaceRequest, HealthRecordUpdateRequest,HealthRecordResponse, Predict
from models import HealthRecord
from sqlalchemy import select, func
from datetime import date, timedelta
from .auth import get_current_user
import joblib
from llm.llm import get_llm_response_summary, get_llm_response_trend


router = APIRouter()

model = joblib.load("./ml/DailyHabitTracker_model.joblib")

def predict_mood(body: Predict):
    data=[
        body.wake_up_time.hour * 60 + body.wake_up_time.minute,
        body.sleep_hours,
        body.steps,
        body.calories_burned,
        body.water_intake_ml,
        body.study_hours
    ]
    result = model.predict([data])
    return result[0]

@router.post("/predict")
async def predict_mood_api(
    record_date:date,
    session= Depends(get_async_session),
    current_user = Depends(get_current_user),
):
    statement = select(HealthRecord).where(HealthRecord.user_id == current_user.user_id, HealthRecord.record_date == record_date)
    result = await session.execute(statement)
    health_records = result.scalars().first()
    predict_input = Predict(
        wake_up_time = health_records.wake_up_time,
        sleep_hours = health_records.sleep_hours,
        steps = health_records.steps,
        calories_burned = health_records.calories_burned,
        water_intake_ml = health_records.water_intake_ml,
        study_hours = health_records.study_hours
    )
    predict_result = predict_mood(predict_input)
    mood = None
    if predict_result == 1:
        mood = "good"
    if predict_result == 0:
        mood = "bad"
    return {"predicted_user_mood": mood}
    

@router.post("/health-records", response_model=HealthRecordResponse)
async def health_records_create_api(
    body:HealthRecordCreateRequest, session = Depends(get_async_session),
    current_user = Depends(get_current_user)
):
    health_records = HealthRecord(
        user_id = current_user.user_id,
        record_date = body.record_date,
        wake_up_time = body.wake_up_time,
        sleep_hours = body.sleep_hours,
        steps = body.steps,
        calories_burned = body.calories_burned,
        water_intake_ml = body.water_intake_ml,
        study_hours = body.study_hours,
        memo = body.memo
    )
    session.add(health_records)
    await session.commit()
    await session.refresh(health_records)
    return health_records

async def get_health_records_or_404(session, id, user_id):
    stmt = select(HealthRecord).where(HealthRecord.id == id, HealthRecord.user_id == user_id)
    result = await session.execute(stmt)
    health_records = result.scalar()
    if health_records is None:
        raise HTTPException(status_code=404, detail=f"{id} not found")
    return health_records

@router.get("/health-records/{id}", response_model=HealthRecordResponse)
async def health_records_get_one_api(
    id:int, session = Depends(get_async_session),
    current_user = Depends(get_current_user)
):
    health_records = await get_health_records_or_404(session,id, current_user.user_id)
    return health_records

@router.get("/health-records", response_model=list[HealthRecordResponse])
async def health_records_get_all_api(
    session= Depends(get_async_session),
    current_user = Depends(get_current_user)
):
    stmt = select(HealthRecord).where(HealthRecord.user_id == current_user.user_id)
    result = await session.execute(stmt)
    health_records = result.scalars().all()
    return health_records


@router.patch("/health-records/{id}", response_model=HealthRecordResponse)
async def health_records_update_api(
    body: HealthRecordUpdateRequest, id:int, session= Depends(get_async_session),
    current_user = Depends(get_current_user)
):
    health_records = await get_health_records_or_404(session, id, current_user.user_id)
    if body.wake_up_time is not None:
        health_records.wake_up_time = body.wake_up_time
    if body.sleep_hours is not None:
        health_records.sleep_hours = body.sleep_hours
    if body.steps is not None:
        health_records.steps = body.steps
    if body.calories_burned is not None:
        health_records.calories_burned = body.calories_burned
    if body.water_intake_ml is not None:
        health_records.water_intake_ml = body.water_intake_ml
    if body.study_hours is not None:
        health_records.study_hours = body.study_hours
    if body.memo is not None:
        health_records.memo = body.memo
    await session.commit()
    await session.refresh(health_records)
    return health_records

@router.put("/health-records/{id}", response_model=HealthRecordResponse)
async def health_records_replace_api(
    body:HealthRecordReplaceRequest, id:int, session = Depends(get_async_session),
    current_user= Depends(get_current_user)
):
    health_records = await get_health_records_or_404(session,id,current_user.user_id)
    health_records.wake_up_time = body.wake_up_time
    health_records.sleep_hours = body.sleep_hours
    health_records.steps = body.steps
    health_records.calories_burned = body.calories_burned
    health_records.water_intake_ml = body.water_intake_ml
    health_records.study_hours = body.study_hours
    health_records.memo = body.memo
    await session.commit()
    await session.refresh(health_records)
    return health_records

@router.delete("/health-records/{id}", status_code=204)
async def health_records_delete_api(
    id:int, session = Depends(get_async_session),
    current_user = Depends(get_current_user)
):
    health_records = await get_health_records_or_404(session,id, current_user.user_id)
    await session.delete(health_records)
    await session.commit()

#최근 7일을 요약한 숫자- summary
#from datetime import date, timedelta
#최근 7일 평균 수면 시간, 최근 7일 총 걸음 수
@router.get("/summary")
async def health_records_summary_api(
   session=Depends(get_async_session),
   current_user = Depends(get_current_user)
):
    seven_days_ago = date.today() - timedelta(days=7)
    sleep_hour = select(func.avg(HealthRecord.sleep_hours)).where(HealthRecord.record_date >= seven_days_ago
                                                                  ,HealthRecord.user_id == current_user.user_id)
    sleep_result = await session.execute(sleep_hour)
    avg_sleep_hour = sleep_result.scalar()

    steps = select(func.sum(HealthRecord.steps)).where(HealthRecord.record_date >= seven_days_ago,HealthRecord.user_id == current_user.user_id)
    step_result = await session.execute(steps)
    total_steps = step_result.scalar()

    return {
        "avg_sleep_hours_7ds": avg_sleep_hour,
        "total_steps_7" : total_steps,
        "summary_response": get_llm_response_summary({"avg_sleep_hours_7ds": avg_sleep_hour,
                                                      "total_steps_7" : total_steps})
    }


#trend, 시간 흐름에 따른 값의 변화- 날짜별 데이터 다 보여줌
@router.get("/trend")
async def health_records_trend_api(
    n:int=Query(default=7,ge=1), 
    session = Depends(get_async_session),
    current_user = Depends(get_current_user)
):
    n_days_ago = date.today() - timedelta(days=n)
    statement = select(HealthRecord.record_date, HealthRecord.sleep_hours, HealthRecord.steps).where(HealthRecord.user_id == current_user.user_id,
        HealthRecord.record_date>=n_days_ago).order_by(HealthRecord.record_date.asc())
    result = await session.execute(statement)
    health_records = result.mappings().all() #딕셔너리로 반환해야지 json으로 해석해서 llm이 읽을수있음
    return {"health_records":health_records,
            "trend_response": get_llm_response_trend(str(health_records))}