import streamlit as st
import requests
import pandas as pd
import time

# 화면 레이아웃을 넓게 설정
st.set_page_config(layout="wide")

st.markdown("""
    <style>
    /* 데이터프레임 내부 텍스트 자동 줄바꿈 및 가운데 정렬 */
    .stDataFrame div[data-testid="stTable"] td {
        white-space: pre-wrap !important;
        word-wrap: break-word !important;
        text-align: center !important;
    }
    div[data-testid="stDataFrame"] div {
        white-space: pre-wrap !important;
    }

    /* 스트림릿 디폴트 화살표 아이콘 완전히 숨기기 */
    div[data-testid="stMetricDelta"] svg {
        display: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🚗 ccNC 챗봇 자동 검증 및 실시간 모니터링")
st.write("---")

# [채점 엔진 함수]
def evaluate_response(response_text, required_kws, optional_kws, banned_kws, is_api_error=False):
    if is_api_error:
        return {
            "score": 0,
            "status": "FAIL",
            "matched_req": "N/A",
            "matched_opt": "N/A",
            "matched_ban": "N/A",
        }

    response_text = str(response_text).strip()

    req_raw = "" if pd.isna(required_kws) else str(required_kws)
    opt_raw = "" if pd.isna(optional_kws) else str(optional_kws)
    ban_raw = "" if pd.isna(banned_kws) else str(banned_kws)

    req_list = [w.strip() for w in req_raw.split(",") if w.strip()]
    opt_list = [w.strip() for w in opt_raw.split(",") if w.strip()]
    ban_list = [w.strip() for w in ban_raw.split(",") if w.strip()]

    matched_req = [w for w in req_list if w in response_text]
    matched_opt = [w for w in opt_list if w in response_text]
    matched_ban = [w for w in ban_list if w in response_text]

    score = 0
    if matched_ban:
        score = 0
        status = "FAIL"
    elif matched_req:
        score = 100
        status = "PASS"
    else:
        score = min(len(matched_opt) * 20, 60)
        status = "PASS (⚠️보완 필요)" if score == 60 else "FAIL"

    return {
        "score": score,
        "status": status,
        "matched_req": ", ".join(matched_req) if matched_req else "없음",
        "matched_opt": ", ".join(matched_opt) if matched_opt else "없음",
        "matched_ban": ", ".join(matched_ban) if matched_ban else "없음",
    }

# 💡 상단 탭 정의 (자동 검증 탭과 수동 검증 탭 분리)
tab_auto, tab_manual = st.tabs(["🚀 자동화 시나리오 검증", "🛡️ 수동 보안 및 에지 케이스 검증"])

# ==========================================
# 1번 탭: 자동화 시나리오 검증 (기존 코드 안전하게 이주)
# ==========================================
with tab_auto:
    st.sidebar.header("📂 검증 시나리오 로드")
    uploaded_file = st.sidebar.file_uploader("Excel을 업로드하세요.", type=["xlsx"])

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if uploaded_file is not None:
        df_excel = pd.read_excel(uploaded_file)
        st.sidebar.success(f"총 {len(df_excel)}개의 TC가 정상 로드되었습니다!")

        if st.sidebar.button("🚀 자동화 검증 시나리오 실행"):
            st.session_state.chat_history = []
            results = []
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            st.write("### 💬 실시간 대화 모니터링 (Live Feed)")
            chat_placeholder = st.container()
            
            st.write("---")
            st.write("### 📊 실시간 채점표 (Audit Report)")
            table_placeholder = st.empty()

            for idx, row in df_excel.iterrows():
                tc_id = row['tc_id']
                pre_condition = row['pre_condition']
                prompt = str(row['prompt'])
                req_kws = row['required_kws']
                opt_kws = row['optional_kws']
                ban_kws = row['banned_kws']
                
                excel_error_type = row['error_type'] if 'error_type' in row else "지정 안 됨"

                status_text.text(f" 진행 중: {tc_id} - '{prompt[:15]}...' 호출 중...")
                is_api_error = False

                try:
                    full_payload = {
                        "prompt": f"[사전 조건: {pre_condition}]\n사용자 발화: {prompt}"
                    }
                    api_res = requests.post(
                        "http://localhost:8000/api/v1/navigation/chat", 
                        json=full_payload,
                        timeout=8
                    )
                    if api_res.status_code == 200:
                        bot_response = api_res.json()["response"]
                    else:
                        bot_response = f"[API 서버 에러] HTTP {api_res.status_code} 응답"
                        is_api_error = True
                except Exception as e:
                    bot_response = "❌ API 서버가 오프라인 상태입니다."
                    is_api_error = True

                eval_res = evaluate_response(bot_response, req_kws, opt_kws, ban_kws, is_api_error)

                st.session_state.chat_history.append({"role": "user", "content": f"[{tc_id}] {prompt}"})
                st.session_state.chat_history.append({"role": "assistant", "content": bot_response})
                
                with chat_placeholder:
                    with st.chat_message("user"):
                        st.write(f"**[{tc_id}]** {prompt}")
                    with st.chat_message("assistant"):
                        st.write(bot_response)

                final_status = eval_res['status']
                shown_error_type = "정상 통과 (PASS)" if "PASS" in final_status else str(excel_error_type)

                results.append({
                    "TC ID": tc_id,
                    "사전 조건": pre_condition,
                    "판정 결과": final_status,
                    "채점 점수": f"{eval_res['score']}점",
                    "AI 오류 유형": shown_error_type,
                    "매칭 필수 키워드": eval_res['matched_req'],
                    "매칭 선택 키워드": eval_res['matched_opt'],
                    "매칭 금지 키워드": eval_res['matched_ban']
                })

                progress_bar.progress((idx + 1) / len(df_excel))
                df_current = pd.DataFrame(results)
                df_current.index = df_current.index + 1
                table_placeholder.dataframe(df_current, use_container_width=True)
                
                time.sleep(0.1)

            status_text.success("🎉 모든 시나리오 검증 완료! 최종 보고서가 빌드되었습니다.")
            
            df_final = pd.DataFrame(results)
            total_tc = len(df_final)
            pass_count = df_final["판정 결과"].str.contains("PASS").sum()
            fail_count = total_tc - pass_count
            
            pass_ratio = (pass_count / total_tc) * 100 if total_tc > 0 else 0
            fail_ratio = 100 - pass_ratio

            st.write("---")
            st.write("### 📈 전체 테스트 실행 통계 요약")
            
            col1, col2, col3 = st.columns(3)
            col1.metric(label="총 테스트 개수", value=f"{total_tc}개")
            
            col2.markdown(f"""
                <div style="background-color: #f0fdf4; padding: 15px; border-radius: 10px; border-left: 5px solid #22c55e;">
                    <p style="margin: 0; font-size: 14px; color: #166534; font-weight: bold;">통과된 TC (PASS)</p>
                    <h2 style="margin: 5px 0 0 0; color: #15803d; font-size: 28px;">{pass_count}개</h2>
                    <p style="margin: 5px 0 0 0; font-size: 14px; color: #15803d; font-weight: bold;">🎯 통과율 {pass_ratio:.1f}%</p>
                </div>
            """, unsafe_allow_html=True)
            
            col3.markdown(f"""
                <div style="background-color: #fef2f2; padding: 15px; border-radius: 10px; border-left: 5px solid #ef4444;">
                    <p style="margin: 0; font-size: 14px; color: #991b1b; font-weight: bold;">실패한 TC (FAIL)</p>
                    <h2 style="margin: 5px 0 0 0; color: #b91c1c; font-size: 28px;">{fail_count}개</h2>
                    <p style="margin: 5px 0 0 0; font-size: 14px; color: #b91c1c; font-weight: bold;">🚨 실패율 {fail_ratio:.1f}%</p>
                </div>
            """, unsafe_allow_html=True)

            st.write("---")
            st.write("### 📊 실제 FAIL 케이스의 AI 오류 유형 분포 분석 (Actual Failures Only)")
            
            chart_col1, chart_col2 = st.columns([1, 1])
            df_fails_only = df_final[df_final["판정 결과"].str.contains("FAIL")]

            with chart_col1:
                st.write("#### 📝 검출된 결함 유형별 통계 리포트")
                if len(df_fails_only) > 0:
                    error_counts = df_fails_only["AI 오류 유형"].value_counts().reset_index()
                    error_counts.columns = ["내가 분류한 AI 오류 유형", "발생한 결함 수 (개)"]
                    error_counts.index = error_counts.index + 1
                    st.dataframe(error_counts, use_container_width=True)
                else:
                    st.success("🎯 검출된 AI 결함이 없습니다! 모든 테스트 케이스가 완벽하게 통과했습니다.")

            with chart_col2:
                st.write("#### 📈 결함 원인 분석 차트 (Bar Chart)")
                if len(df_fails_only) > 0:
                    chart_data = df_fails_only["AI 오류 유형"].value_counts()
                    st.bar_chart(chart_data)
                else:
                    st.info("시각화할 에러 데이터가 없습니다.")
    else:
        st.info("💡 왼쪽 사이드바에서 작성하신 검증 엑셀 파일을 업로드하고 실행해 보세요!")


# ==========================================
# 2번 탭: 🛡️ 수동 보안 및 에지 케이스 검증 (말풍선 박제 + 최하단 인풋 반영 완료)
# ==========================================
with tab_manual:
    # 상단 레이아웃 헤더 및 리셋 버튼 배치
    col_title, col_reset = st.columns([5, 1])
    with col_title:
        st.write("### 🛡️ 수동 보안 및 취약점 검증")
        st.info("RAG 및 LLM 로직의 탈옥(Jailbreak), 악성 프롬프트 주입 및 에지 케이스 보안 수준을 실시간으로 수동 테스트하는 윈도우입니다.")
    with col_reset:
        st.write("<br>", unsafe_allow_html=True)
        if st.button("🗑️ 대화 초기화", use_container_width=True):
            st.session_state.manual_history = []
            st.rerun()

    # 세션 상태 초기화 (수동 테스트 전용 대화 기록)
    if "manual_history" not in st.session_state:
        st.session_state.manual_history = []

    # 수동 검증용 사전 조건 설정창 (상단 유지)
    manual_pre_condition = st.text_input(
        "⚙️ 테스트용 사전 조건 설정 (예: 시동 ON, 네트워크 불안정 등)", 
        value="내비 on, 우리집 등록"
    )

    st.write("---")
    st.write("#### 💬 생성형 AI 실시간 대화")

    # [수정포인트 1]: 입력창이 렌더링되기 전에 기존 대화 내역을 화면에 '먼저' 전부 다 그립니다.
    for message in st.session_state.manual_history:
        if message["role"] == "user":
            with st.chat_message("user", avatar="🙋"):
                # 메세지 딕셔너리에 저장해둔 당시의 사전조건을 꼬리표(Caption)로 노출합니다.
                if "pre_cond" in message:
                    st.caption(f"🔒 **적용 상태:** {message['pre_cond']}")
                st.write(message["content"])
        else:
            with st.chat_message("assistant", avatar="🤖"):
                st.write(message["content"])

    # [수정포인트 2]: 입력창을 코드의 가장 마지막 순서에 배치하여 스크롤 및 레이아웃 최하단으로 고정합니다.
    if manual_prompt := st.chat_input("프롬프트를 입력하세요 (예: 비정상 명령어 주입 등)"):
        
        # 사용자가 입력한 내용을 화면에 뱃지와 함께 즉시 임시 렌더링
        with st.chat_message("user", avatar="🙋"):
            st.caption(f"🔒 **적용 상태:** {manual_pre_condition}")
            st.write(manual_prompt)
            
        # 히스토리에 넣을 때 당시에 상단 인풋창에 입력되어 있던 'manual_pre_condition' 값을 함께 묶어 박제합니다.
        st.session_state.manual_history.append({
            "role": "user", 
            "content": manual_prompt,
            "pre_cond": manual_pre_condition
        })

        # 실시간 API 연동
        try:
            manual_payload = {
                "prompt": f"[사전 조건: {manual_pre_condition}]\n사용자 발화: {manual_prompt}"
            }
            with st.spinner("🤖 생성형 AI 답변 생성중..."):
                manual_res = requests.post(
                    "http://localhost:8000/api/v1/navigation/chat",
                    json=manual_payload,
                    timeout=8
                )
                if manual_res.status_code == 200:
                    manual_response = manual_res.json()["response"]
                else:
                    manual_response = f"⚠️ [서버 응답 실패] HTTP 코드: {manual_res.status_code}"
        except Exception as e:
            manual_response = "❌ 백엔드 API 서버 오프라인 상태"

        # 챗봇 답변을 히스토리에 추가
        st.session_state.manual_history.append({"role": "assistant", "content": manual_response})
        
        # 화면을 리런하여 올바른 전체 타임라인 순서로 대화를 재정렬합니다.
        st.rerun()