# config.py
import os

# ===== OpenAI / 모델 =====
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

OPENAI_CONFIG = {
    "model": OPENAI_MODEL,
    "api_key": OPENAI_API_KEY,
}

# ===== 파일 처리 =====
FILE_CONFIG = {
    "max_chars_for_analysis": 15000,
    "allowed_exts": [".txt", ".md", ".docx", ".pdf"],
}

# ===== UI 탭 키 (utils/ai_analyzer.py, material_analysis.py와 1:1 매칭) =====
CONTENT_TYPES = [
    "BGN 환자 에피소드형",
    "BGN 검사·과정형",
    "BGN 센터 운영/분위기형",
    "BGN 직원 성장기형",
    "BGN 환자 질문 FAQ형",
]

# ===== 블로그 길이 프리셋 =====
QUALITY_CONFIG = {
    "표준 BGN (2,000자)": {"min_chars": 2000, "target_chars": 2200, "max_tokens": 4500},
    "고품질 BGN (2,500자)": {"min_chars": 2500, "target_chars": 2700, "max_tokens": 6000},
    "프리미엄 BGN (3,000자)": {"min_chars": 3000, "target_chars": 3200, "max_tokens": 7000},
}

# ===== 이미지 생성 기본값 =====
IMAGE_CONFIG = {
    "n": 4,
    "size": "1024x1024",
    "allow_seed": True,
}

# ===== 워드프레스 발행 기본값 (KeyError 방지: 기본 카테고리/태그 필수) =====
WORDPRESS_CONFIG = {
    "endpoint": os.getenv("WP_ENDPOINT", ""),         # 예: https://example.com/wp-json/wp/v2
    "username": os.getenv("WP_USERNAME", ""),
    "application_password": os.getenv("WP_APP_PASSWORD", ""),
    "default_status": os.getenv("WP_DEFAULT_STATUS", "draft"),
    "default_categories": ["BGN 블로그"],             # ← 없어서 죽던 부분
    "default_tags": [],
}
