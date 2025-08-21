# config.py
# 모든 모듈이 참조하는 '단일 출처(Single Source of Truth)' 구성

import os
import streamlit as st

# Streamlit secrets와 환경변수를 모두 지원하는 헬퍼 함수
def get_config_value(key, default=""):
    """Streamlit secrets 또는 환경변수에서 값을 가져오는 함수"""
    try:
        # Streamlit secrets에서 먼저 확인
        if hasattr(st, 'secrets') and key in st.secrets:
            return st.secrets[key]
    except:
        pass
    
    # 환경변수에서 확인
    return os.getenv(key, default)

# ───────────────────── 앱 기본 UI ─────────────────────
APP_CONFIG = {
    "page_title": "BGN 블로그 자동화",
    "page_icon": "🩺",
    "layout": "wide",
    "sidebar_state": "expanded",
    "main_title": "BGN 밝은눈안과 블로그 자동화",
    "footer_text": "© BGN 밝은눈안과",
}

# ───────────────────── 워크플로우 단계 ─────────────────────
STEP_INFO = [
    {"key": "file_upload",        "label": "① 파일 업로드"},
    {"key": "material_analysis",  "label": "② 소재 분석"},
    {"key": "blog_writer",        "label": "③ 블로그 작성"},
    {"key": "image_generator",    "label": "④ 이미지 생성"},
    {"key": "wordpress_publish",  "label": "⑤ 워드프레스 발행"},
]

# ───────────────────── OpenAI ─────────────────────
OPENAI_API_KEY = get_config_value("OPENAI_API_KEY", "")
OPENAI_MODEL = get_config_value("OPENAI_MODEL", "gpt-4o-mini")

OPENAI_CONFIG = {
    "model": OPENAI_MODEL,
    "api_key": OPENAI_API_KEY,
}

# ───────────────────── 파일 처리 ─────────────────────
FILE_CONFIG = {
    "allowed_exts": [".txt", ".md", ".docx", ".pdf"],
    "accept": ".txt,.md,.docx,.pdf",
    "max_size_mb": 25,
    "max_chars_for_analysis": 15000,
}

# ───────────────────── 콘텐츠 탭 키 ─────────────────────
CONTENT_TYPES = [
    "BGN 환자 에피소드형",
    "BGN 검사·과정형",
    "BGN 센터 운영/분위기형",
    "BGN 직원 성장기형",
    "BGN 환자 질문 FAQ형",
]

# ───────────────────── 블로그 길이 프리셋 ─────────────────────
QUALITY_CONFIG = {
    "표준 BGN (2,000자)":   {"min_chars": 2000, "target_chars": 2200, "max_tokens": 4500},
    "고품질 BGN (2,500자)": {"min_chars": 2500, "target_chars": 2700, "max_tokens": 6000},
    "프리미엄 BGN (3,000자)": {"min_chars": 3000, "target_chars": 3200, "max_tokens": 7000},
}

# 블로그 관련 추가 설정
BLOG_CONFIG = {
    "default_style": "따뜻하고 담백한 의료 에세이",
    "default_length": "표준 BGN (2,000자)",
}

# ───────────────────── 이미지 생성 기본값 ─────────────────────
IMAGE_CONFIG = {
    "n": 4,
    "size": "1024x1024",
    "allow_seed": True,
}

# ───────────────────── 워드프레스 ─────────────────────
WORDPRESS_CONFIG = {
    "endpoint": get_config_value("WP_ENDPOINT", "").rstrip("/"),
    "username": get_config_value("WP_USERNAME", ""),
    "application_password": get_config_value("WP_APP_PASSWORD", ""),
    "default_status": get_config_value("WP_DEFAULT_STATUS", "draft"),
    "default_categories": ["BGN 블로그"],
    "default_tags": [],
}