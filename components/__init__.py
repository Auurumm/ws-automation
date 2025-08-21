# BGN 밝은눈안과 블로그 자동화 시스템 - Components 모듈

"""
Streamlit UI 컴포넌트들을 제공하는 모듈입니다.

포함된 컴포넌트:
- file_upload: 인터뷰 파일 업로드 페이지
- material_analysis: 콘텐츠 소재 분석 페이지
- blog_writer: 블로그 작성 페이지
- image_generator: 이미지 생성 페이지
- wordpress_publisher: 워드프레스 발행 페이지
"""

__version__ = "1.0.0"
__author__ = "BGN Blog Automation Team"

# 각 컴포넌트의 렌더링 함수들을 직접 import 할 수 있도록 설정
from .file_upload import render_file_upload_page
from .material_analysis import render_material_analysis_page
from .blog_writer import render_blog_writer_page
from .image_generator import render_image_generator_page
from .wordpress_publisher import render_wordpress_publisher_page

__all__ = [
    'render_file_upload_page',
    'render_material_analysis_page',
    'render_blog_writer_page', 
    'render_image_generator_page',
    'render_wordpress_publisher_page'
]