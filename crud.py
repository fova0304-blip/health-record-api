from fastapi import FastAPI, HTTPException, Depends
from connection import get_async_session
from schema import HealthRecordCreateRequest, HealthRecordReplaceRequest, HealthRecordUpdateRequest,HealthRecordResponse
from models import HealthRecord
from sqlalchemy import select, func
from datetime import date, timedelta

app = FastAPI()

@app.post("/health-records", response_model=HealthRecordResponse)
async def health_records_create_api(
    body:HealthRecordCreateRequest, session = Depends(get_async_session)
):
    health_records = HealthRecord(
        user_id = body.user_id,
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

async def get_health_records_or_404(session, id):
    stmt = select(HealthRecord).where(HealthRecord.id == id)
    result = await session.execute(stmt)
    health_records = result.scalar()
    if health_records is None:
        raise HTTPException(status_code=404, detail=f"{id} not found")
    return health_records

@app.get("/health-records/{id}", response_model=HealthRecordResponse)
async def health_records_get_one_api(
    id:int, session = Depends(get_async_session)
):
    health_records = await get_health_records_or_404(session, id)
    return health_records

@app.get("/health-records", response_model=list[HealthRecordResponse])
async def health_records_get_all_api(
    user_id:int, session= Depends(get_async_session)
):
    stmt = select(HealthRecord).where(HealthRecord.user_id == user_id)
    result = await session.execute(stmt)
    health_records = result.scalars().all()
    return health_records


@app.patch("/health-records/{id}", response_model=HealthRecordResponse)
async def health_records_update_api(
    body: HealthRecordUpdateRequest, id:int, session= Depends(get_async_session)
):
    health_records = await get_health_records_or_404(session, id)
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

@app.put("/health-records/{id}", response_model=HealthRecordResponse)
async def health_records_replace_api(
    body:HealthRecordReplaceRequest, id:int, session = Depends(get_async_session)
):
    health_records = await get_health_records_or_404(session,id)
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

@app.delete("/health-records/{id}", status_code=204)
async def health_records_delete_api(
    id:int, session = Depends(get_async_session)
):
    health_records = await get_health_records_or_404(session,id)
    await session.delete(health_records)
    await session.commit()

#최근 7일을 요약한 숫자- summary
#from datetime import date, timedelta
#최근 7일 평균 수면 시간, 최근 7일 총 걸음 수
@app.get("/summary/{user_id}")
async def health_records_summary_api(
   user_id:int, session=Depends(get_async_session)
):
    seven_days_ago = date.today() - timedelta(7)
    sleep_hour = select(func.avg(HealthRecord.sleep_hours)).where(HealthRecord.record_date >= seven_days_ago
                                                                  ,HealthRecord.user_id == user_id)
    sleep_result = await session.execute(sleep_hour)
    avg_sleep_hour = sleep_result.scalar()

    steps = select(func.sum(HealthRecord.steps)).where(HealthRecord.record_date >= seven_days_ago,HealthRecord.user_id == user_id)
    step_result = await session.execute(steps)
    total_steps = step_result.scalar()

    return {
        "average amount of sleep for 7 days": avg_sleep_hour,
        "total amount of steps for 7 days" : total_steps
    }


    
    




#trend, 시간 흐름에 따른 값의 변화- 날짜별 데이터 다 보여줌

