import asyncio
from playwright.async_api import async_playwright
import os
from datetime import datetime

async def run_tc_automation():
    # 💡 1. 현재 ui_testing 폴더 기준으로docs_and_templates 폴더 안의 엑셀 파일을 바라보도록 경로 수정 완료!
    excel_filename = "../docs_and_templates/ccNC 웹매뉴얼 챗봇_TC_V1.xlsx"
    
    if not os.path.exists(excel_filename):
        print(f"❌ [오류] 폴더 내에 '{excel_filename}' 파일이 존재하지 않습니다.")
        print("엑셀 파일 이름을 확인하여 프로젝트 폴더에 넣어주세요!")
        return

    # 💡 2. 실행 시각을 기준으로 덮어쓰기 없는 고유한 이력 폴더 생성
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_folder = f"test_screenshots/run_{timestamp}"
    os.makedirs(run_folder, exist_ok=True)
    print(f"📂 테스트 증적 저장 경로 생성 완료: {run_folder}")

    async with async_playwright() as p:
        print("🤖 Playwright 브라우저 기동 중...")
        # 눈으로 스크롤과 검증 과정을 구경할 수 있도록 headless=False 설정
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # 3. 스트림릿 대시보드 접속
        print("🌐 스트림릿 대시보드 접속 중...")
        await page.goto("http://localhost:8501")
        await page.wait_for_timeout(3000) # 페이지 초기 렌더링 대기

        # 4. 엑셀 파일 자동 업로드
        print(f"📂 엑셀 파일 자동 업로드 중: {excel_filename}")
        file_input = page.locator("input[type='file']")
        await file_input.set_input_files(excel_filename)
        await page.wait_for_timeout(3000) # 파일 로드 안정화 대기

        # 5. 🚀 자동화 검증 시나리오 실행 버튼 클릭
        print("🚀 '자동화 검증 시나리오 실행' 버튼 클릭!")
        run_button = page.locator("button:has-text('🚀 자동화 검증 시나리오 실행')")
        await run_button.click()

        print("⏳ 실시간 대화 모니터링 및 정밀 캡처 프로세스 시작...")
        
        last_captured_tc = 0

        # 💡 6. 실시간 대화 감지 및 답변 기준 정밀 스크롤/캡처 루프
        while True:
            # 화면에 렌더링된 사용자 질문(User)과 챗봇 답변(Assistant) 요소를 식별
            user_messages = page.locator("div[data-testid='stChatMessage']:has(div[data-testid='stMarkdownContainer']):has-text('[TC-')")
            assistant_messages = page.locator("div[data-testid='stChatMessage']:has(div[data-testid='stMarkdownContainer'])").filter(has_not=page.locator("text=[TC-"))
            
            user_count = await user_messages.count()
            assistant_count = await assistant_messages.count()

            # 질문과 답변이 둘 다 완벽하게 쌍을 이루어 로드되었을 때만 캡처 수행
            if user_count > last_captured_tc and assistant_count >= user_count:
                for idx in range(last_captured_tc, user_count):
                    tc_num_str = f"TC-{idx+1:02d}"
                    print(f"📸 {tc_num_str} 답변 로드 감지! 화면 정렬 중...")

                    # 🎯 [핵심] 챗봇의 '답변 말풍선'을 기준으로 화면을 스크롤
                    target_reply = assistant_messages.nth(idx)
                    await target_reply.scroll_into_view_if_needed()
                    
                    # 💡 미세 조정 대기
                    await page.wait_for_timeout(1500) 

                    # 시퀀스 번호를 붙여 고유한 파일명으로 저장
                    screenshot_name = f"{run_folder}/{idx+1:02d}_{tc_num_str}.png"
                    await page.screenshot(path=screenshot_name)
                    print(f"   └─ 정밀 증적 저장 완료: {screenshot_name}")

                last_captured_tc = user_count

            # 7. 화면 하단에 검증 완료 안내가 떴는지 실시간 감시
            complete_msg = page.locator("text=🎉 모든 시나리오 검증 완료!")
            if await complete_msg.is_visible():
                await complete_msg.scroll_into_view_if_needed()
                await page.wait_for_timeout(1000)
                print("✅ 모든 시나리오 채점 완료 시그널 확인!")
                break

            await asyncio.sleep(1) # 1초 간격으로 모니터링 반복

        # 8. 최종 하단 채점표(Audit Report) 및 전체 대시보드 통계 화면 요약 정밀 캡처
        print("📊 최종 채점 리포트 영역으로 스크롤 이동 중...")
        report_header = page.locator("text=📊 실시간 채점표 (Audit Report)")
        if await report_header.is_visible():
            await report_header.scroll_into_view_if_needed()
            await page.wait_for_timeout(2000) 
            
            # 잘림 방지를 위해 브라우저 창의 높이를 일시적으로 늘림
            await page.set_viewport_size({"width": 1280, "height": 2500})
            await page.wait_for_timeout(1000) 
            
            final_report_path = f"{run_folder}/99_final_audit_report.png"
            await page.screenshot(path=final_report_path)
            print(f"📸 최종 통계 리포트 무감쇄 캡처 완료: {final_report_path}")

        # 9. 브라우저 세션 안전 종료
        await browser.close()
        print(f"🏁 Playwright 자동화 검증 완료! 생성된 모든 증적은 '{run_folder}'에서 확인 가능합니다.")

if __name__ == "__main__":
    asyncio.run(run_tc_automation())