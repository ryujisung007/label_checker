"""📄 법령 학습"""
import streamlit as st
import sys, os
PAGE_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.dirname(PAGE_DIR)
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)
from data import *

st.set_page_config(page_title="법령학습", page_icon="📄", layout="wide")
st.markdown("# 📄 법령 PDF 학습")
st.markdown("3개 법령 PDF를 업로드하면 텍스트를 추출하여 지식베이스를 구축합니다")
st.markdown("---")

for doc_key, schema in REGULATION_SCHEMA.items():
    with st.container(border=True):
        c1, c2 = st.columns([2, 3])

        with c1:
            kb = load_knowledge(doc_key)
            st.markdown(f"### {'✅' if kb else '⬜'} {schema['법령명']}")
            st.caption(f"약칭: {schema['약칭']} | 검토항목: {len(schema['검토항목'])}개")

            if kb:
                st.success(f"학습 완료: {len(kb['chunks'])}개 청크, {kb['full_text_length']:,}자")
                st.caption(f"파일: {kb['filename']} | 갱신: {kb['updated'][:16]}")

                if st.button(f"🗑️ 초기화", key=f"reset_{doc_key}"):
                    filepath = os.path.join(KB_DIR, f"{doc_key}.json")
                    if os.path.exists(filepath):
                        os.remove(filepath)
                    st.rerun()

        with c2:
            uploaded = st.file_uploader(
                f"{schema['약칭']} PDF 업로드",
                type=["pdf"], key=f"pdf_{doc_key}",
                help=f"{schema['법령명']} 원문 PDF를 업로드하세요"
            )

            if uploaded:
                with st.spinner(f"📄 {uploaded.name} 처리 중..."):
                    text, msg = extract_pdf(uploaded)

                if text:
                    n_chunks = save_knowledge(doc_key, text, uploaded.name)
                    st.success(f"✅ {msg} → {n_chunks}개 조항 청크로 저장")

                    with st.expander("추출된 텍스트 미리보기", expanded=False):
                        st.text_area("", text[:3000], height=200, key=f"preview_{doc_key}")
                        if len(text) > 3000:
                            st.caption(f"(전체 {len(text):,}자 중 상위 3,000자)")
                    st.rerun()
                else:
                    st.error(f"❌ {msg}")

    st.markdown("")

# 전체 현황 요약
st.markdown("---")
st.markdown("### 📊 지식베이스 현황")

all_kb = load_all_knowledge()
total_chunks = sum(len(kb.get("chunks", [])) for kb in all_kb.values())
total_chars = sum(kb.get("full_text_length", 0) for kb in all_kb.values())

mc1, mc2, mc3 = st.columns(3)
mc1.metric("학습 법령", f"{len(all_kb)}/3")
mc2.metric("총 청크", f"{total_chunks}개")
mc3.metric("총 텍스트", f"{total_chars:,}자")

if len(all_kb) == 3:
    st.success("🎉 3개 법령 모두 학습 완료! [🔍 적부판정] 페이지에서 검토를 시작하세요.")
elif len(all_kb) > 0:
    missing = [s["약칭"] for k, s in REGULATION_SCHEMA.items() if k not in all_kb]
    st.warning(f"⚠️ 미학습: {', '.join(missing)} — PDF를 업로드하세요. (학습 없이도 기본 규칙 기반 판정은 가능합니다)")
else:
    st.info("📤 법령 PDF를 업로드하면 AI가 더 정확하게 판정할 수 있습니다. PDF 없이도 기본 판정은 가능합니다.")

# 지식베이스 검색
st.markdown("---")
st.markdown("### 🔍 지식베이스 검색")
search_q = st.text_input("키워드 검색", placeholder="예: 소비기한, 알레르기, 원산지, 용출시험")

if search_q:
    for doc_key, schema in REGULATION_SCHEMA.items():
        results = search_knowledge(doc_key, search_q)
        if results:
            st.markdown(f"**📖 {schema['법령명']}** — {len(results)}건")
            for i, r in enumerate(results[:5]):
                with st.expander(f"결과 {i+1}", expanded=i < 2):
                    st.text(r[:500])

render_chatbot("법령학습", "법령 PDF 업로드 및 지식베이스 구축 페이지.")
