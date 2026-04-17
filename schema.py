from pydantic import BaseModel, Field, ConfigDict, EmailStr
from datetime import date, time

class HealthRecordCreateRequest(BaseModel):
    #id: int = Field()
    #user_id:int = Field(...)
    record_date:date = Field(..., examples=["2026-01-01"])
    wake_up_time:time = Field(..., examples= ["10:00"])
    sleep_hours:float = Field(..., ge=0, le=24)
    steps:int = Field(..., ge=0)
    calories_burned :int= Field(..., ge=0)
    water_intake_ml:int = Field(..., ge=0)
    study_hours:float = Field(..., ge=0, le=24)
    memo:str|None = Field(default=None)

class HealthRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True) #sqlalchemy orm 객체를 pydantic으로 변환해서 읽음
    id: int 
    user_id:int 
    record_date:date 
    wake_up_time:time 
    sleep_hours:float 
    steps:int 
    calories_burned :int
    water_intake_ml:int 
    study_hours:float 
    memo:str|None 

class HealthRecordUpdateRequest(BaseModel):
    #id: int = Field()
    #user_id:int|None = Field(default=None)
    #record_date:date|None = Field(default=None)
    wake_up_time:time|None = Field(default =None, examples= ["10:00"])
    sleep_hours:float|None = Field(default=None, ge=0, le=24)
    steps:int|None = Field(default=None, ge=0)
    calories_burned :int|None = Field(default=None, ge=0)
    water_intake_ml:int|None = Field(default=None, ge=0)
    study_hours:float|None = Field(default=None, ge=0, le=24)
    memo:str|None = Field(default=None)

class HealthRecordReplaceRequest(BaseModel):
    #id: int = Field()
    #user_id:int = Field(...)
    #record_date:date = Field(...,examples=["2026-01-01"])
    wake_up_time:time = Field(..., examples= ["10:00"])
    sleep_hours:float = Field(..., ge=0, le=24)
    steps:int = Field(..., ge=0)
    calories_burned :int= Field(..., ge=0)
    water_intake_ml:int = Field(..., ge=0)
    study_hours:float = Field(..., ge=0, le=24)
    memo:str|None = Field(default=None)

class UserCreateRequest(BaseModel):
    hashed_password: str = Field(...,min_length=4)
    user_name: str = Field(..., min_length=2)
    email:EmailStr = Field(...)
    role:str = Field(default="user")

class Token(BaseModel):
    access_token : str
    token_type: str

class Predict(BaseModel):
    wake_up_time:time = Field(..., examples= ["10:00"])
    sleep_hours:float = Field(..., ge=0, le=24)
    steps:int = Field(..., ge=0)
    calories_burned :int= Field(..., ge=0)
    water_intake_ml:int = Field(..., ge=0)
    study_hours:float = Field(..., ge=0, le=24)
