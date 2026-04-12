from orm import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, Date, Time, Float, UniqueConstraint, String
from datetime import date,time

class HealthRecord(Base):
    __tablename__ = 'health_records'

    __table_args__ = (
        UniqueConstraint("user_id", "record_date"), #하루에 하나씩만 만들기
    )

    id : Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, index=True)
    record_date:Mapped[date] = mapped_column(Date, index=True)
    wake_up_time :Mapped[time] = mapped_column(Time)
    sleep_hours: Mapped[float] = mapped_column(Float)
    steps : Mapped[int] = mapped_column(Integer)
    calories_burned:Mapped[int] = mapped_column(Integer)
    water_intake_ml:Mapped[int] = mapped_column(Integer)
    study_hours: Mapped[float] = mapped_column(Float)
    memo:Mapped[str] = mapped_column(String(128), nullable=True)
    #mood_score: Mapped[int] = mapped_column(Integer)