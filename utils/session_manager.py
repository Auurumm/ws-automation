# utils/session_manager.py
import streamlit as st

# config에서 STEP_INFO만 가져옵니다.
# 만약 config에 없으면(ImportError) 기본값을 사용해서 앱이 죽지 않도록 합니다.
try:
    from config import STEP_INFO
except Exception:
    STEP_INFO = [
        {"key": "file_upload",        "label": "① 파일 업로드"},
        {"key": "material_analysis",  "label": "② 소재 분석"},
        {"key": "blog_writer",        "label": "③ 블로그 작성"},
        {"key": "image_generator",    "label": "④ 이미지 생성"},
        {"key": "wordpress_publish",  "label": "⑤ 워드프레스 발행"},
    ]

def _ensure_session_defaults():
    """세션 상태 기본값 설정"""
    if "step_index" not in st.session_state:
        st.session_state.step_index = 0
    if "step" not in st.session_state:  # main.py와의 호환성을 위해 추가
        st.session_state.step = 1
    if "materials" not in st.session_state:
        st.session_state.materials = []
    if "analysis" not in st.session_state:
        st.session_state.analysis = {}
    if "draft" not in st.session_state:
        st.session_state.draft = ""
    if "images" not in st.session_state:
        st.session_state.images = []
    if "publish_result" not in st.session_state:
        st.session_state.publish_result = None
    if "blog_content" not in st.session_state:
        st.session_state.blog_content = ""
    if "blog_title" not in st.session_state:
        st.session_state.blog_title = ""
    if "selected_material" not in st.session_state:
        st.session_state.selected_material = None
    if "uploaded_files" not in st.session_state:
        st.session_state.uploaded_files = []
    if "analysis_results" not in st.session_state:
        st.session_state.analysis_results = {}

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

def get_all_steps() -> list:
    """모든 스텝 정보 반환 (main.py 호환성)"""
    return [step["label"] for step in STEP_INFO]

def move_to_step(index: int):
    """지정 인덱스로 이동"""
    _ensure_session_defaults()
    st.session_state.step_index = max(0, min(index, len(STEP_INFO) - 1))
    st.session_state.step = st.session_state.step_index + 1  # main.py와 동기화

def next_step():
    """다음 단계로 이동"""
    _ensure_session_defaults()
    current_index = st.session_state.step_index
    new_index = min(current_index + 1, len(STEP_INFO) - 1)
    st.session_state.step_index = new_index
    st.session_state.step = new_index + 1  # main.py와 동기화

def previous_step():
    """이전 단계로 이동 (누락된 함수 추가)"""
    _ensure_session_defaults()
    current_index = st.session_state.step_index
    new_index = max(current_index - 1, 0)
    st.session_state.step_index = new_index
    st.session_state.step = new_index + 1  # main.py와 동기화

def reset_workflow():
    """전체 워크플로우 초기화"""
    st.session_state.clear()
    _ensure_session_defaults()

def get_current_step_key():
    """현재 단계의 키 반환"""
    _ensure_session_defaults()
    step_info = get_step_info()
    return step_info.get("key", "file_upload")

def is_step_accessible(step_index: int) -> bool:
    """해당 단계가 접근 가능한지 확인"""
    _ensure_session_defaults()
    
    # 첫 번째 단계는 항상 접근 가능
    if step_index == 0:
        return True
    
    # 이전 단계들이 완료되었는지 확인
    if step_index == 1:  # 소재 분석
        return len(st.session_state.uploaded_files) > 0
    elif step_index == 2:  # 블로그 작성
        return len(st.session_state.analysis_results) > 0
    elif step_index == 3:  # 이미지 생성
        return st.session_state.blog_content != ""
    elif step_index == 4:  # 워드프레스 발행
        return st.session_state.blog_content != "" and st.session_state.blog_title != ""
    
    return False