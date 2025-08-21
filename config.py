# config.py
import os

# ───────────────────── 기본 앱 설정 ─────────────────────
APP_CONFIG = {
    "page_title": "BGN 블로그 자동화",
    "page_icon": "🩺",
    "layout": "wide",
    "sidebar_state": "expanded",
    "main_title": "BGN 밝은눈안과 블로그 자동화",
    "footer_text": "© BGN 밝은눈안과",
}

# 진행 단계(세션/네비게이션에서 사용)
STEP_INFO = [
    "① 인터뷰 업로드",
    "② 소재 분석",
    "③ 글쓰기",
    "④ 이미지 생성",
    "⑤ 워드프레스 발행",
]

# ───────────────────── OpenAI / 모델 ─────────────────────
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

OPENAI_CONFIG = {
    "model": OPENAI_MODEL,
    "api_key": OPENAI_API_KEY,
}

# ───────────────────── 파일 처리 ─────────────────────
FILE_CONFIG = {
    # 인터뷰 분석 시 최대 분석 길이(문자). 너무 길면 토큰 초과/속도 저하.
    "max_chars_for_analysis": 15000,
    "allowed_exts": [".txt", ".md", ".docx", ".pdf"],
}

# ───────────────────── UI 탭 키 (필수: 코드와 1:1 매칭) ─────────────────────
# utils/ai_analyzer.py, components/material_analysis.py가 이 정확한 문자열을 기대합니다.
CONTENT_TYPES = [
    "BGN 환자 에피소드형",
    "BGN 검사·과정형",
    "BGN 센터 운영/분위기형",
    "BGN 직원 성장기형",
    "BGN 환자 질문 FAQ형",
]

# ───────────────────── 블로그 길이/품질 프리셋 ─────────────────────
QUALITY_CONFIG = {
    "표준 BGN (2,000자)": {"min_chars": 2000, "target_chars": 2200, "max_tokens": 4500},
    "고품질 BGN (2,500자)": {"min_chars": 2500, "target_chars": 2700, "max_tokens": 6000},
    "프리미엄 BGN (3,000자)": {"min_chars": 3000, "target_chars": 3200, "max_tokens": 7000},
}

# ───────────────────── 이미지 생성 기본값 ─────────────────────
IMAGE_CONFIG = {
    "n": 4,                  # 한 번에 추천할 이미지 개수
    "size": "1024x1024",
    "allow_seed": True,      # 시드 기반 변주 허용(중복 방지에 도움)
}

# ───────────────────── 워드프레스 발행 ─────────────────────
# KeyError 방지 위해 기본 카테고리/태그 반드시 포함
WORDPRESS_CONFIG = {
    "endpoint": os.getenv("WP_ENDPOINT", "").rstrip("/"),   # 예: https://example.com/wp-json/wp/v2
    "username": os.getenv("WP_USERNAME", ""),
    "application_password": os.getenv("WP_APP_PASSWORD", ""),
    "default_status": os.getenv("WP_DEFAULT_STATUS", "draft"),
    "default_categories": ["BGN 블로그"],                   # ← 필수(없으면 KeyError)
    "default_tags": [],                                     # 필요 시 기본 태그 추가 가능
}
