import os 
from google import genai

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
model="gemini-2.5-flash"

#model = genai.GenerativeModel("gemini-1.5-flash")

def get_llm_response_summary(summary:dict)->str:
    prompt = f"""
        사용자의 최근 7일 건강 데이터:
        7일 평균 수면량: {summary["avg_sleep_hours_7ds"]},
        7일 총 걸음량: {summary["total_steps_7"]}

        데이터를 기반으로 요약 및 조언을 해주세요
    """
    response = client.models.generate_content(
        model=model,
        contents=prompt
    )
    return response.text

def get_llm_response_trend(trend:str)->str:
    prompt = f"""
        사용자의 최근 날짜별 건강 데이터:
        날짜/수면 시간/걸음량: {str(trend)}

        데이터를 기반으로 요약 및 조언을 해주세요
    """

    response = client.models.generate_content(
        model=model,
        contents=prompt
    )
    return response.text

    

