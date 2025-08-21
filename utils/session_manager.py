# utils/session_manager.py
import streamlit as st

# config에서 STEP_INFO만 가져옵니다.
# 만약 config에 없으면(ImportError) 기본값을 사용해서 앱이 죽지 않도록 합니다.
try:
    from config import STEP_INFO
except Exception:
    STEP_INFO = [
        {"key": "file_upload",        "label": "파일 업로드"},
        {"key": "material_analysis",  "label": "소재 분석"},
        {"key": "blog_writer",        "label": "블로그 작성"},
        {"key": "image_generator",    "label": "이미지 생성"},
        {"key": "wordpress_publish",  "label": "워드프레스 발행"},
    ]

def _ensure_session_defaults():
    if "step_index" not in st.session_state:
        st.session_state.step_index = 0
    if "materials" not in st.session_state:
        st.session_state.materials = []          # 업로드/추출된 원문들
    if "analysis" not in st.session_state:
        st.session_state.analysis = {}           # 소재 분석 결과
    if "draft" not in st.session_state:
        st.session_state.draft = ""              # 블로그 초안
    if "images" not in st.session_state:
        st.session_state.images = []             # 생성 이미지 경로/URL
    if "publish_result" not in st.session_state:
        st.session_state.publish_result = None   # WP 발행 결과

def initialize_session_state():
    """앱 시작 시 1회 호출: 세션 키 기본값 구성"""
    _ensure_session_defaults()

def get_total_steps() -> int:
    return len(STEP_INFO)

def get_step_info(index: int = None) -> dict:
    """현재(또는 지정 index의) 스텝 정보 반환"""
    _ensure_session_defaults()
    idx = st.session_state.step_index if index is None else index
    idx = max(0, min(idx, len(STEP_INFO) - 1))
    return STEP_INFO[idx]

def move_to_step(index: int):
    """지정 인덱스로 이동"""
    _ensure_session_defaults()
    st.session_state.step_index = max(0, min(index, len(STEP_INFO) - 1))

def next_step():
    """다음 단계로 이동"""
    _ensure_session_defaults()
    st.session_state.step_index = min(st.session_state.step_index + 1, len(STEP_INFO) - 1)

def reset_workflow():
    """전체 워크플로우 초기화"""
    st.session_state.clear()
    _ensure_session_defaults()
