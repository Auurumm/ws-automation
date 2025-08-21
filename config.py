# config.py
# 모든 모듈이 참조하는 '단일 출처(Single Source of Truth)' 구성

import os

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
# 여러 모듈이 'STEP_INFO' 를 import 하므로 반드시 존재해야 합니다.
STEP_INFO = [
    {"key": "file_upload",        "label": "① 파일 업로드"},
    {"key": "material_analysis",  "label": "② 소재 분석"},
    {"key": "blog_writer",        "label": "③ 블로그 작성"},
    {"key": "image_generator",    "label": "④ 이미지 생성"},
    {"key": "wordpress_publish",  "label": "⑤ 워드프레스 발행"},
]

# ───────────────────── OpenAI ─────────────────────
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL   = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

OPENAI_CONFIG = {
    "model": OPENAI_MODEL,
    "api_key": OPENAI_API_KEY,
}

# ───────────────────── 파일 처리 ─────────────────────
FILE_CONFIG = {
    "allowed_exts": [".txt", ".md", ".docx", ".pdf"],
    "accept": ".txt,.md,.docx,.pdf",   # streamlit file_uploader용
    "max_size_mb": 25,
    "max_chars_for_analysis": 15000,   # 인터뷰 분석시 길이 제한
}

# ───────────────────── 콘텐츠 탭 키 (UI와 1:1) ─────────────────────
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

# (옵션) 블로그 관련 추가 설정을 쓰는 모듈이 있다면 여기서 정의
BLOG_CONFIG = {
    "default_style": "따뜻하고 담백한 의료 에세이",
    "default_length": "표준 BGN (2,000자)",
}

# ───────────────────── 이미지 생성 기본값 ─────────────────────
IMAGE_CONFIG = {
    "n": 4,
    "size": "1024x1024",
    "allow_seed": True,  # 시드 변주 허용(중복 방지)
}

# ───────────────────── 워드프레스 ─────────────────────
WORDPRESS_CONFIG = {
    "endpoint": os.getenv("WP_ENDPOINT", "").rstrip("/"),   # 예: https://example.com/wp-json/wp/v2
    "username": os.getenv("WP_USERNAME", ""),
    "application_password": os.getenv("WP_APP_PASSWORD", ""),
    "default_status": os.getenv("WP_DEFAULT_STATUS", "draft"),
    # ↓ 아래 두 키가 없으면 KeyError가 자주 납니다. 반드시 둡니다.
    "default_categories": ["BGN 블로그"],
    "default_tags": [],
}
