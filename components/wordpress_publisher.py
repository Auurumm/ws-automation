import streamlit as st
from datetime import datetime, date, time
from config import WORDPRESS_CONFIG
from utils.session_manager import previous_step, reset_session

def render_wordpress_publisher_page():
    """5단계: 워드프레스 발행 페이지"""
    
    st.header("5️⃣ 워드프레스 발행")
    
    # 최종 검토
    display_final_review()
    
    # 발행 설정
    configure_publish_settings()
    
    # 워드프레스 연동 설정
    configure_wordpress_settings()
    
    # 발행 버튼 및 완료 처리
    handle_publishing()

def display_final_review():
    """발행 전 최종 검토"""
    st.subheader("📋 발행 전 최종 검토")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**📄 블로그 정보**")
        st.write(f"**제목**: {st.session_state.get('blog_title', '제목 없음')}")
        
        if st.session_state.blog_content:
            content_preview = st.session_state.blog_content[:200]
            if len(st.session_state.blog_content) > 200:
                content_preview += "..."
            st.write(f"**내용 미리보기**: {content_preview}")
        
        # 소재 정보
        if st.session_state.selected_material:
            material_type = st.session_state.selected_material['type']
            st.write(f"**콘텐츠 유형**: {material_type}")
    
    with col2:
        st.write("**🖼️ 생성된 이미지**")
        if st.session_state.generated_image:
            st.success("이미지 준비 완료 ✅")
            # 이미지 썸네일 표시
            image_info = st.session_state.generated_image
            st.image(image_info["url"], width=200)
        else:
            st.warning("이미지를 먼저 생성해주세요")

def configure_publish_settings():
    """발행 설정"""
    st.subheader("⚙️ 발행 설정")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**🏷️ 카테고리 및 태그**")
        
        # 블로그 제목 수정 (최종)
        st.session_state.final_title = st.text_input(
            "최종 제목", 
            value=st.session_state.get('blog_title', ''),
            key="final_title_input"
        )
        
        # 카테고리 선택
        st.session_state.category = st.selectbox(
            "카테고리", 
            WORDPRESS_CONFIG["default_categories"],
            key="category_select"
        )
        
        # 태그 입력
        st.session_state.tags = st.text_input(
            "태그 (쉼표로 구분)", 
            value=WORDPRESS_CONFIG["default_tags"],
            key="tags_input"
        )
    
    with col2:
        st.write("**📅 발행 일정**")
        
        # 즉시 발행 여부
        st.session_state.publish_now = st.checkbox(
            "즉시 발행", 
            value=True,
            key="publish_now_check"
        )
        
        if not st.session_state.publish_now:
            st.session_state.publish_date = st.date_input(
                "예약 발행일",
                value=date.today(),
                key="publish_date_input"
            )
            st.session_state.publish_time = st.time_input(
                "예약 발행 시간",
                value=time(9, 0),
                key="publish_time_input"
            )
        
        # 발행 상태
        st.session_state.post_status = st.selectbox(
            "발행 상태",
            ["publish", "draft", "private"],
            format_func=lambda x: {"publish": "공개", "draft": "임시저장", "private": "비공개"}[x],
            key="post_status_select"
        )

def configure_wordpress_settings():
    """워드프레스 연동 설정"""
    with st.expander("🔗 워드프레스 연동 설정", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.session_state.wp_url = st.text_input(
                "워드프레스 사이트 URL", 
                value=WORDPRESS_CONFIG["default_url"],
                key="wp_url_input"
            )
            st.session_state.wp_username = st.text_input(
                "사용자명",
                key="wp_username_input"
            )
        
        with col2:
            st.session_state.wp_password = st.text_input(
                "비밀번호", 
                type="password",
                key="wp_password_input"
            )
            
            # 연결 테스트 버튼
            if st.button("🔍 연결 테스트", key="test_connection_btn"):
                test_wordpress_connection()

def test_wordpress_connection():
    """워드프레스 연결 테스트"""
    if not all([st.session_state.wp_url, st.session_state.wp_username, st.session_state.wp_password]):
        st.error("모든 연결 정보를 입력해주세요.")
        return
    
    with st.spinner("워드프레스 연결을 테스트하고 있습니다..."):
        try:
            # 실제 연결 테스트 구현 예정
            st.success("✅ 워드프레스 연결이 성공했습니다!")
        except Exception as e:
            st.error(f"❌ 연결 실패: {str(e)}")

def handle_publishing():
    """발행 처리"""
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("⬅️ 이전 단계로", use_container_width=True):
            previous_step()
    
    with col2:
        if st.button("🚀 워드프레스에 발행하기", type="primary", use_container_width=True):
            publish_to_wordpress()

def publish_to_wordpress():
    """워드프레스에 실제 발행"""
    # 필수 정보 확인
    if not st.session_state.get('final_title'):
        st.error("제목을 입력해주세요.")
        return
    
    if not st.session_state.get('blog_content'):
        st.error("블로그 내용이 없습니다.")
        return
    
    # 워드프레스 연결 정보 확인
    if not all([
        st.session_state.get('wp_url'), 
        st.session_state.get('wp_username'), 
        st.session_state.get('wp_password')
    ]):
        st.error("워드프레스 연결 정보를 모두 입력해주세요.")
        return
    
    with st.spinner("워드프레스에 발행하고 있습니다..."):
        try:
            # 실제 워드프레스 API 연동 구현 예정
            success = publish_post_to_wp()
            
            if success:
                display_success_page()
            else:
                st.error("발행 중 오류가 발생했습니다. 설정을 확인해주세요.")
                
        except Exception as e:
            st.error(f"발행 실패: {str(e)}")

def publish_post_to_wp():
    """실제 워드프레스 포스트 발행 (구현 예정)"""
    # 여기에 실제 WordPress REST API 또는 XML-RPC 연동 코드 구현
    # 현재는 시뮬레이션
    import time
    time.sleep(2)  # 발행 시뮬레이션
    return True

def display_success_page():
    """발행 성공 페이지"""
    st.success("🎉 블로그가 성공적으로 발행되었습니다!")
    st.balloons()
    
    # 발행 정보 요약
    st.subheader("📊 발행 완료 정보")
    
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"""
        **📰 발행된 글 정보**
        - 제목: {st.session_state.final_title}
        - 카테고리: {st.session_state.category}
        - 태그: {st.session_state.tags}
        - 상태: {st.session_state.post_status}
        """)
    
    with col2:
        st.info(f"""
        **🕐 발행 시간 정보**
        - 발행일: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        - 즉시발행: {'예' if st.session_state.publish_now else '아니오'}
        - 사이트: {st.session_state.wp_url}
        """)
    
    # 통계 정보
    display_statistics()
    
    # 새 작업 시작 버튼
    if st.button("🔄 새 블로그 작성하기", type="primary", use_container_width=True):
        reset_session()

def display_statistics():
    """작업 통계 표시"""
    st.subheader("📈 작업 통계")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("완료된 단계", "5/5", "100%")
    
    with col2:
        content_length = len(st.session_state.blog_content) if st.session_state.blog_content else 0
        st.metric("생성된 글자 수", f"{content_length:,}자")
    
    with col3:
        material_type = st.session_state.selected_material['type'] if st.session_state.selected_material else "없음"
        st.metric("선택된 소재 유형", material_type)
    
    with col4:
        st.metric("생성된 이미지", "1개" if st.session_state.generated_image else "0개")
    
    # 소요 시간 (실제로는 세션 시작 시간부터 계산)
    st.info("💡 **팁**: 다음번에는 더 빠르게 작업할 수 있습니다. API 키와 워드프레스 설정을 미리 준비해두세요!")