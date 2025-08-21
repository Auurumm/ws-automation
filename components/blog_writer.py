import streamlit as st
from config import BLOG_CONFIG, QUALITY_CONFIG
from utils.session_manager import previous_step, next_step
from utils.ai_analyzer import AIAnalyzer
import time

def render_blog_writer_page():
    """3단계: 소재 선택 및 블로그 작성 페이지 (BGN 톤앤매너 적용)"""
    
    st.header("3️⃣ 소재 선택 및 블로그 작성")
    
    # 선택된 소재 정보 표시
    if st.session_state.selected_material:
        display_selected_material()
        configure_blog_settings()
        generate_blog_content()
    else:
        st.warning("먼저 콘텐츠 소재를 선택해주세요.")
        if st.button("⬅️ 소재 선택으로 돌아가기", use_container_width=True):
            previous_step()

def display_selected_material():
    """선택된 소재 정보 표시"""
    material = st.session_state.selected_material['data']
    material_type = st.session_state.selected_material['type']
    
    st.success(f"📌 선택된 소재: **{material_type}** - {material['title']}")
    
    with st.expander("📋 선택된 소재 상세 정보", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**📋 내용**: {material['content']}")
            st.write(f"**⏰ 시간대**: {material['timestamp']}")
            st.write(f"**🎯 활용 포인트**: {material['usage_point']}")
        
        with col2:
            # 키워드 정보
            if 'keywords' in material:
                keywords_display = " ".join([f"`{kw}`" for kw in material['keywords'][:8]])
                st.markdown(f"**🏷️ 키워드**: {keywords_display}")
            
            if 'target_audience' in material:
                st.write(f"**👥 대상 독자**: {material['target_audience']}")
            
            if 'direct_quote' in material and material['direct_quote']:
                st.info(f"💬 **직접 인용**: \"{material['direct_quote']}\"")

def configure_blog_settings():
    """블로그 작성 설정 (BGN 톤앤매너 중심)"""
    st.subheader("📝 블로그 작성 설정")
    
    st.info("💡 **모든 블로그는 BGN 고유의 자연스러운 톤앤매너로 2,000자 이상 작성됩니다**")
    
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.blog_style = st.selectbox(
            "작성 스타일",
            [
                "검안사의 일상 경험담 (친근한 1인칭)",
                "간호사의 따뜻한 케어 스토리",
                "원무팀의 고객 응대 에피소드",
                "의료진의 전문적이면서도 따뜻한 조언"
            ],
            key="blog_style_select"
        )
        
        # 직무별 화자 설정
        staff_roles = {
            "검안사의 일상 경험담": ("검안사", "김서연"),
            "간호사의 따뜻한 케어": ("간호사", "박지현"),
            "원무팀의 고객 응대": ("원무팀", "이미소"),
            "의료진의 전문적이면서도": ("의료진", "정하늘")
        }
        
        for key, (role, name) in staff_roles.items():
            if key in st.session_state.blog_style:
                st.session_state.staff_role = role
                st.session_state.staff_name = name
                break
    
    with col2:
        # 품질 옵션
        quality_options = [
            "표준 품질 (2,000자 이상)",
            "고품질 (2,500자 이상)", 
            "프리미엄 (3,000자 이상)"
        ]
        st.session_state.content_length = st.selectbox(
            "콘텐츠 품질", 
            quality_options,
            key="content_length_select"
        )
        
        # BGN 톤앤매너 특성 체크박스
        st.markdown("**🎯 BGN 톤앤매너 특성**")
        st.session_state.use_emotions = st.checkbox("감정 표현 사용 (:), ㅠㅠ, ... 등)", value=True)
        st.session_state.use_casual_talk = st.checkbox("자연스러운 구어체 혼용", value=True)
        st.session_state.use_empathy = st.checkbox("담담한 공감 톤", value=True)
    
    # 추가 요청사항
    st.session_state.additional_request = st.text_area(
        "추가 요청사항 (선택사항)",
        height=100,
        placeholder="예: 특정 에피소드 강조, 전문 용어 쉽게 설명, 감정적 포인트 부각 등",
        key="additional_request_text"
    )

def generate_blog_content():
    """블로그 콘텐츠 생성 (BGN 톤앤매너 적용)"""
    st.subheader("🤖 BGN 스타일 블로그 생성")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📝 BGN 톤앤매너로 블로그 작성", type="primary", use_container_width=True):
            if not st.session_state.get('openai_api_key'):
                st.error("❌ OpenAI API 키를 먼저 입력해주세요")
            else:
                generate_with_ai()
    
    with col2:
        if st.button("🎯 BGN 샘플 블로그로 테스트", use_container_width=True):
            generate_sample_blog()
    
    # 생성된 블로그 내용 표시 및 수정
    if st.session_state.blog_content:
        display_generated_blog()

def generate_with_ai():
    """AI를 사용하여 BGN 톤앤매너 블로그 생성"""
    with st.spinner("🤖 BGN 고유의 자연스러운 톤앤매너로 2,000자 이상 블로그를 작성하고 있습니다..."):
        try:
            analyzer = AIAnalyzer(st.session_state.get('openai_api_key'))
            
            # 진행률 표시
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.text("📝 BGN 톤앤매너 적용 중...")
            progress_bar.progress(20)
            time.sleep(1)
            
            status_text.text("✍️ 자연스러운 말투로 본문 작성 중...")
            progress_bar.progress(60)
            
            # BGN 스타일 매개변수 전달
            bgn_style_params = {
                'staff_role': st.session_state.get('staff_role', '검안사'),
                'staff_name': st.session_state.get('staff_name', '김서연'),
                'use_emotions': st.session_state.get('use_emotions', True),
                'use_casual_talk': st.session_state.get('use_casual_talk', True),
                'use_empathy': st.session_state.get('use_empathy', True)
            }
            
            blog_content = analyzer.generate_blog_content_bgn_style(
                st.session_state.selected_material,
                st.session_state.blog_style,
                st.session_state.content_length,
                st.session_state.additional_request,
                bgn_style_params
            )
            
            progress_bar.progress(90)
            status_text.text("🔍 BGN 톤앤매너 품질 검증 중...")
            time.sleep(0.5)
            
            st.session_state.blog_content = blog_content
            
            progress_bar.progress(100)
            status_text.empty()
            progress_bar.empty()
            
            # 글자수 확인 및 알림
            char_count = len(blog_content)
            if char_count >= 2000:
                st.success(f"✅ BGN 스타일 블로그 완성! (총 {char_count:,}자)")
                st.balloons()
            else:
                st.warning(f"⚠️ 목표 글자수에 미달하지만 생성 완료 ({char_count:,}자)")
            
        except Exception as e:
            st.error(f"❌ 블로그 작성 중 오류: {str(e)}")
            st.warning("💡 BGN 샘플 블로그로 진행합니다.")
            generate_sample_blog()

def generate_sample_blog():
    """BGN 톤앤매너 샘플 블로그 생성"""
    material = st.session_state.selected_material['data']
    material_type = st.session_state.selected_material['type']
    
    # 직무와 이름 설정
    staff_role = st.session_state.get('staff_role', '검안사')
    staff_name = st.session_state.get('staff_name', '김서연')
    
    sample_content = f"""
# {material['title']}

안녕하세요, **BGN밝은눈안과(잠실점)** {staff_role} **{staff_name}**입니다.

## 오늘도 이런 일이 있었어요

아침부터 한 분이 상담실로 들어오시더라고요. 표정이 좀 어두우셨는데, 알고 보니 {material['content']}

그 말씀을 들으면서 저도 마음이 좀 아팠습니다. 왜냐하면 정말 많은 분들이 이런 고민을 안고 계시거든요. 

{material['timestamp']}에 진행된 상담이었는데, 처음에는 조금 긴장하셨던 것 같아요. 그래도 이야기를 나누면서 점점 마음을 여시더라고요.

이런 분들을 만날 때마다 항상 생각하는 게 있어요. 겉으로는 단순해 보이는 문제일 수도 있지만, 그 뒤에는 정말 긴 고민의 시간들이 있었을 거라는 거죠.

사실 저희한테 오시기까지도 많은 용기가 필요하셨을 텐데... 그런 마음을 생각하면 더욱 세심하게 봐드려야겠다는 생각이 들어요.

## 사실 저희도 많이 배워요

이런 분들을 만날 때마다 느끼는 건데요, 환자분들이 저희에게 많은 걸 가르쳐주시는 것 같습니다. 

특히 이 분 같은 경우에는... 정말 솔직하게 말씀해주셨거든요. "선생님, 정말 괜찮아질까요?" 하시면서요.

그 말에 저도 모르게 웃음이 나왔어요. 왜냐하면 그 마음, 정말 잘 알거든요. 처음에는 다들 그런 마음이시니까요.

"괜찮습니다. 저희가 옆에 있잖아요." 이렇게 말씀드렸더니 조금은 안심하시는 것 같더라고요.

사실 이런 순간들이 제가 이 일을 하면서 가장 좋아하는 부분이에요. 기술적인 설명도 중요하지만, 그보다는 마음을 나누는 시간들이요.

환자분들도 처음에는 많이 어색해하시는데, 대화를 나누다 보면 "아, 이런 것도 물어봐도 되나요?" 하시면서 궁금한 걸 하나둘 말씀해주세요.

그럴 때가 정말 좋아요. 뭔가 마음의 벽이 허물어지는 느낌이랄까요? :)

## 그래서 더 세심하게 봐드렸어요

{material['usage_point']}

사실 이런 케이스는 정말 조심스럽거든요. 단순히 기술적인 문제가 아니라, 그분의 일상 전체가 바뀌는 일이니까요.

그래서 평소보다 더 자세히 설명드렸습니다. 과정 하나하나, 예상되는 변화들, 그리고 주의할 점들까지요.

뭔가 이상한 게 있으면 언제든 연락주시라고도 했고요. 작은 거라도 궁금하면 편하게 물어보시라고 했어요.

이 분이 특히 관심 있어 하신 부분이 일상복귀 시기였어요. 언제부터 정상적인 생활이 가능한지, 주의해야 할 점은 뭔지... 그런 실질적인 것들이요.

당연한 질문이죠. 누구나 가장 궁금해하시는 부분이니까요.

혹시나 해서 제가 직접 경험했던 다른 케이스들도 몇 가지 말씀드렸어요. 물론 개인정보는 빼고요. 그냥 "이런 분도 계셨는데, 결과가 정말 좋았어요" 이런 식으로요.

## 며칠 후에 연락이 왔어요

그런데 며칠 후에 전화가 왔더라고요. 처음에는 '혹시 문제가 있나?' 싶어서 조금 걱정했는데요.

알고 보니 너무 좋아서 전화를 주신 거였어요. "선생님, 정말 신세계네요!" 하시면서요 ㅠㅠ

그 말을 듣는 순간... 저도 모르게 울컥했습니다. 이런 일을 하면서 가장 보람을 느끼는 순간이거든요.

특히 이 분은 변화에 대해서 정말 자세히 말씀해주셨어요. 아침에 일어나서부터 밤에 잠들 때까지, 하루 일과가 어떻게 달라졌는지... 듣고 있으면 저도 덩달아 기분이 좋아지더라고요.

"예전에는 이런 게 이렇게 불편했는데, 지금은 너무 편해요!" 하시는 그 목소리에서 정말 기쁨이 느껴졌거든요.

가장 인상깊었던 건... "선생님, 제가 이렇게 연락드리는 게 이상하지 않죠? 너무 좋아서 그냥 말씀드리고 싶었어요" 라고 하시더라고요.

이상할 리가 없죠! 오히려 정말 감사한 일이에요.

## 생각해보니 당연한 일이었어요

사실 저희가 특별한 걸 한 건 아니에요. 그냥 평소에 하던 대로, 세심하게 봐드린 것뿐이거든요.

하지만 그분에게는 그게 정말 큰 변화였나 봅니다. 일상이 완전히 달라졌다고 하시더라고요.

이런 이야기를 들을 때마다 생각하는 건데요, 저희가 하는 일이 단순한 의료 서비스가 아니라는 거예요. 누군가의 삶의 질을 바꾸는 일이죠.

그래서 더 책임감을 느끼게 되는 것 같아요. 기술적인 부분도 물론 중요하지만, 그 이후의 변화까지 생각하게 되니까요.

매일매일 이런 분들을 만나면서 느끼는 건... 정말 소중한 일을 하고 있구나 싶어요. 

물론 힘들 때도 있어요. 모든 케이스가 다 좋은 결과만 있는 건 아니니까요. 하지만 이런 순간들이 있어서 계속 할 수 있는 것 같아요.

## 비슷한 고민을 하고 계신다면

혹시 비슷한 고민을 하고 계신 분이 있다면... 너무 오래 혼자 끙끙 앓지 마세요.

이게 별거 아닌 것 같아도 저는 중요하게 생각해요. 왜냐하면 그 '별거 아닌 것'이 매일매일의 삶에 영향을 주고 있거든요.

저희가 무리하게 권하지는 않을 거예요. 다만, 정확한 정보는 드릴 수 있을 것 같습니다. 그래서 스스로 판단하실 수 있도록요.

상담받으러 오시는 것도 부담스러우시면, 일단 전화로라도 물어보세요. 간단한 궁금증이라도 편하게 연락주시면 됩니다.

요즘은 온라인으로도 간단한 상담이 가능하거든요. 부담 없이 궁금한 점부터 물어보시는 것도 좋을 것 같아요.

정말 작은 것부터 시작하시면 되는 거예요. "이런 증상이 있는데 어떤가요?" 이런 식으로요.

그러면 저희가 최대한 자세히, 그리고 이해하기 쉽게 설명드릴게요. 전문 용어보다는 일상 언어로요.

## 마지막으로 하고 싶은 말

오늘 이 이야기를 나누면서 다시 한 번 느꼈습니다. 저희가 하는 일이 얼마나 소중한 일인지요.

단순히 시력을 좋게 하는 게 아니라, 누군가의 하루하루를 더 밝게 만드는 일이니까요. 그런 마음으로 앞으로도 열심히 할게요.

사실 환자분들이 저희에게 고마워하시는데... 저희가 더 고마운 것 같아요. 이런 보람을 느끼게 해주시니까요.

혹시 궁금한 게 있으시면 언제든 연락주세요. 작은 것도 좋으니까요 :)

정말 편하게 생각하시고 연락주시면 됩니다. 저희는 항상 여기 있으니까요.

이상으로 **BGN밝은눈안과(잠실점)** {staff_role} **{staff_name}**이었습니다. 오늘도 여러분의 소중한 눈을 생각하며... 좋은 하루 보내세요!
"""
    
    st.session_state.blog_content = sample_content.strip()
    char_count = len(st.session_state.blog_content)
    st.success(f"✅ BGN 톤앤매너 샘플 블로그 생성! (총 {char_count:,}자)")

def display_generated_blog():
    """생성된 블로그 내용 표시 및 수정 (BGN 스타일 검증)"""
    st.subheader("📄 생성된 BGN 스타일 블로그")
    
    # 글자수 실시간 표시
    char_count = len(st.session_state.blog_content)
    
    # BGN 톤앤매너 체크
    bgn_score = check_bgn_style_quality(st.session_state.blog_content)
    
    col1, col2 = st.columns(2)
    with col1:
        if char_count >= 2000:
            st.success(f"✅ 목표 달성! 총 {char_count:,}자")
        else:
            st.error(f"❌ 목표 미달: 총 {char_count:,}자")
    
    with col2:
        if bgn_score >= 0.8:
            st.success(f"🎯 BGN 톤앤매너: 우수 ({bgn_score:.1f})")
        elif bgn_score >= 0.6:
            st.info(f"🎯 BGN 톤앤매너: 양호 ({bgn_score:.1f})")
        else:
            st.warning(f"🎯 BGN 톤앤매너: 개선필요 ({bgn_score:.1f})")
    
    # 제목 수정
    if not st.session_state.blog_title:
        st.session_state.blog_title = extract_title_from_content(st.session_state.blog_content)
    
    st.session_state.blog_title = st.text_input(
        "블로그 제목", 
        value=st.session_state.blog_title,
        key="blog_title_input"
    )
    
    # 내용 수정 
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.session_state.blog_content = st.text_area(
            "BGN 톤앤매너를 유지하며 내용을 수정할 수 있습니다:",
            value=st.session_state.blog_content,
            height=400,
            key="blog_content_editor"
        )
    
    with col2:
        # 실시간 통계
        current_chars = len(st.session_state.blog_content)
        words = len(st.session_state.blog_content.split())
        
        st.metric("현재 글자수", f"{current_chars:,}자")
        st.metric("목표까지", f"{max(0, 2000-current_chars):,}자")
        st.metric("단어 수", f"{words:,}개")
        
        # BGN 톤앤매너 실시간 체크
        current_bgn_score = check_bgn_style_quality(st.session_state.blog_content)
        st.metric("BGN 스타일", f"{current_bgn_score:.1f}")
    
    # BGN 톤앤매너 분석 결과
    with st.expander("🎯 BGN 톤앤매너 분석", expanded=False):
        bgn_analysis = analyze_bgn_style(st.session_state.blog_content)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write("**화자 설정**")
            if bgn_analysis['has_proper_intro']:
                st.success("✅ 올바른 시작 멘트")
            else:
                st.warning("⚠️ BGN 시작 멘트 필요")
        
        with col2:
            st.write("**말투 다양성**")
            st.info(f"종결어미 {bgn_analysis['ending_variety']}종류")
            
        with col3:
            st.write("**감정 표현**")
            if bgn_analysis['has_emotions']:
                st.success("✅ 감정 표현 포함")
            else:
                st.warning("⚠️ 감정 표현 부족")
    
    # 미리보기
    with st.expander("👀 블로그 미리보기", expanded=False):
        st.markdown(f"# {st.session_state.blog_title}")
        st.markdown(st.session_state.blog_content)
    
    # 하단 네비게이션
    display_navigation()

def check_bgn_style_quality(content):
    """BGN 톤앤매너 품질 점수"""
    score = 0.5
    
    # BGN 시작/종료 멘트 체크
    if "BGN밝은눈안과(잠실점)" in content:
        score += 0.2
    
    # 다양한 종결어미 체크
    endings = ['해요', '습니다', '죠', '거든요', '더라고요', '라고요', '네요']
    found_endings = sum(1 for ending in endings if ending in content)
    if found_endings >= 4:
        score += 0.2
    elif found_endings >= 2:
        score += 0.1
    
    # 감정 표현 체크
    emotions = [':)', 'ㅠㅠ', '...', '웃음이 나왔', '울컥했']
    if any(emotion in content for emotion in emotions):
        score += 0.1
    
    return min(score, 1.0)

def analyze_bgn_style(content):
    """BGN 스타일 상세 분석"""
    analysis = {
        'has_proper_intro': "BGN밝은눈안과(잠실점)" in content and "입니다." in content[:200],
        'has_proper_outro': "이상으로" in content and "BGN밝은눈안과" in content[-200:],
        'ending_variety': 0,
        'has_emotions': False,
        'has_empathy': False
    }
    
    # 종결어미 다양성
    endings = ['해요', '습니다', '죠', '거든요', '더라고요', '라고요', '네요']
    analysis['ending_variety'] = sum(1 for ending in endings if ending in content)
    
    # 감정 표현
    emotions = [':)', 'ㅠㅠ', '...', '웃음이 나왔', '울컥했']
    analysis['has_emotions'] = any(emotion in content for emotion in emotions)
    
    # 공감 표현
    empathy_words = ['괜찮', '이해', '마음', '공감', '함께']
    analysis['has_empathy'] = any(word in content for word in empathy_words)
    
    return analysis

def extract_title_from_content(content):
    """블로그 내용에서 제목 추출"""
    lines = content.split('\n')
    for line in lines:
        if line.startswith('# '):
            return line[2:].strip()
    
    if st.session_state.selected_material:
        return st.session_state.selected_material['data']['title']
    
    return "BGN 밝은눈안과의 따뜻한 이야기"

def display_navigation():
    """하단 네비게이션"""
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("⬅️ 소재 선택으로", use_container_width=True):
            previous_step()
    
    with col2:
        current_chars = len(st.session_state.blog_content)
        if current_chars >= 1500:
            if st.button("🔄 BGN 스타일로 재생성", use_container_width=True):
                if st.session_state.get('openai_api_key'):
                    generate_with_ai()
                else:
                    generate_sample_blog()
                st.rerun()
        else:
            st.button("🔄 BGN 스타일로 재생성", disabled=True, use_container_width=True, 
                     help=f"최소 1,500자 필요 (현재: {current_chars:,}자)")
    
    with col3:
        # BGN 품질 체크 후 진행
        bgn_score = check_bgn_style_quality(st.session_state.blog_content)
        if current_chars >= 2000 and bgn_score >= 0.6:
            if st.button("🖼️ 이미지 생성하기", type="primary", use_container_width=True):
                next_step()
        else:
            reasons = []
            if current_chars < 2000:
                reasons.append(f"{2000-current_chars:,}자 부족")
            if bgn_score < 0.6:
                reasons.append("BGN 톤앤매너 개선 필요")
            
            st.button("🖼️ 이미지 생성하기", disabled=True, use_container_width=True, 
                     help=f"조건 미충족: {', '.join(reasons)}")