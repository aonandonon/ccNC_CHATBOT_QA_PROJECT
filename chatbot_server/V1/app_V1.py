from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import openai
import os
from dotenv import load_dotenv

# 1. 환경변수 로드 및 앱 초기화
load_dotenv()
app = FastAPI(title="ccNC QA Backend Server Verified")

# 2. OpenAI 클라이언트 설정
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("❌ OPENAI_API_KEY 환경변수가 누락되었습니다.")

client = openai.OpenAI(api_key=openai_api_key)

class ChatRequest(BaseModel):
    prompt: str
    session_id: str = "default_session"

# ====================================================
# [우선순위 1단계] 🚨 특정 HTTP 상태 코드를 강제 검증하는 정적 라우터
# ====================================================

# [TC-07 / TC-18] GET 방식의 목적지 검색 및 특정 예외 처리
@app.get("/api/v1/navigation/search")
async def search_place_get(prompt: str):
    # TC-18: 30자 초과 시 400 (Known Issue)
    if len(prompt) > 30:
        raise HTTPException(status_code=400, detail="입력하신 목적지 이름이 너무 깁니다. 다시 말씀해주세요.")
    # TC-07: 가상 장소 예외 404
    if "우주정거장" in prompt or "판교역" in prompt:
         raise HTTPException(status_code=404, detail="존재하지 않는 장소이므로 결과가 없습니다.")
    return {"status": "success", "response": f"경로 안내를 시작합니다: {prompt}"}

# [TC-12] DB 트랜잭션 에러 시뮬레이션 (DELETE 500)
@app.delete("/api/v1/user/home")
async def delete_home_favorite():
    raise HTTPException(status_code=500, detail="서버 통신이 원활하지 않아 삭제에 실패했습니다. 잠시 후 다시 시도해주세요.")

# [TC-25] 설정 페이지 미지원 기능 예외 시뮬레이션 (GET 404)
@app.get("/api/v1/navigation/settings/stock")
async def get_stock_settings():
    raise HTTPException(status_code=404, detail="현재 지원하지 않는 사양입니다.")

# [TC-31] 블루링크 만료 상태 예외 시뮬레이션 (POST 403)
@app.post("/api/v1/navigation/weather")
async def get_weather_data(request: Request):
    raise HTTPException(status_code=403, detail="블루링크 서비스 가입 시 날씨 정보 제공이 가능합니다.")


# ====================================================
# [우선순위 2단계] ⚔️ 상용 세팅(Temp 0.2) 와일드카드 유연 통합 라우터
# ====================================================

# 모든 나머지 POST/DELETE 요청을 정석 Temp 0.2 환경의 GPT로 처리
@app.post("/api/v1/{catchall:path}")
@app.delete("/api/v1/{catchall:path}")
async def dynamic_llm_post_endpoint(catchall: str, request: ChatRequest):
    
    # 💡 [교정 핵심] 오직 목적지 검색(search) 주소로 들어온 요청일 때만 30자 제한 필터를 적용합니다!
    if "search" in catchall and len(request.prompt) > 30:
        raise HTTPException(status_code=400, detail="입력하신 목적지 이름이 너무 깁니다. 다시 말씀해주세요.")

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "너는 차량 인포테인먼트(ccNC) 시스템 비서야. 사용자의 질문에 맞춰 아주 친절하고 짤막하게 한두 문장으로만 답변해줘."},
                {"role": "user", "content": request.prompt}
            ],
            temperature=0.2  # 철저한 상용 규격 세팅 유지
        )
        return {
            "status": "success",
            "prompt": request.prompt,
            "response": response.choices[0].message.content
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 모든 나머지 GET 요청 통합
@app.get("/api/v1/{catchall:path}")
async def dynamic_llm_get_endpoint(catchall: str, request: Request):
    params = dict(request.query_params)
    prompt_value = params.get("prompt", params.get("type", "차량 상태 조회"))
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "너는 차량 인포테인먼트 비서야. 하이패스 이력이나 차량 정보에 대해 친절하고 아주 간결하게 답해줘."},
                {"role": "user", "content": prompt_value}
            ],
            temperature=0.2
        )
        return {
            "status": "success",
            "response": response.choices[0].message.content
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)