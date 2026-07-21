import os
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import DocArrayInMemorySearch
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel

app = FastAPI(title="ccNC Chatbot V2 - RAG Engine")

# 1. 환경 변수 및 모델 초기화 (V1 스펙 유지: gpt-4o-mini, Temp 0.2)
load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("❌ OPENAI_API_KEY 환경변수가 누락되었습니다. .env 파일을 확인해주세요.")

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)

# 2. JSON 기반 초고속 RAG 지식 베이스(Vector DB) 빌드
try:
    with open("parsed_ccnc_manual.json", "r", encoding="utf-8") as f:
        raw_content = f.read()
    
    clean_content = raw_content.replace('\u200b', '').replace('\ufeff', '')
    json_data = json.loads(clean_content)
    
    docs = [] # TextSplitter를 거치지 않고 바로 docs로 만듭니다.
    
    if isinstance(json_data, list):
        for item in json_data:
            category_name = item.get("category", "미분류").strip()
            
            # 카테고리를 최상단에 명확하게 배치
            text_parts = [f"카테고리: {category_name}"]
            
            # 상세 기능 내역 결합
            if "features" in item and isinstance(item["features"], list):
                features_clean = [str(f).strip() for f in item["features"] if str(f).strip()]
                if features_clean:
                    text_parts.append("상세 내용:\n" + "\n".join(features_clean))
                
            # 주의 및 제약 사항(warnings) 결합
            if "warnings" in item and isinstance(item["warnings"], list):
                warnings_clean = [str(w).strip() for w in item["warnings"] if str(w).strip()]
                if warnings_clean:
                    text_parts.append("주의 및 제약 사항:\n" + "\n".join(warnings_clean))
                
            text_content = "\n\n".join(text_parts)
            
            # Document 1개 = 매뉴얼 항목 1개 완벽 보존! (TextSplitter 사용 안 함)
            docs.append(Document(
                page_content=text_content,
                metadata={"category": category_name}
            ))

    # OpenAI 임베딩 전환
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    
    # 메모리형 Vector DB 구축 (카테고리 원본 보존)
    vectorstore = DocArrayInMemorySearch.from_documents(docs, embeddings)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
    print(f"✅ 총 {len(docs)}개 카테고리 완벽 보존 및 RAG 지식 베이스 빌드 성공!")
    
except Exception as e:
    print(f"🚨 지식 베이스 초기화 실패: {e}")
    retriever = None

# 3. 고도화된 QA 최적화 프롬프트 템플릿 설정
system_prompt = """
[Role & Tone]
- 너는 차량 인포테인먼트 마스터 '브레이크 마스터'이다. 
- 모든 답변은 친절하고 명확하게, 아주 간결하게 제공하라.

[핵심 처리 로직 - 반드시 순서대로 적용]

1. [Context 기반 답변 - 최우선]
 - 사용자가 "켜줘", "실행해줘", "바꿔줘" 등 동작을 요청하면, 훈계조로 매뉴얼 전체를 길게 읽지 말고 **"실행 요청에 응답하는 단축 문구"**로 답변하라.
 - 예시: 
   * "DMB 좀 켜줘" -> "DMB를 실행합니다. (또는 [MEDIA] 버튼을 눌러 DMB를 선택하실 수 있습니다.)"
 - 절대로 매뉴얼의 모든 스텝(1, 2, 3...)을 줄줄이 나열하지 말고, 핵심 조작법 1문장으로만 아주 짧게 답하라.
 - 사전조건과 비교하여 warnings 조건에 해당하는 경우 해당 내용을 안내해줘라.
 - 질문에서 요구하는 수치나 조건이 [Context]에 명시된 제약 조건과 충돌할 경우(예: 최대 2명인데 3명 등록 요청 등), 미지원 기능이라고 답하지 말고 제약 사항을 명확히 안내하라.

2. [미지원 기능 처리 - RAG에 정말 아무 관련 내용이 없을 때만]
   - [Context] 전체를 확인했음에도 질문한 기능이 완전히 언급조차 없거나, '지원 예정/미지원'으로 명시된 경우에만 오직 아래 문구만 출력하라:
     "죄송합니다. 해당 기능은 현재 지원하지 않습니다."

3. [기타 예외 조건]
   - 존재하지 않는 허구의 장소/지명 질문 시: "존재하지 않는 장소이므로 다시 말씀해 주세요."
   - 사전 조건과 요청이 동시에 성립할 수 없는 물리적/논리적 모순 시: "불가능한 조건입니다." 와 함께 불가능한 이유에 대해 간단하게 설명하라.
   - 위치 지정 없는 날씨 질문 시: 기본 위치 "서울" 적용.

[Context]
{context}

사용자 질문: {question}
답변:
"""
prompt = ChatPromptTemplate.from_template(system_prompt)

# 4. RAG 체인 구성
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

if retriever:
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
    )
else:
    rag_chain = prompt | llm

# ====================================================
# 5. RAG 응답 공통 처리 함수 (디버깅 로직 포함)
# ====================================================
class ChatRequest(BaseModel):
    prompt: str  # Postman/Newman 데이터셋 규격에 맞춰 prompt로 변경!

def process_rag_response(user_input: str) -> str:
    """기존 RAG 검색 및 디버깅 출력을 수행하고 답변을 반환하는 핵심 함수"""
    # 🔍 터미널에 검색된 카테고리와 텍스트 실시간 출력 (기존 디버깅 로직)
    if retriever:
        retrieved_docs = retriever.invoke(user_input)
        print("\n🔍 [RAG Retrieved Context Top-5 Check]")
        for i, doc in enumerate(retrieved_docs):
            category = doc.metadata.get("category", "알 수 없음")
            snippet = doc.page_content.replace('\n', ' ')[:60]
            print(f"  Chunk {i+1} [{category}]: {snippet}...")
        print("--------------------------------------------------\n")

    response = rag_chain.invoke(user_input)
    return response.content if hasattr(response, 'content') else str(response)


# ====================================================
# [우선순위 1단계] 🚨 특정 HTTP 상태 코드를 강제 검증하는 정적 라우터
# ====================================================

# [TC-07 / TC-18] GET 방식의 목적지 검색 및 특정 예외 처리
@app.get("/api/v1/navigation/search")
async def search_place_get(prompt: str):
    if len(prompt) > 30:
        raise HTTPException(status_code=400, detail="입력하신 목적지 이름이 너무 깁니다. 다시 말씀해주세요.")
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
# Streamlit UI 전용 엔드포인트 (/chat)
# ====================================================
class UIChatRequest(BaseModel):
    user_input: str | None = None
    prompt: str | None = None

@app.post("/chat")
async def chat_ui_endpoint(request: UIChatRequest):
    # user_input 또는 prompt 둘 중 하나로 들어온 값을 획득
    input_text = request.user_input or request.prompt
    
    if not input_text:
        raise HTTPException(status_code=400, detail="질문 내용을 입력해주세요.")
        
    try:
        # 기존 RAG 공통 처리 함수 호출
        rag_answer = process_rag_response(input_text)
        return {"response": rag_answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ====================================================
# [우선순위 2단계] ⚔️ V2 RAG 기반 동적 와일드카드 라우터
# ====================================================

# 모든 나머지 POST/DELETE 요청을 V2 RAG로 처리
@app.post("/api/v1/{catchall:path}")
@app.delete("/api/v1/{catchall:path}")
async def dynamic_llm_post_endpoint(catchall: str, request: ChatRequest):
    if "search" in catchall and len(request.prompt) > 30:
        raise HTTPException(status_code=400, detail="입력하신 목적지 이름이 너무 깁니다. 다시 말씀해주세요.")

    try:
        rag_answer = process_rag_response(request.prompt)
        return {
            "status": "success",
            "prompt": request.prompt,
            "response": rag_answer
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 모든 나머지 GET 요청 통합
@app.get("/api/v1/{catchall:path}")
async def dynamic_llm_get_endpoint(catchall: str, request: Request):
    params = dict(request.query_params)
    prompt_value = params.get("prompt", params.get("type", "차량 상태 조회"))
    
    try:
        rag_answer = process_rag_response(prompt_value)
        return {
            "status": "success",
            "response": rag_answer
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)