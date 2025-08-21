# config.py
# 전역 설정 및 워크플로우 스텝 정보

import os

# --- 앱/파일 업로드 관련 설정 ---
FILE_CONFIG = {
    "upload_dir": "uploads",
    "allowed_exts": [".pdf", ".docx", ".txt", ".md"],
    "max_mb": 25,
}

# --- OpenAI / 이미지 등 API 키 로딩 ---
# 환경변수에서 불러오되, 값이 없으면 빈 문자열로 둡니다.
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
IMAGE_API_KEY = os.environ.get("IMAGE_API_KEY", "")

# 모델 설정(필요 시 앱 내부에서 사용)
LLM_MODEL = os.environ.get("LLM_MODEL", "gpt-4o-mini")
LLM_TEMPERATURE = float(os.environ.get("LLM_TEMPERATURE", "0.4"))

# --- 워크플로우 단계 정의 ---
# key: 내부 라우팅/상태 키, label: UI에 보일 이름
STEP_INFO = [
    {"key": "file_upload",        "label": "파일 업로드"},
    {"key": "material_analysis",  "label": "소재 분석"},
    {"key": "blog_writer",        "label": "블로그 작성"},
    {"key": "image_generator",    "label": "이미지 생성"},
    {"key": "wordpress_publish",  "label": "워드프레스 발행"},
]

# 편의 상수
TOTAL_STEPS = len(STEP_INFO)
