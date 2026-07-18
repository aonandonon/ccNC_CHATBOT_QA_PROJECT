import pandas as pd
import json

# 1. 엑셀 파일 읽기 (상대 경로 반영)
df = pd.read_excel("../docs_and_templates/ccNC 웹매뉴얼 챗봇_TC_V1.xlsx", sheet_name="자동화")

json_data = []

for index, row in df.iterrows():
    # 실제 엑셀 헤더 이름인 'required_kws'와 'banned_kws'를 반영했습니다.
    req_kws = [k.strip() for k in str(row["required_kws"]).split(",")] if pd.notna(row["required_kws"]) else []
    ban_kws = [k.strip() for k in str(row["banned_kws"]).split(",")] if pd.notna(row["banned_kws"]) else []
    
    # 💡 딕셔너리 만들기 전에 줄바꿈(\n, \r)을 일반 공백으로 먼저 치환합니다.
    clean_prompt = str(row["prompt"]).replace("\n", " ").replace("\r", " ")
    
    tc_item = {
        "tc_id": str(row["tc_id"]),
        "method": str(row["method"]).upper().strip(),
        "url": str(row["url"]).strip(),
        "prompt": clean_prompt,                  # 쉼표(,) 잊지 말고 꼭 챙겨주세요!
        "expected_status": int(row["expected_status"]),
        "required_kws": req_kws,
        "banned_kws": ban_kws
    }
    
    json_data.append(tc_item)

# 2. 완벽한 JSON 파일로 저장하기
with open("test_data_set.json", "w", encoding="utf-8") as f:
    json.dump(json_data, f, ensure_ascii=False, indent=2)

print("🎉 영어 매핑 기반 JSON 파일(test_data_set.json) 변환 성공!")