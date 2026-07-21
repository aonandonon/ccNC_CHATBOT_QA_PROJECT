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

🚀 단계별 검증 성과 & 고도화 (Milestones)
🔹 V1: 기초 QA 프레임워크 구축 (Rule-based)
시나리오 기반 TC 설계: 웹매뉴얼 챗봇 핵심 유저 시나리오 문서화 완료

API 응답 무결성 검증: 서버 통신 로그 및 데이터 흐름을 추적하여 report_V1.html 자동 생성

UI 자동화 & 증적 포착: Playwright를 활용해 상태 전이 검증 및 결함 구간 자동 스크린샷(01_TC-01.png 등) 저장

🔹 V2: RAG 파이프라인 구축 & 자동화 고도화 (Current)
35/35 전체 TC 자동화 완료: API 통신 및 UI 풀페이지 감사 리포트(99_final_audit_report_V2.png) 캡처 성공

할루시네이션 극복: 무관한 질의(Out-of-Domain)에 대한 환각 답변을 완전히 제거하고, 미지원 기능 오분류 최소화 (4건 ➡️ 1건 감소)

🛠️ V2 RAG Engine Architecture
현대 ccNC 웹매뉴얼 데이터 기반의 고도화된 RAG 파이프라인을 구축하여 환각 현상을 극복하고 정밀한 검증 환경을 구현했습니다.

1. Data Pipeline & Knowledge Base
웹매뉴얼 파싱: ccNC 공식 웹매뉴얼 107개 HTML의 <p>, <li> 태그를 정제하여 parsed_ccnc_manual.json 구축

Context 보존 청킹: 문맥 단절 방지를 위해 TextSplitter 대신 1개 카테고리/기능당 1개의 Document로 1:1 완벽 맵핑 (카테고리명, 상세 기능, Warnings 구조화)

2. Tech Stack & Models
구분,기술 스택 / 모델,역할
Framework,LangChain,RAG 체인 파이프라인 구성
Embedding,text-embedding-3-small,매뉴얼 문맥의 고성능 벡터화
Vector DB,DocArrayInMemorySearch,메모리 기반 초고속 유사도 검색 (k=5)
LLM,OpenAI gpt-4o-mini (temp=0.2),검색된 문맥 기반 답변 생성

3. Prompt Engineering & Dual-Routing
페르소나: 차량 인포테인먼트 마스터 '브레이크 마스터'

제어 요청 최적화: 단순 "켜줘/실행해줘" 요청 시 장황한 설명 없이 1문장 단축 응답으로 처리

제약 조건(Warnings) 안내: 조건 초과 요청 시 '미지원'으로 오인하지 않고 정확한 제약 사항 안내

Strict Out-of-Domain: 매뉴얼에 없는 질의는 *"죄송합니다. 해당 기능은 현재 지원하지 않습니다."*로 답변 고정

FastAPI Dual-Routing:

Priority 1 (정적 라우터): 특정 TC 검증용 HTTP 예외 코드(400, 403, 404, 500) 시뮬레이션

Priority 2 (동적 와일드카드): 나머지 모든 REST API/Streamlit 요청을 V2 RAG 파이프라인으로 유연하게 처리

🛠️ 향후 로드맵 (Roadmap)
V3: RAG 응답 평가 자동화 Metrics (Ragas 등) 도입 및 엣지 케이스 시나리오 확장

V4: CI/CD 파이프라인 연동을 통한 QA 자동화 테스트 무인화
