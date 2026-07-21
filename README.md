# 🚗 ccNC Chatbot Dashboard QA Project

> **ccNC 웹매뉴얼 챗봇의 품질 확보를 위한 시나리오 기반 QA 자동화 프레임워크**
> 
> 시스템 상태 전이 및 데이터 흐름 추적, RAG 데이터 무결성 검증, UI 결함 자동 포착 및 리포팅을 종합적으로 수행합니다.

---

## 📌 프로젝트 개요 (Overview)

본 프로젝트는 차량 인포테인먼트(ccNC) 웹매뉴얼 기반 챗봇의 응답 무결성 및 UI 상태 전이를 검증하기 위해 구축된 **End-to-End QA 자동화 프레임워크**입니다. 

* **핵심 목적**: RAG 파이프라인 응답 정확도 검증, API 통신 무결성 확보, 멀티 UI 환경 자동화 테스트
* **주요 스택**: `Python`, `FastAPI`, `LangChain`, `Playwright`, `Postman/Newman`, `Streamlit`

---

## 📂 프로젝트 구조 (Project Structure)

보안을 위해 API Key 등 민감 정보는 루트 하위 `.env.example` 템플릿으로 관리하며, V1/V2 검증 환경을 완전히 분리하여 운용합니다.

```text
ccNC_CHATBOT_QA_PROJECT/
├── chatbot_server/                 # 챗봇 백엔드 서버 및 프론트엔드 대시보드
│   ├── V1/                         # V1 버전 (Rule-based / Mock Backend)
│   │   ├── app_V1.py
│   │   └── dashboard.py
│   ├── V2/                         # V2 버전 (LangChain RAG 파이프라인 엔진)
│   │   ├── app_V2.py               # FastAPI Dual-Routing 및 RAG 엔진 백엔드
│   │   ├── dashboard_V2.py         # Streamlit V2 인터랙티브 대시보드
│   │   └── parsed_ccnc_manual.json # ccNC 웹매뉴얼 파싱 지식 베이스 (107개 HTML)
│   └── .env.example                # 중앙 환경변수 설정 템플릿 (.env로 복사 사용)
│
└── qa_automation/                  # QA 자동화 테스트 스크립트 및 검증 산출물
    ├── json_conversion.py          # Newman 결함 리포트 JSON ➡️ Excel/HTML 자동 변환 스크립트
    ├── V1/                         # V1 테스트 스크립트 및 결과 리포트
    │   ├── api_testing/            # Postman/Newman 기반 API 자동화 테스트
    │   ├── ui_testing/             # Playwright 기반 UI E2E 테스트 및 결함 캡처
    │   └── docs_and_templates/     # ccNC 웹매뉴얼 챗봇_TC_V1.xlsx
    └── V2/                         # V2 RAG 검증 스크립트 및 자동화 산출물
        ├── api_testing/            # V2 RAG 검증용 TC-01~TC-35 실행 및 Newman 리포트
        ├── ui_testing/             # Playwright V2 검증 (35개 스크린샷 & 99_final_audit_report_V2.png)
        └── docs_and_templates/     # ccNC 웹매뉴얼 챗봇_TC_V2.xlsx

## 🚀 단계별 검증 성과 & 고도화 (Milestones)
## 🔹 V1: QA 자동화 프레임워크 구축 (Foundation)
시나리오 기반 TC 설계: ccNC 웹매뉴얼 챗봇의 핵심 유저 시나리오를 바탕으로 검증 항목 및 데이터셋 문서화

API/UI 자동화 파이프라인 구축: Postman/Newman 기반 API 무결성 검증(report_V1.html) 및 Playwright 기반 UI 상태 전이 검증/결함 자동 캡처(01_TC-01.png 등) 체계 완성

## 🔹 V2: RAG 파이프라인 도입 및 질적 개선 (RAG Evaluation)
하드코딩(비즈니스 룰) 한계 극복: 기존 V1의 단순 규칙 기반(Rule-based) 응답 방식에서 벗어나, LangChain + OpenAI RAG 파이프라인을 도입하여 매뉴얼 맥락에 맞는 동적·고도화 응답 체계 구현

RAG 품질 검증 & 감사 리포트: V1에서 구축한 자동화 파이프라인으로 V2 RAG 엔진(35개 TC)을 검증하여 최종 풀페이지 감사 리포트(99_final_audit_report_V2.png) 산출

RAG 할루시네이션(환각) 차단:

매뉴얼 영역을 벗어난 무관한 질의(Out-of-Domain)에 대한 환각 답변 완전 제거

매뉴얼 내 제약 사항(Warnings) 안내 강화로 '미지원 기능' 오분류 최소화 (4건 ➡️ 1건으로 75% 감소)

## 🧪 V1 Baseline Architecture
RAG 도입 전 베이스라인 측정 및 품질 게이트 수립

## 1. Baseline 검증 계획 및 목표
목적: 생성형 AI 챗봇 아키텍처에 RAG를 도입하기 전, 시스템의 기본 성능을 정량적으로 평가하고 향후 회귀 테스트의 기준점이 될 Baseline 품질 게이트 수립

테스트 대상: GPT-4o-mini 기반의 차량 인포테인먼트 QA 목적 Baseline 시뮬레이터

핵심 프롬프트 & 파라미터:

System 페르소나: "너는 차량 인포테인먼트 비서야. 하이패스 이력이나 차량 정보에 대해 친절하고 아주 간결하게 답해줘."

Temperature: 0.2 (답변의 일관성 및 결정론적 출력을 확보하기 위한 저온도 설정)

검증 스코프: RAG 없이 내부 파라미터와 System 페르소나 제어만으로 ccNC 사용자 인풋에 대해 정확하고 일관된 답변을 도출하는지 확인

## 🛠️ V2 RAG Engine Architecture
현대 ccNC 웹매뉴얼 데이터 기반 고도화 RAG 파이프라인 구축

## 1. Data Pipeline & Knowledge Base
웹매뉴얼 파싱: ccNC 공식 웹매뉴얼 107개 HTML의 <p>, <li> 태그를 정제하여 parsed_ccnc_manual.json 구축

Context 보존 청킹: 문맥 단절 방지를 위해 TextSplitter 대신 1개 카테고리/기능당 1개의 Document로 1:1 완벽 맵핑 (카테고리명, 상세 기능, Warnings 구조화)

### 2. Tech Stack & Models
* **Framework (`LangChain`)**: RAG 체인 파이프라인 구성 및 체인 제어
* **Embedding (`text-embedding-3-small`)**: ccNC 웹매뉴얼 문맥의 고성능 벡터화
* **Vector DB (`DocArrayInMemorySearch`)**: 메모리 기반 초고속 유사도 검색 (`k=5`)
* **LLM (`OpenAI gpt-4o-mini`)**: 검색된 문맥 기반 답변 생성 (`temperature=0.2`)

## 3. Prompt Engineering & Dual-Routing
System 페르소나: 차량 인포테인먼트 마스터 '브레이크 마스터'

제어 요청 최적화: 단순 "켜줘/실행해줘" 요청 시 장황한 설명 없이 1문장 단축 응답으로 처리

제약 조건(Warnings) 안내: 조건 초과 요청 시 '미지원'으로 오인하지 않고 정확한 제약 사항 안내

Strict Out-of-Domain: 매뉴얼에 없는 질의는 *"죄송합니다. 해당 기능은 현재 지원하지 않습니다."*로 답변 고정

FastAPI Dual-Routing:

Priority 1 (정적 라우터): 특정 TC 검증용 HTTP 예외 코드(400, 403, 404, 500) 시뮬레이션

Priority 2 (동적 와일드카드): 나머지 모든 REST API/Streamlit 요청을 V2 RAG 파이프라인으로 유연하게 처리

## 🛠️ 향후 로드맵 (Roadmap)

V3: 가드레일 주입

V4: 긴급 대응 프로세스 적용
