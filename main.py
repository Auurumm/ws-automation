# main.py
import streamlit as st
import os
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

# 컴포넌트 import (안전한 fallback 포함)
try:
    from components.file_upload import render_file_upload_page
except ImportError:
    def render_file_upload_page():
        st.warning("⚠️ file_upload 컴포넌트가 없습니다.")
        st.button("다음 단계", key="next_file", on_click=lambda: setattr(st.session_state, 'step', 2))

try:
    from components.material_analysis import render_material_analysis_page
except ImportError:
    def render_material_analysis_page():
        st.warning("⚠️ material_analysis 컴포넌트가 없습니다.")
        st.button("다음 단계", key="next_analysis", on_click=lambda: setattr(st.session_state, 'step', 3))

try:
    from components.blog_writer import render_blog_writer_page
except ImportError:
    def render_blog_writer_page():
        st.warning("⚠️ blog_writer 컴포넌트가 없습니다.")
        st.button("다음 단계", key="next_blog", on_click=lambda: setattr(st.session_state, 'step', 4))

try:
    from components.image_generator import render_image_generator_page
except ImportError:
    def render_image_generator_page():
        st.warning("⚠️ image_generator 컴포넌트가 없습니다.")
        st.button("다음 단계", key="next_image", on_click=lambda: setattr(st.session_state, 'step', 5))

try:
    from components.wordpress_publisher import render_wordpress_publisher_page
except ImportError:
    def render_wordpress_publisher_page():
        st.warning("⚠️ wordpress_publisher 컴포넌트가 없습니다.")
        st.info("마지막 단계입니다.")

# 유틸리티 import
from utils.session_manager import initialize_session_state, get_all_steps

# 설정 import
try:
    from config import APP_CONFIG
except ImportError:
    APP_CONFIG = {
        "page_title": "BGN 블로그 자동화",
        "page_icon": "🩺",
        "layout": "wide",
        "sidebar_state": "expanded",
        "main_title": "BGN 밝은눈안과 블로그 자동화",
        "footer_text": "© BGN 밝은눈안과",
    }

# auth_manager 안전한 import (없으면 기본 동작)
try:
    from utils.auth_manager import auth_manager
    HAS_AUTH = True
except ImportError:
    HAS_AUTH = False
    class DummyAuth:
        def login(self): return True
        def get_current_user(self): return "사용자"
        def render_user_info(self): st.sidebar.info("로그인 기능 없음")
    auth_manager = DummyAuth()

# 페이지 설정
st.set_page_config(
    page_title=APP_CONFIG["page_title"],
    page_icon=APP_CONFIG["page_icon"],
    layout=APP_CONFIG["layout"],
    initial_sidebar_state=APP_CONFIG["sidebar_state"]
)

def main():
    """메인 앱 함수"""
    # 인증 확인 (있는 경우만)
    if HAS_AUTH and not auth_manager.login():
        return
    
    # 세션 상태 초기화
    initialize_session_state()
    
    # 사이드바 렌더링
    render_sidebar()
    
    # 메인 헤더
    st.title(APP_CONFIG["main_title"])
    
    # 현재 사용자 정보 표시
    current_user = auth_manager.get_current_user()
    st.markdown(f"**환영합니다, {current_user}님!** 👋")
    st.markdown("---")
    
    # 단계별 페이지 렌더링
    if st.session_state.step == 1:
        render_file_upload_page()
    elif st.session_state.step == 2:
        render_material_analysis_page()
    elif st.session_state.step == 3:
        render_blog_writer_page()
    elif st.session_state.step == 4:
        render_image_generator_page()
    elif st.session_state.step == 5:
        render_wordpress_publisher_page()
    
    # 하단 정보
    st.markdown("---")
    st.markdown(f"{APP_CONFIG['footer_text']} | 로그인: {current_user}")

def render_sidebar():
    """사이드바 렌더링"""
    st.sidebar.title("📋 진행 단계")
    
    # 사용자 정보 표시 (인증 기능이 있는 경우)
    if HAS_AUTH:
        auth_manager.render_user_info()
    
    # API 키 설정
    with st.sidebar.expander("⚙️ API 설정", expanded=False):
        # 환경변수에서 API 키 자동 로드
        default_api_key = os.getenv('OPENAI_API_KEY', '')
        
        if default_api_key:
            st.success("✅ 환경변수에서 API 키를 자동으로 로드했습니다")
            st.session_state.openai_api_key = default_api_key
            
            # API 키 변경 옵션
            if st.checkbox("다른 API 키 사용하기"):
                new_api_key = st.text_input(
                    "새 OpenAI API Key", 
                    type="password",
                    help="다른 API 키를 사용하려면 입력하세요",
                    key="new_openai_api_key"
                )
                if new_api_key:
                    st.session_state.openai_api_key = new_api_key
                    st.success("✅ 새 API 키가 설정되었습니다")
        else:
            openai_api_key = st.text_input(
                "OpenAI API Key", 
                type="password",
                help="OpenAI API 키를 입력하세요",
                key="openai_api_key"
            )
            if openai_api_key:
                st.success("✅ API 키가 설정되었습니다")
            else:
                st.warning("⚠️ API 키를 입력하거나 .env 파일에 설정해주세요")
        
        # API 키 저장 안내
        if not default_api_key:
            with st.expander("💡 API 키 자동 로드 설정 방법"):
                st.markdown("""
                **매번 API 키를 입력하지 않으려면:**
                
                1. 프로젝트 폴더에 `.env` 파일 생성
                2. 다음 내용 추가:
                ```
                OPENAI_API_KEY=your_actual_api_key_here
                ```
                3. Streamlit 재시작
                
                ⚠️ **주의**: .env 파일은 Git에 커밋하지 마세요!
                """)
    
    # 진행 단계 표시
    steps = get_all_steps()
    for i, step_label in enumerate(steps, 1):
        if i == st.session_state.step:
            st.sidebar.markdown(f"**🔄 {step_label}**")
        elif i < st.session_state.step:
            st.sidebar.markdown(f"✅ {step_label}")
        else:
            st.sidebar.markdown(f"⏳ {step_label}")
    
    # 단계 이동 버튼
    st.sidebar.markdown("---")
    st.sidebar.markdown("**🎯 빠른 이동**")
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.session_state.step > 1:
            if st.button("⬅️ 이전", use_container_width=True):
                st.session_state.step -= 1
                st.rerun()
    
    with col2:
        if st.session_state.step < 5:
            if st.button("➡️ 다음", use_container_width=True):
                st.session_state.step += 1
                st.rerun()

if __name__ == "__main__":
    main()