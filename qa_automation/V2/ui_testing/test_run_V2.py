import asyncio
from playwright.async_api import async_playwright
import os
from datetime import datetime

async def run_tc_automation():
    # 💡 1. V2용 엑셀 테스트케이스 파일 경로 지정
    excel_filename = "../docs_and_templates/ccNC 웹매뉴얼 챗봇_TC_V2.xlsx"
    
    if not os.path.exists(excel_filename):
        print(f"❌ [오류] 폴더 내에 '{excel_filename}' 파일이 존재하지 않습니다.")
        return

    # 💡 2. V2 전용 증적 폴더 생성
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_folder = f"test_screenshots/run_V2_{timestamp}"
    os.makedirs(run_folder, exist_ok=True)
    print(f"📂 [V2] 테스트 증적 저장 경로 생성 완료: {run_folder}")

    async with async_playwright() as p:
        print("🤖 Playwright 브라우저 기동 중 (V2 QA Mode)...")
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            # 3. 스트림릿 대시보드 접속
            print("🌐 스트림릿 대시보드 접속 중...")
            await page.goto("http://localhost:8501")
            await page.wait_for_timeout(3000)

            # 4. V2 엑셀 파일 자동 업로드
            print(f"📂 V2 엑셀 파일 자동 업로드 중: {excel_filename}")
            file_input = page.locator("input[type='file']")
            await file_input.set_input_files(excel_filename)
            await page.wait_for_timeout(3000)

            # 5. 🚀 자동화 검증 시나리오 실행 버튼 클릭
            print("🚀 '자동화 검증 시나리오 실행' 버튼 클릭!")
            run_button = page.locator("button:has-text('🚀 자동화 검증 시나리오 실행')")
            await run_button.click()

            print("⏳ V2 실시간 대화 모니터링 및 정밀 캡처 프로세스 시작...")
            
            last_captured_tc = 0
            TOTAL_TC_COUNT = 35  # V2 전체 테스트케이스 개수 지정

            # 6. 실시간 대화 감지 및 답변 기준 정밀 스크롤/캡처 루프
            while True:
                user_messages = page.locator("div[data-testid='stChatMessage']:has(div[data-testid='stMarkdownContainer']):has-text('[TC-')")
                assistant_messages = page.locator("div[data-testid='stChatMessage']:has(div[data-testid='stMarkdownContainer'])").filter(has_not=page.locator("text=[TC-"))
                
                user_count = await user_messages.count()
                assistant_count = await assistant_messages.count()

                # 질문과 답변이 둘 다 완벽하게 쌍을 이루어 로드되었을 때 캡처
                if user_count > last_captured_tc and assistant_count >= user_count:
                    for idx in range(last_captured_tc, user_count):
                        tc_num_str = f"TC-{idx+1:02d}"
                        print(f"📸 {tc_num_str} V2 답변 로드 감지! 화면 정렬 중...")

                        target_reply = assistant_messages.nth(idx)
                        await target_reply.scroll_into_view_if_needed()
                        
                        await page.wait_for_timeout(1200)

                        screenshot_name = f"{run_folder}/{idx+1:02d}_{tc_num_str}.png"
                        await page.screenshot(path=screenshot_name)
                        print(f"   └─ V2 정밀 증적 저장 완료: {screenshot_name}")

                    last_captured_tc = user_count

                # 🎯 [핵심 변경] 35개 TC 캡처가 모두 끝나면 무조건 루프 탈출!
                if last_captured_tc >= TOTAL_TC_COUNT:
                    print("\n🎉 모든 35개 TC 답변 캡처 완료! 최종 리포트 캡처 준비 중...")
                    break

                await asyncio.sleep(1)

            # 7. 🎯 실시간 채점표 요소로 정밀 스크롤 후 캡처
            print("📊 최종 실시간 채점표 영역으로 정밀 스크롤 이동 중...")
            await page.wait_for_timeout(3000)  # 리포트 카드 계산 및 UI 완충 대기
            
            # 실시간 채점표 헤더 요소 찾기
            audit_report_header = page.locator("text=실시간 채점표 (Audit Report)")
            
            if await audit_report_header.is_visible():
                # 해당 채점표 제목 위치로 화면을 딱 맞춰 스크롤!
                await audit_report_header.scroll_into_view_if_needed()
                await page.wait_for_timeout(1500)
                
                # 채점표 전체가 화면에 넉넉히 들어오도록 뷰포트 높이 지정
                await page.set_viewport_size({"width": 1280, "height": 2000})
                await page.wait_for_timeout(1000)
                
                final_report_path = f"{run_folder}/99_final_audit_report_V2.png"
                await page.screenshot(path=final_report_path)
                print(f"📸 V2 최종 통계 리포트 정밀 캡처 완료: {final_report_path}")
            else:
                # 만약 요소를 못 찾을 경우 강제 하단 스크롤
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await page.wait_for_timeout(1500)
                final_report_path = f"{run_folder}/99_final_audit_report_V2.png"
                await page.screenshot(path=final_report_path, full_page=True)
                print(f"📸 대체 전체 스크롤 캡처 완료: {final_report_path}")
                
        finally:
            # 8. 브라우저 세션 안전 종료
            await browser.close()
            print(f"🏁 V2 Playwright 자동화 검증 완료! 생성된 증적 폴더: '{run_folder}'")

if __name__ == "__main__":
    asyncio.run(run_tc_automation())