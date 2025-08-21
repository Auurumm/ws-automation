# utils/session_manager.py
import streamlit as st
try:
    from config import STEP_INFO
except ImportError as e:
    # 배포 경로 문제로 config 모듈 로딩 실패 시 방어
    STEP_INFO = ["1️⃣ 인터뷰 업로드","2️⃣ 소재 도출","3️⃣ 블로그 작성","4️⃣ 이미지 생성","5️⃣ 발행"]


def _ordered_keys():
    return list(STEP_INFO.keys())

def _first_key():
    return _ordered_keys()[0]

def _last_key():
    return _ordered_keys()[-1]

def initialize_session_state():
    """세션 상태 초기화"""
    if "step_key" not in st.session_state:
        st.session_state.step_key = _first_key()

    # 공통 상태 버킷(필요 시 추가)
    st.session_state.setdefault("uploaded_file_info", None)   # 업로드된 파일 메타/텍스트
    st.session_state.setdefault("material_result", None)       # 소재 분석 결과
    st.session_state.setdefault("blog_draft", None)            # 블로그 초안
    st.session_state.setdefault("image_prompts", [])           # 이미지 프롬프트 리스트
    st.session_state.setdefault("generated_images", [])        # 생성된 이미지들(URL/바이너리)
    st.session_state.setdefault("publish_result", None)        # 워드프레스 발행 결과/에러

def get_step_info(key=None):
    """현재 또는 지정 key의 step info 반환"""
    if key is None:
        key = st.session_state.get("step_key", _first_key())
    info = STEP_INFO.get(key, None)
    if info is None:
        return {"key": _first_key(), **STEP_INFO[_first_key()]}
    return {"key": key, **info}

def move_to_step(key: str):
    """특정 step key로 이동"""
    if key in STEP_INFO:
        st.session_state.step_key = key
    else:
        # 잘못된 key가 들어오면 처음으로
        st.session_state.step_key = _first_key()

def next_step():
    """다음 단계로 이동"""
    keys = _ordered_keys()
    cur = st.session_state.get("step_key", _first_key())
    i = keys.index(cur)
    if i < len(keys) - 1:
        st.session_state.step_key = keys[i + 1]
    else:
        st.session_state.step_key = _last_key()

def prev_step():
    """이전 단계로 이동"""
    keys = _ordered_keys()
    cur = st.session_state.get("step_key", _first_key())
    i = keys.index(cur)
    if i > 0:
        st.session_state.step_key = keys[i - 1]
    else:
        st.session_state.step_key = _first_key()

def step_title():
    """현재 단계 제목(헤더용)"""
    info = get_step_info()
    return info["title"]
