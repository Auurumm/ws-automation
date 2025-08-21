# config.py
from collections import OrderedDict
import os

__all__ = [
    "APP_NAME",
    "FILE_CONFIG",
    "STEP_INFO",
    "OPENAI_MODEL",
    "ENV_VARS_REQUIRED",
]

# 앱 이름
APP_NAME = "BGN 블로그 자동화"

# 업로드 파일 설정
FILE_CONFIG = {
    "allowed_exts": [".txt", ".md", ".docx", ".pdf"],
    "max_size_mb": 20,
    # Streamlit file_uploader accept param용 (문자열)
    "accept": ".txt,.md,.docx,.pdf",
}

# 단계(라우팅) 정의: key 순서가 곧 진행 순서입니다.
# components/*.py 에서 이 key를 기반으로 next_step() 등이 동작합니다.
STEP_INFO = OrderedDict(
    [
        ("upload", {"index": 0, "title": "파일 업로드"}),
        ("material", {"index": 1, "title": "소재 분석"}),
        ("blog", {"index": 2, "title": "블로그 초안"}),
        ("image", {"index": 3, "title": "이미지 생성"}),
        ("publish", {"index": 4, "title": "워드프레스 발행"}),
    ]
)

# OpenAI 모델(원하시는 모델명으로 교체 가능)
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# 필수 환경변수 점검용(부족해도 앱은 켜지지만 경고 띄울 때 사용)
ENV_VARS_REQUIRED = [
    "OPENAI_API_KEY",        # OpenAI
    "WP_BASE_URL",           # WordPress
    "WP_USERNAME",
    "WP_APP_PASSWORD",
]
