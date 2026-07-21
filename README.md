# ccNC Chatbot Dashboard QA Project

## 📌 프로젝트 개요 (Project Overview)
본 프로젝트는 **ccNC 웹매뉴얼 챗봇**의 품질을 확보하기 위해, V1부터 V4 단계로 세분화한 **시나리오 기반 QA 자동화 프레임워크**입니다.
시스템 상태 전이와 데이터 흐름을 추적하고, UI 결함을 자동으로 포착하여 리포팅하도록 설계되었습니다.

* **목적**: 챗봇 응답 API 데이터 무결성 검증 및 다양한 UI 환경에서의 화면 상태 전이 검증
* **핵심 기술**: Playwright, Python, JSON Data Parsing, API 검증 리포트 자동화

---

## 📂 프로젝트 구조 (Project Structure)
V1 단계의 프레임워크는 멀티 폴더 구조로 설계되어 있으며, 보안을 위해 API Key 등 민감 정보는 `.env.example` 템플릿 처리하여 관리합니다.

```text
ccNC_CHATBOT_QA_PROJECT/
├── chatbot_server/          # 챗봇 목업 서버 및 대시보드
│   ├── V1/
│   └── .env.example         # 환경변수 설정 템플릿 (.env로 복사하여 사용)
└── qa_automation/           # QA 자동화 테스트 스크립트 및 산출물
    ├── json_conversion.py   # 로그/데이터 파싱 및 변환 스크립트
    └── V1/
        ├── api_testing/     # API 기능 및 데이터 검증 (TC / HTML 리포트)
        ├── ui_testing/      # Playwright 기반 UI 자동화 테스트 (결함 스크린샷 포함)
        └── docs_and_templates/ # ccNC 웹매뉴얼 챗봇_TC_V1.xlsx (테스트케이스)

🚀 V1 주요 검증 내용 & 성과 (Key Achievements)
1.시나리오 기반 TC 설계: 웹매뉴얼 챗봇 핵심 시나리오를 바탕으로 검증 항목을 구조화하여 엑셀 문서화 완료.
2.API 응답 무결성 검증: 서버 통신 로그 및 데이터 흐름을 추적하고 report_V1.html로 검증 결과 자동 출력.
3.UI 자동화 및 결함 포착: Playwright를 활용해 사용자 시나리오별 UI 상태 전이를 검증하고, 결함 의심 구간의 스크린샷(01_TC-01.png 등)을 자동 캡처하여 증적 확보.

🛠️ 향후 업데이트 계획 (Roadmap)
V2: 예외 시나리오 확장 및 LangChain / RAG 구조 기반 데이터 무결성 검증 추가
V3-V4: RAG 할루시네이션(환각) 방지 시나리오 테스트 및 QA 자동화 파이프라인 고도화


**## 📂 프로젝트 구조 (Project Structure)**

ccNC_CHATBOT_QA_PROJECT/
├── chatbot_server/                # 챗봇 백엔드 서버 및 프론트엔드 대시보드
│   ├── V1/                        # V1 버전 (Rule-based / Mock Backend)
│   │   ├── app_V1.py
│   │   └── dashboard.py
│   ├── V2/                        # V2 버전 (LangChain RAG 파이프라인 엔진)
│   │   ├── app_V2.py              # FastAPI Dual-Routing 및 RAG 엔진 백엔드
│   │   ├── dashboard_V2.py        # Streamlit V2 인터랙티브 대시보드
│   │   └── parsed_ccnc_manual.json # ccNC 웹 매뉴얼 파싱 지식 베이스 (107개 HTML 기반)
│   └── .env.example               # 중앙 환경변수 설정 템플릿 (.env로 복사하여 사용)
└── qa_automation/                 # QA 자동화 테스트 스크립트 및 검증 산출물
    ├── json_conversion.py         # Newman 결함 리포트 JSON ➡️ Excel/HTML 자동 변환 스크립트
    ├── V1/                        # V1 테스트 스크립트 및 결과 리포트
    │   ├── api_testing/           # Postman/Newman 기반 API 자동화 테스트
    │   ├── ui_testing/            # Playwright 기반 UI E2E 테스트 및 결함 캡처
    │   └── docs_and_templates/    # ccNC 웹매뉴얼 챗봇_TC_V1.xlsx (테스트케이스)
    └── V2/                        # V2 RAG 검증 스크립트 및 자동화 산출물
        ├── api_testing/           # V2 RAG 검증용 TC-01~TC-35 실행 및 Newman 리포트
        ├── ui_testing/            # Playwright V2 검증 (35개 스크린샷 & 99_final_audit_report_V2.png)
        └── docs_and_templates/    # ccNC 웹매뉴얼 챗봇_TC_V2.xlsx (개선된 TC 및 평가 결과)

## 🛠️ V2 RAG Engine Architecture & Key Features

현대 ccNC 웹 매뉴얼 데이터 기반의 **고도화된 RAG 파이프라인**을 구축하여 환각(Hallucination) 현상을 극복하고 정밀한 검증 환경을 구현했습니다.

### 1. Data Pipeline & Knowledge Base
* **웹 매뉴얼 파싱**: ccNC 공식 웹 매뉴얼 107개 HTML의 `<p>`, `<li>` 태그를 정제하여 `parsed_ccnc_manual.json` 데이터셋 구축
* **Context 보존 청킹 (Chunking Strategy)**: 일반적인 `TextSplitter` 사용 시 문맥 단절이 발생하는 문제를 방지하기 위해 **1개 카테고리/기능당 1개의 `Document`로 맵핑**
  * 각 문서에 `카테고리명`, `상세 기능`, `주의 및 제약 사항(Warnings)`을 구조화하여 메타데이터와 함께 저장

### 2. RAG Stack & Models
| 구분 | 기술 스택 / 모델 | 역할 |
|---|---|---|
| **Framework** | LangChain (`langchain-openai`, `langchain-community`) | RAG 체인 파이프라인 구성 |
| **Embedding** | `text-embedding-3-small` | 매뉴얼 문맥의 고성능 벡터화 |
| **Vector DB** | `DocArrayInMemorySearch` | 메모리 기반의 초고속 유사도 검색 (`k=5`) |
| **LLM** | OpenAI `gpt-4o-mini` (Temp: `0.2`) | 검색된 문맥 기반 답변 생성 |

### 3. Prompt Engineering & Response Optimization
* **페르소나 설정**: 차량 인포테인먼트 마스터 '브레이크 마스터' 지정
* **제약 조건 및 예외 최적화**:
  * **제어 요청 처리**: 단순 "켜줘/실행해줘" 요청 시 길고 장황한 설명 대신 핵심 단축 문구(1문장)로 즉시 응답
  * **제약 조건(Warnings) 안내**: 사용자가 조건 초과 요청 시 '미지원'으로 오분류하지 않고 매뉴얼상의 정확한 제약 사항 제시
  * **Strict Out-of-Domain**: 매뉴얼에 관련 정보가 전혀 없는 경우에만 *"죄송합니다. 해당 기능은 현재 지원하지 않습니다."* 문구 고정 출력

### 4. FastAPI Dual-Routing Architecture
* **정적 예외 라우터 (Priority 1)**: 특정 TC(TC-07, 12, 25, 31 등) 검증을 위한 HTTP 상태 코드(`400`, `403`, `404`, `500`) 시뮬레이션 엔드포인트 배치
* **동적 와일드카드 라우터 (Priority 2)**: 나머지 모든 REST API 요청(`GET`, `POST`, `DELETE`) 및 Streamlit UI 요청(`/chat`)을 V2 RAG 파이프라인으로 유연하게 수용

