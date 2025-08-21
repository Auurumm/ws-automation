import streamlit as st
from config import STEP_INFO

def initialize_session_state():
    """세션 상태 초기화"""
    if 'step' not in st.session_state:
        st.session_state.step = 1
    if 'interview_file' not in st.session_state:
        st.session_state.interview_file = None
    if 'interview_content' not in st.session_state:
        st.session_state.interview_content = ""
    if 'content_materials' not in st.session_state:
        st.session_state.content_materials = {}
    if 'selected_material' not in st.session_state:
        st.session_state.selected_material = {}
    if 'blog_content' not in st.session_state:
        st.session_state.blog_content = ""
    if 'blog_title' not in st.session_state:
        st.session_state.blog_title = ""
    if 'generated_image' not in st.session_state:
        st.session_state.generated_image = None
    if 'openai_api_key' not in st.session_state:
        st.session_state.openai_api_key = ""

def get_step_info():
    """단계 정보 반환"""
    return STEP_INFO

def move_to_step(step_number):
    """특정 단계로 이동"""
    if 1 <= step_number <= len(STEP_INFO):
        st.session_state.step = step_number
        st.rerun()

def next_step():
    """다음 단계로 이동"""
    if st.session_state.step < len(STEP_INFO):
        st.session_state.step += 1
        st.rerun()

def previous_step():
    """이전 단계로 이동"""
    if st.session_state.step > 1:
        st.session_state.step -= 1
        st.rerun()

def reset_session():
    """세션 초기화 (새 작업 시작)"""
    for key in list(st.session_state.keys()):
        if key not in ['openai_api_key']:  # API 키는 유지
            del st.session_state[key]
    initialize_session_state()
    st.rerun()