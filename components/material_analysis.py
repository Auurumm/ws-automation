# components/material_analysis.py
import streamlit as st
from utils.session_manager import previous_step, next_step
from utils.ai_analyzer import AIAnalyzer
from config import CONTENT_TYPES

def render_material_analysis_page():
    """2단계: 소재 분석 페이지"""
    
    st.header("2️⃣ 소재 분석")
    
    # 업로드된 파일 확인
    if not st.session_state.uploaded_files:
        st.warning("업로드된 파일이 없습니다.")
        if st.button("⬅️ 파일 업로드로 돌아가기", use_container_width=True):
            previous_step()
        return
    
    # 분석 시작
    if not st.session_state.analysis_results:
        display_file_info()
        start_analysis()
    else:
        display_analysis_results()
        select_material()

def display_file_info():
    """업로드된 파일 정보 표시"""
    st.subheader("📄 업로드된 파일")
    
    for i, file in enumerate(st.session_state.uploaded_files):
        with st.expander(f"📄 {file.name}", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                file_size = getattr(file, 'size', 0) / 1024 / 1024
                st.write(f"**크기**: {file_size:.2f} MB")
                st.write(f"**형식**: {getattr(file, 'type', 'unknown')}")
            
            with col2:
                # 파일 내용 미리보기
                try:
                    if hasattr(file, 'read'):
                        content = file.read()
                        if isinstance(content, bytes):
                            content = content.decode('utf-8')
                        elif hasattr(content, 'decode'):
                            content = content.decode('utf-8')
                        else:
                            content = str(content)
                        
                        preview = content[:300] + "..." if len(content) > 300 else content
                        st.text_area(
                            f"미리보기",
                            preview,
                            height=100,
                            disabled=True,
                            key=f"preview_{i}"
                        )
                except Exception as e:
                    st.warning(f"미리보기 불가: {str(e)}")

def start_analysis():
    """분석 시작"""
    st.subheader("🤖 AI 소재 분석")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🚀 AI 분석 시작", type="primary", use_container_width=True):
            if not st.session_state.get('openai_api_key'):
                st.error("❌ OpenAI API 키를 먼저 입력해주세요")
            else:
                run_ai_analysis()
    
    with col2:
        if st.button("🎯 샘플 분석 결과 사용", use_container_width=True):
            use_sample_analysis()

def run_ai_analysis():
    """AI 분석 실행"""
    with st.spinner("🤖 AI가 콘텐츠 소재를 분석하고 있습니다..."):
        try:
            # 파일 내용 읽기
            all_content = ""
            for file in st.session_state.uploaded_files:
                try:
                    if hasattr(file, 'read'):
                        content = file.read()
                        if isinstance(content, bytes):
                            content = content.decode('utf-8')
                        elif hasattr(content, 'decode'):
                            content = content.decode('utf-8')
                        else:
                            content = str(content)
                        all_content += f"\n\n=== {file.name} ===\n{content}"
                except Exception as e:
                    st.warning(f"{file.name} 읽기 실패: {str(e)}")
            
            # AI 분석 실행
            analyzer = AIAnalyzer(st.session_state.get('openai_api_key'))
            results = analyzer.analyze_interview_content_keyword_based(all_content)
            
            st.session_state.analysis_results = results
            st.success("✅ 분석이 완료되었습니다!")
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ 분석 중 오류 발생: {str(e)}")
            st.warning("💡 샘플 분석 결과를 사용해보세요.")

def use_sample_analysis():
    """샘플 분석 결과 사용"""
    sample_results = {
        "BGN 환자 에피소드형": [
            {
                "title": "BGN 검안사가 본 20대 직장인의 라식 여정 - 안경에서 자유로워지기까지",
                "content": "매일 아침 안경을 찾는 일상, 운동 중 흘러내리는 안경, 마스크 김서림의 불편함. 20대 직장인 분이 라식 상담을 받으러 오셨는데, 마스크 때문에 안경 김이 서려서 너무 불편하다고 하시더라고요. 이런 분들이 정말 많으세요. 특히 요즘 마스크 때문에 더 심해진 것 같아요.",
                "keywords": ["BGN", "20대", "직장인", "라식", "안경", "불편함", "마스크", "일상"],
                "timestamp": "상담 초반",
                "usage_point": "검안사 시점에서 공감대 형성 후 자연스러운 해결책 제시",
                "staff_perspective": "검안사",
                "target_audience": "예비 환자",
                "direct_quote": "마스크 때문에 안경 김이 서려서 너무 불편했어요",
                "source_quote": "마스크 때문에 안경 김이 서려서 너무 불편하다고 하시더라고요",
                "evidence_span": [85, 120],
                "bgn_brand_fit": "일상의 불편함을 이해하는 따뜻함",
                "emotion_tone": "공감과 이해"
            }
        ],
        "BGN 검사·과정형": [
            {
                "title": "BGN 간호사가 말하는 첫 수술 전 상담의 중요성",
                "content": "처음 수술을 받으시는 분들은 정말 많이 긴장하세요. 손이 떨리시는 분도 계시고, 계속 질문을 하시는 분도 계시죠. 그럴 때는 차근차근 설명해드리고 옆에서 계속 말씀드려요. 그러면 점점 안정되시더라고요.",
                "keywords": ["BGN", "간호사", "첫 수술", "상담", "긴장", "안정", "설명", "과정"],
                "timestamp": "수술 전 상담",
                "usage_point": "간호사의 세심한 케어 과정을 통한 신뢰감 형성",
                "staff_perspective": "간호사",
                "target_audience": "예비 환자",
                "direct_quote": "차근차근 설명해드리고 옆에서 계속 말씀드려요",
                "source_quote": "차근차근 설명해드리고 옆에서 계속 말씀드려요",
                "evidence_span": [78, 105],
                "bgn_brand_fit": "전문성과 따뜻한 케어의 조화",
                "emotion_tone": "안정감과 신뢰"
            }
        ],
        "BGN 센터 운영/분위기형": [
            {
                "title": "BGN에서 느끼는 특별한 분위기 - 환자와 직원이 함께 만드는 공간",
                "content": "저희 BGN은 단순한 병원이 아니라 환자분들과 소통하는 공간이라고 생각해요. 환자분들도 처음에는 어색해하시는데, 대화를 나누다 보면 점점 편해지시더라고요. 그런 순간들이 정말 좋아요.",
                "keywords": ["BGN", "분위기", "소통", "공간", "편안함", "대화", "관계", "병원"],
                "timestamp": "일상적 상담",
                "usage_point": "BGN만의 특별한 분위기와 환자 중심 서비스 강조",
                "staff_perspective": "전체 직원",
                "target_audience": "잠재 환자",
                "direct_quote": "대화를 나누다 보면 점점 편해지시더라고요",
                "source_quote": "대화를 나누다 보면 점점 편해지시더라고요",
                "evidence_span": [95, 120],
                "bgn_brand_fit": "친근하고 편안한 의료 환경",
                "emotion_tone": "따뜻함과 편안함"
            }
        ]
    }
    
    st.session_state.analysis_results = sample_results
    st.success("✅ 샘플 분석 결과가 로드되었습니다!")
    st.rerun()

def display_analysis_results():
    """분석 결과 표시"""
    st.subheader("📊 분석 결과")
    
    total_materials = sum(len(materials) for materials in st.session_state.analysis_results.values())
    st.info(f"총 {total_materials}개의 콘텐츠 소재가 추출되었습니다.")
    
    # 탭으로 카테고리별 표시
    tabs = st.tabs(list(st.session_state.analysis_results.keys()))
    
    for i, (category, materials) in enumerate(st.session_state.analysis_results.items()):
        with tabs[i]:
            if materials:
                st.write(f"**{len(materials)}개 소재**")
                
                for j, material in enumerate(materials):
                    with st.expander(f"📝 {material['title']}", expanded=False):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write(f"**내용**: {material['content'][:200]}...")
                            st.write(f"**활용 포인트**: {material.get('usage_point', '미지정')}")
                            st.write(f"**대상 독자**: {material.get('target_audience', '일반')}")
                        
                        with col2:
                            keywords = material.get('keywords', [])
                            if keywords:
                                keywords_display = " ".join([f"`{kw}`" for kw in keywords[:6]])
                                st.markdown(f"**키워드**: {keywords_display}")
                            
                            st.write(f"**직원 관점**: {material.get('staff_perspective', '미지정')}")
                            st.write(f"**감정 톤**: {material.get('emotion_tone', '미지정')}")
                        
                        # 선택 버튼
                        if st.button(f"이 소재 선택", key=f"select_{category}_{j}", use_container_width=True):
                            st.session_state.selected_material = {
                                'type': category,
                                'data': material
                            }
                            st.success(f"✅ '{material['title']}'이 선택되었습니다!")
                            time.sleep(1)
                            next_step()
            else:
                st.write("이 카테고리에는 추출된 소재가 없습니다.")

def select_material():
    """소재 선택"""
    if st.session_state.selected_material:
        selected = st.session_state.selected_material
        st.success(f"✅ 선택된 소재: **{selected['type']}** - {selected['data']['title']}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 다른 소재 선택", use_container_width=True):
                st.session_state.selected_material = None
                st.rerun()
        
        with col2:
            if st.button("➡️ 블로그 작성하기", type="primary", use_container_width=True):
                next_step()
    
    # 하단 네비게이션
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("⬅️ 파일 업로드로", use_container_width=True):
            previous_step()
    
    with col2:
        if st.button("🔄 분석 다시 실행", use_container_width=True):
            st.session_state.analysis_results = {}
            st.rerun()