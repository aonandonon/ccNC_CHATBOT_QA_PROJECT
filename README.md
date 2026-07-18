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
│   └── .env.example         # 환경변수 템플릿 (실행시 .env로 파일명 변경 필요)
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

