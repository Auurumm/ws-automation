import streamlit as st
from config import CONTENT_TYPES
from utils.session_manager import previous_step, next_step
from utils.ai_analyzer import AIAnalyzer, get_sample_materials

def render_material_analysis_page():
    """2단계: 콘텐츠 소재 도출 페이지"""
    
    st.header("2️⃣ 콘텐츠 소재 도출")
    
    # 업로드된 파일 정보
    st.info(f"📁 분석 대상: {st.session_state.interview_file}")
    
    # 소재 도출 가이드라인 표시
    with st.expander("📋 소재 도출 가이드라인", expanded=False):
        st.markdown("**🎯 콘텐츠 유형 분류:**")
        
        for type_name, info in CONTENT_TYPES.items():
            st.markdown(f"**{info['icon']} {type_name}**: {info['description']}")
        
        st.markdown("\n각 유형별로 최소 2개 이상의 구체적 소재를 시간대 정보와 함께 도출합니다.")
    
    # AI 분석 버튼
    if st.button("🤖 AI로 콘텐츠 소재 분석하기", type="primary"):
        if not st.session_state.get('openai_api_key'):
            st.error("❌ OpenAI API 키를 먼저 입력해주세요")
        else:
            st.session_state.analysis_started = True
            analyze_content_with_ai()
    
    # 샘플 데이터 버튼 (테스트용)
    if st.button("🎯 샘플 소재로 테스트하기", help="테스트용 샘플 소재 데이터를 로드합니다"):
        st.session_state.content_materials = get_sample_materials()
        st.success("✅ 샘플 소재가 로드되었습니다!")
    
    # 도출된 소재 표시
    if st.session_state.content_materials:
        display_analyzed_materials()
        
        # 하단 버튼들
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ 이전 단계로", use_container_width=True):
                previous_step()
        with col2:
            if st.button("🔄 소재 재분석", use_container_width=True):
                st.session_state.content_materials = {}
                st.rerun()
    else:
        # 소재가 없을 때 이전 단계 버튼만
        if st.button("⬅️ 이전 단계로", use_container_width=True):
            previous_step()

def analyze_content_with_ai():
    """AI를 사용하여 콘텐츠 분석"""
    
    # 분석 진행 상태 체크
    if not hasattr(st.session_state, 'analysis_in_progress'):
        st.session_state.analysis_in_progress = False
    
    if st.session_state.analysis_in_progress:
        with st.spinner("인터뷰 내용을 분석하여 콘텐츠 소재를 도출하고 있습니다..."):
            try:
                analyzer = AIAnalyzer(st.session_state.get('openai_api_key'))
                materials = analyzer.analyze_interview_content(st.session_state.interview_content)
                
                if materials:  # 분석 결과가 있을 때만 저장
                    st.session_state.content_materials = materials
                    st.success("✅ 콘텐츠 소재 분석이 완료되었습니다!")
                    st.session_state.analysis_in_progress = False
                    st.rerun()
                
            except Exception as e:
                error_msg = str(e)
                
                # API 할당량 초과 오류 처리
                if "insufficient_quota" in error_msg or "429" in error_msg:
                    st.error("💳 **OpenAI API 할당량이 초과되었습니다**")
                    st.warning("""
                    **해결 방법:**
                    1. [OpenAI Platform](https://platform.openai.com/usage)에서 사용량 확인
                    2. 결제 정보 추가 또는 한도 증액
                    3. 아래 '샘플 소재로 테스트하기' 버튼으로 계속 진행 가능
                    """)
                elif "context_length_exceeded" in error_msg:
                    st.error("📏 **텍스트가 너무 길어서 토큰 한계를 초과했습니다**")
                    st.info("위에서 다른 분석 방법을 선택해보세요.")
                elif "401" in error_msg or "invalid" in error_msg.lower():
                    st.error("🔑 **API 키가 올바르지 않습니다**")
                    st.warning("사이드바에서 올바른 OpenAI API 키를 입력해주세요.")
                else:
                    st.error(f"❌ 분석 중 오류가 발생했습니다: {str(e)}")
                
                # 항상 샘플 데이터로 진행 가능하도록
                st.info("💡 **샘플 데이터로 계속 진행하시려면** 아래 '샘플 소재로 테스트하기' 버튼을 클릭해주세요.")
                st.session_state.analysis_in_progress = False
    
    else:
        # 분석 시작 버튼이 클릭되면 분석 모드로 전환
        if 'analysis_started' in st.session_state and st.session_state.analysis_started:
            st.session_state.analysis_in_progress = True
            st.session_state.analysis_started = False
            st.rerun()

def display_analyzed_materials():
    """분석된 소재들을 표시"""
    st.subheader("🎯 도출된 콘텐츠 소재")
    
    # 탭으로 유형별 구분
    tab_names = []
    tab_objects = []
    
    for type_name, info in CONTENT_TYPES.items():
        tab_names.append(f"{info['icon']} {type_name.replace('형', '')}")
    
    tabs = st.tabs(tab_names)
    
    for i, (type_name, info) in enumerate(CONTENT_TYPES.items()):
        with tabs[i]:
            display_material_type(type_name, info)

def display_material_type(material_type, type_info):
    """특정 유형의 소재들을 표시"""
    if material_type in st.session_state.content_materials:
        materials = st.session_state.content_materials[material_type]
        
        if materials:
            st.markdown(f"**📝 {type_info['description']}**")
            st.markdown("---")
            
            for i, material in enumerate(materials):
                with st.container():
                    # 소재 카드 스타일
                    col1, col2 = st.columns([4, 1])
                    
                    with col1:
                        st.markdown(f"### 💡 소재 {i+1}: {material['title']}")
                        st.write(f"**📋 내용**: {material['content']}")
                        st.write(f"**⏰ 시간대**: {material['timestamp']}")
                        st.write(f"**🎯 활용 포인트**: {material['usage_point']}")
                    
                    with col2:
                        # 선택 버튼
                        if st.button(
                            "이 소재 선택", 
                            key=f"select_{material_type}_{i}",
                            type="primary",
                            use_container_width=True
                        ):
                            select_material(material_type, material)
                    
                    st.markdown("---")
        else:
            st.info("해당 유형의 소재가 발견되지 않았습니다.")
    else:
        st.info("해당 유형의 소재가 발견되지 않았습니다.")

def select_material(material_type, material):
    """소재를 선택하고 다음 단계로 이동"""
    st.session_state.selected_material = {
        'type': material_type,
        'data': material
    }
    
    # 선택 완료 메시지
    st.success(f"✅ '{material['title']}' 소재가 선택되었습니다!")
    
    # 잠시 후 다음 단계로 이동
    st.balloons()
    next_step()