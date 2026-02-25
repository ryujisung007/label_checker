"""
📋 식품 표시사항 적부 판별 시스템
"""
import streamlit as st
import sys, os
APP_DIR = os.path.dirname(os.path.abspath(__file__))
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)
from data import *

st.set_page_config(page_title="식품 표시 적부 판별", page_icon="📋", layout="wide")

st.markdown("# 📋 식품 표시사항 적부 판별 시스템")
st.markdown("#### PDF 법령 학습 → 제품 표시사항 입력 → 자동 적부 판정 → 법령 근거 제시")
st.markdown("---")

# API 키
has_key = render_api_key_input()

# 지식베이스 현황
kb = load_all_knowledge()
st.markdown("### 📚 법령 학습 현황")
c1, c2, c3 = st.columns(3)

for i, (doc_key, schema) in enumerate(REGULATION_SCHEMA.items()):
    col = [c1, c2, c3][i]
    kb_data = kb.get(doc_key)
    with col:
        with st.container(border=True):
            if kb_data:
                st.markdown(f"### ✅ {schema['약칭']}")
                st.caption(schema['법령명'])
                st.metric("조항 청크", f"{len(kb_data.get('chunks',[]))}개")
                st.caption(f"📄 {kb_data.get('filename','')} ({kb_data.get('full_text_length',0):,}자)")
            else:
                st.markdown(f"### ⬜ {schema['약칭']}")
                st.caption(schema['법령명'])
                st.warning("미학습 — [📄 법령학습] 페이지에서 PDF 업로드")

# 워크플로우
st.markdown("---")
st.markdown("### 🔄 사용 흐름")
st.markdown("""
```
Step 1 → 📄 법령 학습     PDF 업로드 (식품등의 표시기준, 원산지 표시요령, 기구용기 규격)
                              ↓
Step 2 → ✍️ 표시사항 입력   텍스트 붙여넣기 또는 CSV 업로드
                              ↓
Step 3 → 🔍 적부 판정      3개 법령 기준 자동 검토 (적합/주의/부적합)
                              ↓
Step 4 → 📊 결과 보고서     항목별 판정 + 관련 조항 + 개선 권고
                              ↓
Step 5 → 🤖 AI 심화분석     GPT 기반 맥락적 법령 해석
```
""")

# 검토 항목 목록
st.markdown("---")
st.markdown("### 📑 검토 항목 총괄")
for doc_key, schema in REGULATION_SCHEMA.items():
    with st.expander(f"**{schema['법령명']}** ({len(schema['검토항목'])}항목)", expanded=False):
        rows = []
        for item in schema["검토항목"]:
            rows.append({
                "코드": item["id"],
                "항목": item["항목"],
                "설명": item["설명"],
                "관련조항": item["관련조항"],
                "필수": "✅" if item["필수"] else "선택",
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

st.markdown("---")
if has_key:
    st.success("🔑 OpenAI API 연결됨")
else:
    st.info("🔑 사이드바에서 API 키를 입력하면 AI 심화분석을 사용할 수 있습니다")

st.caption("← 사이드바에서 메뉴를 선택하세요")

render_chatbot("메인", "식품 표시 적부 판별 시스템 메인. 3개 법령 기반 표시사항 검토.")
