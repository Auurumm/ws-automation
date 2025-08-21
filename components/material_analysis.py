# components/material_analysis.py
import streamlit as st
from config import CONTENT_TYPES, OPENAI_CONFIG
from utils.ai_analyzer import AIAnalyzer

def render_material_analysis_page():
    st.header("② 인터뷰 기반 소재 분석")

    # 업로드 파일/텍스트 확보
    interview_text = st.session_state.get("interview_text", "")
    uploaded_filename = st.session_state.get("uploaded_filename")  # 업로드 단계에서 name 저장

    if not interview_text:
        st.info("①에서 인터뷰 파일을 업로드하거나 텍스트를 입력해 주세요.")
        return

    if st.button("AI로 콘텐츠 소재 분석하기", type="primary"):
        analyzer = AIAnalyzer(api_key=OPENAI_CONFIG.get("api_key"))
        with st.spinner("분석 중..."):
            materials = analyzer.analyze_interview_content_keyword_based(interview_text)
            st.session_state["materials"] = materials
            st.session_state["uploaded_filename"] = uploaded_filename
        st.success("분석 완료!")

    materials = st.session_state.get("materials")
    if not materials:
        return

    # 탭 렌더링
    tabs = st.tabs(CONTENT_TYPES)
    for i, tab_name in enumerate(CONTENT_TYPES):
        with tabs[i]:
            items = materials.get(tab_name, [])
            if not items:
                st.caption("해당 유형의 소재가 발견되지 않았습니다.")
            for idx, it in enumerate(items, 1):
                with st.expander(f"{idx}. {it.get('title','(무제)')}"):
                    st.markdown(f"**요약:** {it.get('content','')}")
                    st.markdown(f"**키워드:** {', '.join(it.get('keywords', []))}")
                    if it.get("source_quote"):
                        st.markdown(f"**근거 문장:** “{it['source_quote']}”")
                    st.json(it)

    # 선택값 저장(다음 단계에서 사용)
    st.markdown("---")
    st.subheader("다음 단계로")
    sel_tab = st.selectbox("어떤 탭에서 소재를 선택할까요?", CONTENT_TYPES)
    idx = st.number_input("선택할 소재 번호(1부터)", min_value=1, step=1, value=1)
    if st.button("이 소재로 글 쓰기"):
        items = st.session_state["materials"].get(sel_tab, [])
        if not items or idx > len(items):
            st.error("선택 번호가 올바르지 않습니다.")
        else:
            st.session_state["selected_material"] = {"type": sel_tab, "data": items[idx-1]}
            st.session_state["step"] = 3
            st.success("선택되었습니다. 상단 탭에서 ③ 글쓰기 페이지로 이동하세요.")
