# components/file_upload.py
import streamlit as st
from utils.session_manager import next_step
from config import FILE_CONFIG

def render_file_upload_page():
    """1단계: 파일 업로드 페이지"""
    
    st.header("1️⃣ 파일 업로드")
    st.markdown("인터뷰 파일이나 콘텐츠 소재를 업로드해주세요.")
    
    # 파일 업로드
    uploaded_files = st.file_uploader(
        "파일을 업로드하세요",
        type=["txt", "md", "docx", "pdf"],
        accept_multiple_files=True,
        help=f"지원 형식: {', '.join(FILE_CONFIG['allowed_exts'])}"
    )
    
    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)}개 파일이 업로드되었습니다!")
        
        # 업로드된 파일 정보 표시
        for i, file in enumerate(uploaded_files):
            with st.expander(f"📄 {file.name}", expanded=False):
                file_size = file.size / 1024 / 1024  # MB
                st.write(f"**크기**: {file_size:.2f} MB")
                st.write(f"**형식**: {file.type}")
                
                # 텍스트 파일인 경우 미리보기
                if file.name.endswith(('.txt', '.md')):
                    try:
                        content = str(file.read(), "utf-8")
                        file.seek(0)  # 파일 포인터 리셋
                        st.text_area(
                            f"미리보기 ({file.name})", 
                            content[:500] + "..." if len(content) > 500 else content,
                            height=100,
                            disabled=True
                        )
                    except:
                        st.warning("텍스트 미리보기를 할 수 없습니다.")
        
        # 세션에 저장
        st.session_state.uploaded_files = uploaded_files
        
        # 다음 단계로 이동
        if st.button("➡️ 소재 분석 시작", type="primary", use_container_width=True):
            next_step()
    
    else:
        st.info("파일을 업로드하여 시작하세요.")
        
        # 샘플 파일 옵션
        with st.expander("💡 샘플 파일로 테스트하기"):
            if st.button("📝 샘플 인터뷰 파일 생성", use_container_width=True):
                create_sample_file()
                next_step()

def create_sample_file():
    """샘플 파일 생성"""
    sample_content = """
BGN 밝은눈안과 직원 인터뷰 - 검안사 김서연

Q: 오늘 기억에 남는 환자분이 계셨나요?

A: 네, 20대 직장인 분이 오셨어요. 라식 상담을 받으러 오셨는데, 마스크 때문에 안경 김이 서려서 너무 불편했다고 하시더라고요. 매일 아침 안경 찾는 것도 스트레스고, 운동할 때도 계속 흘러내려서 불편하다고 하시면서요.

Q: 그런 분들이 많으신가요?

A: 정말 많으세요. 특히 요즘 마스크 때문에 더 심해진 것 같아요. 하루 종일 마스크를 써야 하니까 안경 쓰시는 분들은 정말 답답하실 거예요. 그래서 라식을 고려하시는 분들이 늘어나고 있는 것 같아요.

Q: 상담할 때 어떤 점을 중요하게 생각하시나요?

A: 환자분의 마음을 이해하려고 노력해요. 처음 오시는 분들은 정말 많이 긴장하시거든요. 손이 떨리시는 분도 계시고, 계속 질문을 하시는 분도 계시고요. 그럴 때는 차근차근 설명해드리고 옆에서 계속 말씀드려요. 그러면 점점 안정되시더라고요.

Q: 보람을 느끼는 순간은 언제인가요?

A: 며칠 후에 연락이 올 때가 가장 보람있어요. 오늘 그 분도 전화를 주셨는데 "선생님, 정말 신세계네요!" 하시면서 너무 좋아하시더라고요. 그런 말씀을 들으면 정말 이 일을 하길 잘했다는 생각이 들어요.

Q: 마지막으로 하고 싶은 말씀이 있다면?

A: 비슷한 고민을 하고 계신 분들이 너무 오래 혼자 끙끙 앓지 마셨으면 좋겠어요. 작은 것이라도 궁금한 게 있으시면 편하게 연락주세요. 저희가 항상 여기 있으니까요.
"""
    
    # 샘플 파일을 세션에 저장
    class SampleFile:
        def __init__(self, name, content):
            self.name = name
            self.content = content
            self.size = len(content.encode('utf-8'))
            self.type = "text/plain"
            
        def read(self):
            return self.content.encode('utf-8')
    
    sample_file = SampleFile("sample_interview.txt", sample_content)
    st.session_state.uploaded_files = [sample_file]
    
    st.success("✅ 샘플 인터뷰 파일이 생성되었습니다!")
    st.info("다음 단계로 넘어가서 소재 분석을 시작하세요.")