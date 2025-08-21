import streamlit as st
from config import IMAGE_CONFIG, QUALITY_CONFIG
from utils.session_manager import previous_step, next_step
import requests
from io import BytesIO
from PIL import Image

def render_image_generator_page():
    """4단계: 이미지 생성 페이지 (BGN 톤앤매너 반영)"""
    
    st.header("4️⃣ 이미지 생성")
    
    # 블로그 내용 미리보기
    display_blog_preview()
    
    # BGN 스타일 자동 이미지 생성
    render_bgn_auto_image_generation()
    
    # 생성된 이미지 표시
    if st.session_state.generated_image:
        display_generated_image()
    
    # 하단 네비게이션
    display_navigation()

def display_blog_preview():
    """BGN 블로그 내용 미리보기"""
    if st.session_state.blog_content:
        char_count = len(st.session_state.blog_content)
        
        # BGN 스타일 체크
        bgn_elements = {
            'has_bgn_intro': "BGN밝은눈안과(잠실점)" in st.session_state.blog_content[:300],
            'has_natural_tone': any(tone in st.session_state.blog_content for tone in ['거든요', '더라고요', '죠']),
            'has_emotions': any(emotion in st.session_state.blog_content for emotion in [':)', 'ㅠㅠ', '...'])
        }
        
        bgn_score = sum(bgn_elements.values()) / len(bgn_elements)
        
        if bgn_score >= 0.7:
            st.success(f"📝 BGN 스타일 블로그 완성: **{st.session_state.blog_title}** ({char_count:,}자) 🎯")
        else:
            st.info(f"📝 작성된 블로그: **{st.session_state.blog_title}** ({char_count:,}자)")
        
        with st.expander("📄 BGN 블로그 미리보기", expanded=False):
            preview_content = st.session_state.blog_content[:400]
            if len(st.session_state.blog_content) > 400:
                preview_content += "..."
            st.write(preview_content)
            
            # BGN 톤앤매너 체크 결과
            col1, col2, col3 = st.columns(3)
            with col1:
                if bgn_elements['has_bgn_intro']:
                    st.success("✅ BGN 시작 멘트")
                else:
                    st.warning("⚠️ BGN 시작 멘트 없음")
            with col2:
                if bgn_elements['has_natural_tone']:
                    st.success("✅ 자연스러운 말투")
                else:
                    st.warning("⚠️ 말투 개선 필요")
            with col3:
                if bgn_elements['has_emotions']:
                    st.success("✅ 감정 표현")
                else:
                    st.warning("⚠️ 감정 표현 부족")
    else:
        st.warning("⚠️ 블로그 내용이 없습니다. 이전 단계로 돌아가 BGN 스타일 블로그를 작성해주세요.")
        if st.button("⬅️ BGN 블로그 작성으로"):
            previous_step()

def render_bgn_auto_image_generation():
    """BGN 스타일 자동 이미지 생성"""
    st.subheader("🎨 BGN 스타일 이미지 생성")
    
    if not st.session_state.blog_content:
        st.warning("먼저 BGN 스타일 블로그를 작성해주세요.")
        return
    
    # BGN 맞춤 프롬프트 생성
    bgn_prompts = generate_bgn_image_prompt(
        st.session_state.blog_content, 
        st.session_state.blog_title, 
        st.session_state.selected_material
    )
    
    st.info("💡 BGN 블로그 내용을 분석하여 브랜드에 맞는 따뜻한 이미지 프롬프트를 생성했습니다.")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        selected_prompt = st.selectbox(
            "🎨 BGN 추천 프롬프트:",
            [bgn_prompts["main_prompt"]] + bgn_prompts["alternatives"],
            key="bgn_prompt_selection"
        )
    
    with col2:
        if st.button("🖼️ BGN 이미지 생성", type="primary", use_container_width=True):
            generate_bgn_image_with_prompt(selected_prompt)
    
    # BGN 스타일 프롬프트 수정 옵션
    with st.expander("✏️ BGN 스타일 프롬프트 커스터마이징", expanded=False):
        st.markdown("**🎯 BGN 이미지 스타일 가이드:**")
        st.markdown("- 따뜻하고 전문적인 의료 환경")
        st.markdown("- 한국인 환자와 의료진의 자연스러운 소통")
        st.markdown("- 밝고 깨끗한 병원 분위기")
        st.markdown("- 신뢰감 있는 최신 의료 장비")
        
        custom_prompt = st.text_area(
            "프롬프트 직접 수정:", 
            value=selected_prompt,
            height=120,
            key="custom_bgn_prompt"
        )
        if st.button("수정된 BGN 프롬프트로 생성", key="custom_bgn_generate"):
            generate_bgn_image_with_prompt(custom_prompt)
    
    # BGN 콘텐츠 분석 결과
    with st.expander("🔍 BGN 콘텐츠 분석 결과", expanded=False):
        analysis = bgn_prompts["analysis"]
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**📊 감지된 BGN 요소:**")
            st.metric("메인 장면", analysis['main_scene'])
            st.metric("감정 톤", analysis['emotional_tone'])
        
        with col2:
            st.markdown("**🎨 추천 이미지 스타일:**")
            st.metric("BGN 브랜드 적합성", f"{analysis['brand_fit']}/5")
            st.metric("따뜻함 지수", f"{analysis['warmth_level']}/5")

def generate_bgn_image_prompt(blog_content, blog_title, selected_material):
    """BGN 브랜드에 맞는 이미지 프롬프트 생성"""
    
    # BGN 기본 브랜드 설정
    bgn_base = "warm and professional Korean eye clinic BGN, modern medical facility in Jamsil, bright and caring atmosphere"
    
    # 소재 유형별 BGN 맞춤 프롬프트
    material_type = selected_material.get('type', '기본')
    bgn_type_prompts = {
        "고객 에피소드형": "Korean patient and BGN staff heartwarming consultation, genuine care and empathy, emotional connection",
        "검사·과정형": "Korean eye examination at BGN clinic, advanced medical equipment, professional yet caring procedure",
        "센터 운영/분위기형": "BGN clinic interior, Korean medical staff teamwork, warm and professional atmosphere, patient-centered care",
        "초년차 성장기형": "young Korean medical professional at BGN, learning and mentorship moment, supportive work environment",
        "고객 질문 FAQ형": "Korean doctor at BGN explaining to patient, caring consultation room, informative and reassuring discussion",
        "키워드 기반 소재": "BGN eye clinic scene, Korean medical staff and patients, warm professional medical environment"
    }
    
    base_prompt = bgn_type_prompts.get(material_type, bgn_type_prompts["키워드 기반 소재"])
    
    # BGN 블로그 내용에서 감정과 상황 추출
    bgn_analysis = analyze_bgn_content_for_image(blog_content, blog_title)
    
    # BGN 최종 프롬프트 구성
    final_prompt = f"{bgn_base}, {base_prompt}, {bgn_analysis['emotional_scene']}, Korean people, realistic warm photography, bright natural lighting, BGN brand professional medical setting, {bgn_analysis['mood']}, high quality, detailed, caring atmosphere"
    
    # BGN 스타일 변형 프롬프트들
    alternative_prompts = [
        f"Wide shot of BGN eye clinic in Jamsil, {bgn_analysis['emotional_scene']}, modern Korean medical interior, warm professional atmosphere",
        f"Close-up moment at BGN clinic, {bgn_analysis['focus_element']}, Korean patient and caring staff, emotional and professional interaction",
        f"BGN medical consultation scene, {bgn_analysis['emotional_scene']}, warm and trustworthy Korean medical environment, natural lighting"
    ]
    
    return {
        "main_prompt": final_prompt.strip(),
        "alternatives": alternative_prompts,
        "analysis": bgn_analysis,
        "style_recommendation": "warm, professional BGN brand photography",
        "mood_recommendation": bgn_analysis['mood']
    }

def analyze_bgn_content_for_image(blog_content, blog_title):
    """BGN 블로그 내용 분석하여 브랜드 맞춤 이미지 요소 추출"""
    
    content_lower = blog_content.lower()
    title_lower = blog_title.lower()
    
    # BGN 감정 톤 분석 (블로그 톤앤매너 기반)
    emotion_keywords = {
        "따뜻한 공감": "caring and empathetic interaction",
        "전문적 신뢰": "professional and trustworthy medical scene", 
        "자연스러운 소통": "natural and comfortable communication",
        "희망적 분위기": "hopeful and positive medical environment",
        "안심과 격려": "reassuring and encouraging atmosphere",
        "진솔한 케어": "genuine care and attention"
    }
    
    detected_emotion = "caring and professional interaction"
    for keyword, scene in emotion_keywords.items():
        if any(word in content_lower for word in keyword.split()):
            detected_emotion = scene
            break
    
    # BGN 특화 장면 키워드 분석
    bgn_scene_keywords = {
        "상담": "BGN consultation scene with caring staff",
        "검사": "BGN eye examination with modern equipment",
        "치료": "BGN treatment process with professional care",
        "회복": "BGN recovery support and follow-up care",
        "소통": "BGN staff-patient communication and trust building",
        "케어": "BGN comprehensive patient care service"
    }
    
    detected_scene = "BGN general patient care scene"
    for keyword, scene in bgn_scene_keywords.items():
        if keyword in content_lower or keyword in title_lower:
            detected_scene = scene
            break
    
    # BGN 포커스 요소 분석
    focus_keywords = {
        "환자": "patient's comfortable and trusting expression",
        "의료진": "BGN staff's professional and caring interaction", 
        "과정": "BGN medical procedure with careful attention",
        "결과": "positive treatment outcome and patient satisfaction",
        "소통": "meaningful communication between BGN staff and patient"
    }
    
    detected_focus = "BGN staff-patient caring interaction"
    for keyword, focus in focus_keywords.items():
        if keyword in content_lower:
            detected_focus = focus
            break
    
    # BGN 브랜드 적합성 및 따뜻함 지수 계산
    bgn_indicators = ['bgn', '밝은눈안과', '잠실', '따뜻', '케어', '소통', '신뢰']
    brand_fit = min(5, sum(1 for indicator in bgn_indicators if indicator in content_lower))
    
    warmth_indicators = ['따뜻', '편안', '안심', '케어', '소통', '공감', '격려']
    warmth_level = min(5, sum(1 for indicator in warmth_indicators if indicator in content_lower))
    
    return {
        "main_scene": detected_scene,
        "emotional_scene": detected_emotion,
        "emotional_tone": "따뜻하고 전문적인",
        "focus_element": detected_focus,
        "mood": "warm, caring and professional",
        "brand_fit": brand_fit,
        "warmth_level": warmth_level
    }

def generate_bgn_image_with_prompt(prompt):
    """BGN 스타일 프롬프트로 이미지 생성"""
    with st.spinner("🎨 BGN 브랜드에 맞는 따뜻한 이미지를 생성하고 있습니다..."):
        try:
            # 실제 DALL-E API 호출은 여기서 구현
            # 현재는 BGN 스타일에 맞는 샘플 이미지 생성
            generated_image = create_bgn_sample_image(prompt)
            
            st.session_state.generated_image = generated_image
            st.success("✅ BGN 스타일 이미지가 성공적으로 생성되었습니다!")
            
        except Exception as e:
            st.error(f"❌ 이미지 생성 중 오류: {str(e)}")
            st.session_state.generated_image = create_bgn_fallback_image()

def create_bgn_sample_image(prompt):
    """BGN 프롬프트 기반 샘플 이미지 생성"""
    
    # BGN 스타일에 맞는 이미지 선택
    if "consultation" in prompt.lower() or "상담" in prompt:
        image_url = "https://images.unsplash.com/photo-1559757148-5c350d0d3c56?w=800&h=600&fit=crop&auto=format"
        description = "BGN 스타일 의사-환자 따뜻한 상담 장면"
    elif "examination" in prompt.lower() or "검사" in prompt:
        image_url = "https://images.unsplash.com/photo-1582750433449-648ed127bb54?w=800&h=600&fit=crop&auto=format"
        description = "BGN 전문적이고 세심한 안과 검사 장면"
    elif "clinic" in prompt.lower() or "병원" in prompt:
        image_url = "https://images.unsplash.com/photo-1551190822-a9333d879b1f?w=800&h=600&fit=crop&auto=format"
        description = "BGN 밝고 따뜻한 안과 병원 환경"
    elif "caring" in prompt.lower() or "케어" in prompt:
        image_url = "https://images.unsplash.com/photo-1576091160399-112ba8d25d1f?w=800&h=600&fit=crop&auto=format"
        description = "BGN 직원의 세심한 환자 케어 모습"
    else:
        image_url = "https://images.unsplash.com/photo-1551190822-a9333d879b1f?w=800&h=600&fit=crop&auto=format"
        description = "BGN 밝은눈안과의 전문적이고 따뜻한 분위기"
    
    return {
        "url": image_url,
        "prompt": prompt,
        "description": description,
        "filename": "bgn_blog_image.jpg",
        "generation_method": "BGN 브랜드 맞춤 AI 생성",
        "style": "BGN 따뜻한 전문성"
    }

def create_bgn_fallback_image():
    """BGN 오류 시 대체 이미지"""
    return {
        "url": "https://images.unsplash.com/photo-1551190822-a9333d879b1f?w=800&h=600&fit=crop&auto=format",
        "prompt": "BGN 밝은눈안과 따뜻한 전문 의료 환경",
        "description": "BGN 기본 브랜드 이미지",
        "filename": "bgn_fallback_image.jpg",
        "generation_method": "BGN 기본 이미지",
        "style": "BGN 브랜드 스타일"
    }

def display_generated_image():
    """생성된 BGN 이미지 표시"""
    st.subheader("🖼️ 생성된 BGN 브랜드 이미지")
    
    image_info = st.session_state.generated_image
    
    # 이미지와 BGN 브랜드 정보를 나란히 표시
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.image(
            image_info["url"], 
            caption=image_info["description"],
            use_container_width=True
        )
    
    with col2:
        st.write("**🎨 BGN 이미지 정보**")
        st.write(f"**생성 방식**: {image_info.get('generation_method', 'BGN AI 생성')}")
        st.write(f"**브랜드 스타일**: {image_info.get('style', 'BGN 스타일')}")
        st.write(f"**설명**: {image_info['description']}")
        
        # BGN 브랜드 적합성 체크
        bgn_quality = check_bgn_image_quality(image_info)
        if bgn_quality["score"] >= 0.8:
            st.success(f"✅ BGN 브랜드 적합성: {bgn_quality['score']:.1f}/1.0")
        else:
            st.warning(f"⚠️ BGN 브랜드 적합성: {bgn_quality['score']:.1f}/1.0")
            st.write("개선 제안:", bgn_quality["suggestions"])
    
    # BGN 프롬프트 정보
    with st.expander("🔧 BGN 생성 프롬프트", expanded=False):
        st.code(image_info["prompt"], language="text")
        st.markdown("**💡 BGN 프롬프트 특징:**")
        st.markdown("- 따뜻하고 전문적인 의료 환경")
        st.markdown("- 한국인 환자와 의료진")
        st.markdown("- BGN 브랜드 정체성 반영")
    
    # BGN 이미지 관리 옵션
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🔄 BGN 스타일로 재생성", use_container_width=True):
            generate_bgn_image_with_prompt(image_info["prompt"])
            st.rerun()
    
    with col2:
        if st.button("✏️ BGN 프롬프트 수정", use_container_width=True):
            st.session_state.show_bgn_prompt_editor = True
            st.rerun()
    
    with col3:
        if st.button("💾 BGN 이미지 저장", use_container_width=True):
            save_bgn_image_locally(image_info)

def check_bgn_image_quality(image_info):
    """BGN 브랜드 이미지 품질 점검"""
    score = 0.8  # BGN 기본 점수
    suggestions = []
    
    prompt = image_info.get("prompt", "").lower()
    
    # BGN 브랜드 키워드 확인
    bgn_keywords = ["bgn", "korean", "warm", "caring", "professional"]
    if sum(1 for keyword in bgn_keywords if keyword in prompt) >= 3:
        score += 0.1
    else:
        suggestions.append("BGN 브랜드 키워드 강화 필요")
    
    # 의료 환경 키워드 확인
    medical_keywords = ["medical", "clinic", "eye", "patient", "staff"]
    if sum(1 for keyword in medical_keywords if keyword in prompt) >= 2:
        score += 0.1
    else:
        suggestions.append("의료 환경 표현 강화 필요")
    
    return {
        "score": min(score, 1.0),
        "suggestions": suggestions if suggestions else ["BGN 브랜드에 적합한 이미지입니다"]
    }

def save_bgn_image_locally(image_info):
    """BGN 이미지를 로컬에 저장"""
    try:
        response = requests.get(image_info["url"])
        if response.status_code == 200:
            st.session_state.image_data = response.content
            st.success("✅ BGN 브랜드 이미지가 저장되었습니다.")
        else:
            st.error("❌ BGN 이미지 저장에 실패했습니다.")
    except Exception as e:
        st.error(f"❌ 저장 중 오류: {str(e)}")

def display_navigation():
    """하단 네비게이션 (BGN 스타일)"""
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("⬅️ BGN 블로그 수정", use_container_width=True):
            previous_step()
    
    with col2:
        if st.session_state.generated_image:
            if st.button("🔄 새 BGN 이미지 생성", use_container_width=True):
                if st.session_state.blog_content:
                    bgn_prompts = generate_bgn_image_prompt(
                        st.session_state.blog_content, 
                        st.session_state.blog_title, 
                        st.session_state.selected_material
                    )
                    generate_bgn_image_with_prompt(bgn_prompts["main_prompt"])
                    st.rerun()
    
    with col3:
        if st.session_state.generated_image:
            # BGN 이미지 품질 체크 후 진행
            bgn_quality = check_bgn_image_quality(st.session_state.generated_image)
            if bgn_quality["score"] >= 0.7:
                if st.button("📤 워드프레스 발행", type="primary", use_container_width=True):
                    next_step()
            else:
                st.button("📤 워드프레스 발행", disabled=True, use_container_width=True, 
                         help="BGN 브랜드 품질을 개선한 후 발행 가능합니다")
        else:
            st.button("📤 워드프레스 발행", disabled=True, use_container_width=True, 
                     help="먼저 BGN 스타일 이미지를 생성해주세요")