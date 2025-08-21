import json
import streamlit as st
from openai import OpenAI
from config import OPENAI_CONFIG, CONTENT_TYPES, QUALITY_CONFIG
import time

class AIAnalyzer:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)
        self.config = OPENAI_CONFIG
    
    def generate_blog_content_bgn_style(self, selected_material, style, length, additional_request, bgn_style_params):
        """BGN 톤앤매너로 블로그 콘텐츠 생성"""
        
        material = selected_material['data']
        material_type = selected_material['type']
        
        # BGN 스타일 매개변수 추출
        staff_role = bgn_style_params.get('staff_role', '검안사')
        staff_name = bgn_style_params.get('staff_name', '김서연')
        use_emotions = bgn_style_params.get('use_emotions', True)
        use_casual_talk = bgn_style_params.get('use_casual_talk', True)
        use_empathy = bgn_style_params.get('use_empathy', True)
        
        # 목표 글자수 설정
        length_config = {
            "표준 품질 (2,000자 이상)": {"min_chars": 2000, "target_chars": 2200, "max_tokens": 3500},
            "고품질 (2,500자 이상)": {"min_chars": 2500, "target_chars": 2700, "max_tokens": 4000},
            "프리미엄 (3,000자 이상)": {"min_chars": 3000, "target_chars": 3200, "max_tokens": 4500}
        }
        
        config = length_config.get(length, length_config["표준 품질 (2,000자 이상)"])
        
        # 직접 인용구 및 키워드 추출
        direct_quote = material.get('direct_quote', '')
        keywords = material.get('keywords', [])
        
        prompt = f"""
BGN밝은눈안과(잠실점) 블로그 포스트를 BGN 고유의 톤앤매너로 작성해주세요. **반드시 {config['min_chars']}자 이상**으로 작성해야 합니다.

📋 소재 정보:
- 유형: {material_type}
- 제목: {material['title']}
- 내용: {material['content']}
- 키워드: {', '.join(keywords[:8]) if keywords else '없음'}
- 시간대: {material['timestamp']}
- 활용 포인트: {material['usage_point']}
{f"- 직접 인용: {direct_quote}" if direct_quote else ""}

👤 BGN 화자 설정:
- 직무: {staff_role}
- 이름: {staff_name}
- 스타일: {style}

🎯 BGN 고유 톤앤매너 (절대 준수):
- **시작**: "안녕하세요, **BGN밝은눈안과(잠실점)** {staff_role} **{staff_name}**입니다."
- **종료**: "이상으로 **BGN밝은눈안과(잠실점)** {staff_role} **{staff_name}**이었습니다. 오늘도 여러분의 소중한 눈을 생각하며..."

🗣️ BGN 말투 특징 (자연스럽게 혼용):
- **다양한 종결어미**: 해요/습니다/죠/거든요/네요/더라고요/라고요/이에요 등 자연스럽게 섞어서 사용
- **감정 표현**: {':), ㅠㅠ, ..., 웃음이 나왔어요, 울컥했습니다' if use_emotions else '절제된 감정 표현'}
- **구어체 표현**: {'자연스러운 말줄임표, 감탄사, 웃음 표현 사용' if use_casual_talk else '정중한 구어체'}
- **공감 표현**: {'괜찮으세요, 저희가 옆에 있잖아요, 이해해요' if use_empathy else '전문적 조언'}

💡 BGN 특화 표현법:
- "오늘도 이런 일이 있었어요" (일상 에피소드 시작)
- "그 말에 저도 모르게..." (자연스러운 감정 반응)
- "사실 저희도 많이 배워요" (겸손한 자세)
- "이게 별거 아닌 것 같아도 저는 중요하게 생각해요" (세심한 관심)
- "무리하게 권하지는 않을 거예요" (강요 없는 조언)
- "편하게 물어보세요" (친근한 접근)

{f"🔧 추가 요청사항: {additional_request}" if additional_request else ""}

📝 BGN 블로그 구조 (각 섹션 충분히 길게, 최소 글자수 보장):

# [환자 경험 중심의 따뜻한 제목]

안녕하세요, **BGN밝은눈안과(잠실점)** {staff_role} **{staff_name}**입니다.

## 오늘도 이런 일이 있었어요
(**최소 5-6문단**, 일상 에피소드로 자연스럽게 시작)
- "아침부터 한 분이 들어오시더라고요..."
- 환자의 첫인상과 상황 묘사
- 상담 초기의 분위기와 대화
- {staff_role}로서의 첫 느낌과 생각
- 환자의 구체적 고민과 걱정
- 소재 내용을 자연스럽게 녹여내기

## 사실 저희도 많이 배워요
(**최소 5-6문단**, 겸손하면서도 전문적으로)
- 환자에게서 배우는 점들
- 의료진의 솔직한 소감과 성찰
- 구체적인 상담/치료 과정 설명
- "이런 케이스는 정말 조심스럽거든요"
- 환자와의 소통에서 느끼는 점
- BGN만의 접근 방식 소개

## 그래서 더 세심하게 봐드렸어요
(**최소 5-6문단**, 개별 맞춤 케어 강조)
- {material['usage_point']}를 중심으로 한 구체적 접근
- 환자별 맞춤 상담 과정
- "뭔가 이상한 게 있으면 언제든 연락주시라고..."
- 세부적인 설명과 안내 과정
- 환자의 질문과 의료진의 답변
- 실제 치료/검사 경험담

## 며칠 후에 연락이 왔어요
(**최소 4-5문단**, 감동적인 후기)
- 환자의 피드백과 변화된 모습
- 구체적인 개선 사례와 만족도
- "그 말을 듣는 순간 저도 모르게 울컥했습니다"
- 일상생활의 구체적 변화
- 주변 사람들의 반응
- 의료진으로서의 보람

## 생각해보니 당연한 일이었어요
(**최소 4-5문단**, 겸손하고 따뜻하게)
- "저희가 특별한 걸 한 건 아니에요"
- 환자 중심 서비스의 당연함
- BGN의 일상적인 케어 문화
- 작은 배려의 큰 의미
- 환자와 의료진의 상호 성장
- 의료진의 사명감과 보람

## 비슷한 고민을 하고 계신다면
(**최소 4-5문단**, 강요 없는 따뜻한 조언)
- "이게 별거 아닌 것 같아도 저는 중요하게 생각해요"
- "무리하게 권하지는 않을 거예요"
- "편하게 물어보세요" 분위기 조성
- 작은 궁금증부터 시작하는 것의 중요성
- BGN의 열린 상담 문화
- 환자 스스로의 선택을 존중하는 자세

## 마지막으로 하고 싶은 말
(**최소 3-4문단**, 진심 어린 마무리)
- 핵심 메시지 요약
- 환자에 대한 진솔한 마음
- "혹시 궁금한 게 있으시면 언제든 연락주세요"
- BGN 의료진의 다짐과 약속
- 독자에게 전하는 따뜻한 메시지

이상으로 **BGN밝은눈안과(잠실점)** {staff_role} **{staff_name}**이었습니다. 오늘도 여러분의 소중한 눈을 생각하며... [자연스러운 마무리 인사]

⚠️ BGN 절대 준수사항:
- **반드시 {config['min_chars']}자 이상 작성** (미달 절대 금지)
- **다양한 종결어미 자연스럽게 혼용** (해요/습니다/죠/거든요/더라고요 등)
- **BGN 고유 화자 설정 유지** ({staff_role} {staff_name}의 1인칭 시점)
- **병원 홍보나 영업성 멘트 절대 금지** (자연스러운 경험담 중심)
- **감정 표현과 구어체** 적절히 사용 ({':), ㅠㅠ, ...' if use_emotions else '절제된 표현'})
- **강요 없는 따뜻한 조언** 톤 유지
- **구체적 사례와 개인 경험** 풍부하게 포함
- **BGN 브랜드 정체성** (따뜻함, 전문성, 신뢰) 자연스럽게 표현
- 각 섹션별로 **충분한 분량 확보** (4-6문단씩)
- **즉시 발행 가능한 완성형** 구조
"""

        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                response = self.client.chat.completions.create(
                    model=self.config["model"],
                    messages=[
                        {
                            "role": "system", 
                            "content": f"""당신은 BGN밝은눈안과 전속 블로그 작가입니다. 

🎯 핵심 미션: 
- **절대적으로 {config['min_chars']}자 이상의 BGN 브랜드 톤앤매너 블로그 작성**
- BGN 고유의 따뜻하고 자연스러운 1인칭 실무자 시점 구현
- 실제 인터뷰 내용을 BGN 스타일로 생생하게 재구성
- 즉시 발행 가능한 완성도 높은 콘텐츠

🏥 BGN 브랜드 정체성:
- **따뜻함**: 기계적이지 않은 인간적 케어
- **전문성**: 의학적 정확성과 신뢰성
- **진솔함**: 과장 없는 솔직하고 담담한 소통
- **접근성**: 부담 없이 편하게 다가갈 수 있는 분위기

💬 BGN 톤앤매너 DNA:
1. **자연스러운 말투**: 다양한 종결어미 혼용으로 기계적 반복 방지
2. **경험 기반 서사**: "오늘 이런 일이 있었어요" 스타일의 일상 에피소드
3. **겸손한 전문성**: "저희도 많이 배워요", "특별한 건 아니에요"
4. **담담한 공감**: 과장 없는 진솔한 감정 표현
5. **강요 없는 조언**: "무리하게 권하지 않을 거예요"
6. **열린 소통**: "편하게 물어보세요", "작은 것도 좋으니까요"

✍️ BGN 글쓰기 철학:
1. **분량 절대 보장**: 각 문단 5-8문장으로 풍부하게
2. **구체성 극대화**: 일반론 대신 개인 경험과 구체적 사례
3. **자연스러운 완성도**: 수정 없이 바로 발행 가능한 수준
4. **브랜드 일관성**: BGN의 따뜻하고 전문적인 이미지 유지
5. **독자 중심**: 환자의 시선에서 불안 해소와 자연스러운 선택 유도

🚫 BGN 절대 금지사항:
- {config['min_chars']}자 미만 작성
- 단조로운 종결어미 반복 (해요만 계속 사용 등)
- 형식적이거나 구조적인 제목
- 과도한 영업성 멘트나 병원 방문 유도
- "보통", "대부분" 같은 모호한 표현
- BGN 브랜드 정체성에 맞지 않는 톤"""
                        },
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=config['max_tokens']
                )
                
                blog_content = response.choices[0].message.content
                char_count = len(blog_content)
                
                # BGN 스타일 검증
                bgn_validation = self._validate_bgn_style(blog_content, config['min_chars'])
                
                if char_count >= config['min_chars']:
                    st.success(f"✅ BGN 스타일 블로그 완성! (총 {char_count:,}자)")
                    
                    if bgn_validation["bgn_score"] >= 0.7:
                        st.info(f"🎯 BGN 톤앤매너: 우수 ({bgn_validation['bgn_score']:.1f}/1.0)")
                    else:
                        st.warning(f"🎯 BGN 톤앤매너: 개선필요 ({bgn_validation['bgn_score']:.1f}/1.0)")
                        st.write("개선사항:", bgn_validation['improvement_suggestions'])
                    
                    return blog_content
                else:
                    if attempt < max_attempts - 1:
                        shortage = config['min_chars'] - char_count
                        st.warning(f"⚠️ 글자수 부족 ({char_count:,}자/{config['min_chars']:,}자) - BGN 스타일로 재생성 중... ({attempt+2}/{max_attempts})")
                        
                        # BGN 스타일 강화 요청
                        prompt += f"\n\n**긴급 BGN 요청**: 현재 {char_count}자로 {shortage}자가 부족합니다. BGN 톤앤매너를 유지하면서 각 섹션을 더욱 상세하고 풍부하게 작성하여 반드시 {config['min_chars']}자를 넘겨주세요. 특히 BGN만의 따뜻한 에피소드와 구체적인 경험담을 더 많이 포함해주세요."
                    else:
                        st.error(f"❌ {max_attempts}번 시도했지만 BGN 목표 글자수 달성 실패 (현재 {char_count}자)")
                        st.warning("💡 생성된 내용을 제공하니 BGN 스타일로 추가 편집해주세요.")
                        return blog_content
                        
            except Exception as e:
                if attempt < max_attempts - 1:
                    st.warning(f"BGN 블로그 생성 중 오류 - 재시도 중... ({attempt+2}/{max_attempts}): {str(e)}")
                else:
                    st.error(f"BGN 블로그 생성 실패: {str(e)}")
                    raise e
        
        return blog_content
    
    def _validate_bgn_style(self, blog_content, min_chars):
        """BGN 톤앤매너 스타일 검증"""
        bgn_score = 0.5
        improvement_suggestions = []
        
        # BGN 브랜드 요소 체크
        bgn_elements = {
            'has_bgn_intro': "BGN밝은눈안과(잠실점)" in blog_content[:300],
            'has_bgn_outro': "BGN밝은눈안과(잠실점)" in blog_content[-300:],
            'has_staff_intro': any(role in blog_content[:200] for role in ['검안사', '간호사', '원무팀', '의료진']),
            'has_daily_episode': "오늘도 이런 일이" in blog_content or "오늘" in blog_content[:500]
        }
        
        if sum(bgn_elements.values()) >= 3:
            bgn_score += 0.2
        else:
            improvement_suggestions.append("BGN 브랜드 요소 강화 필요")
        
        # 톤앤매너 다양성 체크
        tone_variety = {
            'ending_variety': len([end for end in ['해요', '습니다', '죠', '거든요', '더라고요', '라고요'] if end in blog_content]),
            'emotion_expressions': any(expr in blog_content for expr in [':)', 'ㅠㅠ', '...', '웃음이', '울컥']),
            'empathy_words': any(word in blog_content for word in ['괜찮', '함께', '옆에 있', '이해'])
        }
        
        if tone_variety['ending_variety'] >= 4:
            bgn_score += 0.15
        elif tone_variety['ending_variety'] >= 2:
            bgn_score += 0.1
        else:
            improvement_suggestions.append("종결어미 다양성 부족")
        
        if tone_variety['emotion_expressions']:
            bgn_score += 0.1
        else:
            improvement_suggestions.append("감정 표현 부족")
        
        if tone_variety['empathy_words']:
            bgn_score += 0.05
        else:
            improvement_suggestions.append("공감 표현 부족")
        
        # BGN 특화 표현 체크
        bgn_phrases = [
            "저희도 많이 배워요", "별거 아닌 것 같아도", "무리하게 권하지", 
            "편하게 물어보세요", "특별한 걸 한 건 아니에요"
        ]
        
        found_phrases = sum(1 for phrase in bgn_phrases if phrase in blog_content)
        if found_phrases >= 2:
            bgn_score += 0.1
        else:
            improvement_suggestions.append("BGN 특화 표현 부족")
        
        return {
            "bgn_score": min(bgn_score, 1.0),
            "improvement_suggestions": improvement_suggestions if improvement_suggestions else ["BGN 톤앤매너가 잘 적용되었습니다"],
            "bgn_elements": bgn_elements,
            "tone_variety": tone_variety
        }

    def analyze_interview_content_keyword_based(self, content):
        """키워드 기반 인터뷰 분석 (BGN 브랜드 관점)"""
        content_length = len(content)
        
        if content_length <= 15000:
            st.info(f"📄 텍스트 길이: {content_length:,}자 - BGN 맞춤 키워드 분석")
            return self._analyze_keywords_for_bgn(content)
        else:
            st.warning(f"📄 텍스트 길이: {content_length:,}자 - BGN 앞부분 분석으로 진행")
            # 앞부분만 분석
            truncated_content = content[:15000]
            return self._analyze_keywords_for_bgn(truncated_content)
    
    def _analyze_keywords_for_bgn(self, content):
        """BGN 브랜드 관점에서 키워드 분석"""
        
        prompt = f"""
BGN밝은눈안과(잠실점) 직원 인터뷰에서 BGN 브랜드에 맞는 블로그 소재를 추출해주세요.

📋 인터뷰 내용:
{content}

🏥 BGN 브랜드 관점에서 추출:
1. **BGN 특화 키워드** - BGN의 따뜻하고 전문적인 브랜드와 연결되는 키워드
2. **다양한 톤앤매너 소재** - 검안사, 간호사, 원무팀 등 다양한 직무 관점의 소재
3. **환자 중심 에피소드** - BGN의 환자 케어 철학이 드러나는 실제 사례

📝 결과 형식:
{{
  "키워드 기반 소재": [
    {{
      "title": "BGN 직원 시점의 구체적이고 따뜻한 블로그 제목",
      "content": "인터뷰에서 실제 언급된 BGN 관련 구체적 내용과 사례 (최소 120자 이상)",
      "keywords": ["BGN", "특화", "키워드", "6-8개"],
      "timestamp": "인터뷰에서 언급된 정확한 구간",
      "usage_point": "BGN 톤앤매너로 2000자 이상 블로그 구성 방안",
      "staff_perspective": "검안사/간호사/원무팀 중 적합한 화자 설정",
      "target_audience": "예비 환자/기존 환자/일반인 중 선택",
      "direct_quote": "BGN 직원의 인상적인 직접 인용구 (있다면)",
      "bgn_brand_fit": "BGN 브랜드 정체성(따뜻함/전문성/신뢰)과의 연결점",
      "emotion_tone": "해당 소재의 감정적 톤 (따뜻한 공감/전문적 신뢰/자연스러운 소통 등)"
    }}
  ]
}}

⚠️ BGN 중요 지침:
- 반드시 **6개 이상의 서로 다른 소재** 제공
- 각 소재는 **BGN 브랜드 정체성** (따뜻함, 전문성, 신뢰)과 연결
- **다양한 직무 관점** (검안사, 간호사, 원무팀 등) 포함
- 인터뷰에서 **실제 언급된 내용**만 사용
- **구체적 개인 특성**과 감정 포함 (나이, 직업, 증상 등)
- BGN의 **자연스러운 톤앤매너**로 확장 가능한 소재
- **2000자 이상 블로그로 확장 가능**한 구체성 보장
- 각 소재마다 **서로 다른 관점과 주제** 커버
- BGN **브랜드 차별화** 요소 포함

절대 금지:
- 일반적이거나 추상적인 내용
- "보통", "대부분", "흔히" 같은 모호한 표현
- 인터뷰에 없는 내용 추가
- BGN 브랜드와 맞지 않는 톤
"""

        try:
            response = self.client.chat.completions.create(
                model=self.config["model"],
                messages=[
                    {
                        "role": "system", 
                        "content": """당신은 BGN밝은눈안과 전문 콘텐츠 기획자입니다.

핵심 미션: 
- 인터뷰에서 BGN 브랜드에 맞는 2000자 이상 완성도 높은 블로그로 확장 가능한 소재 발굴
- BGN의 따뜻하고 전문적인 브랜드 정체성에 맞는 구체적이고 생생한 개인 경험담 중심
- 다양한 BGN 직무 관점(검안사, 간호사, 원무팀 등)에서 접근 가능한 소재

BGN 브랜드 추출 원칙:
1. 실제 언급된 구체적 사례만 사용
2. BGN의 따뜻함, 전문성, 신뢰성이 드러나는 내용
3. 개인적 특성과 감정 포함
4. 다양한 연령대와 상황 커버
5. 각 소재는 서로 다른 관점과 주제
6. BGN 톤앤매너로 2000자 확장 가능성 보장

절대 금지:
- 일반적이거나 추상적인 내용
- "일반적으로", "보통", "대부분" 같은 모호한 표현
- 인터뷰에 없는 내용 추가
- BGN 브랜드 정체성에 맞지 않는 소재"""
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=4000
            )
            
            result = response.choices[0].message.content
            
            try:
                start = result.find('{')
                end = result.rfind('}') + 1
                if start != -1 and end > start:
                    json_str = result[start:end]
                    materials = json.loads(json_str)
                    
                    # BGN 품질 검증
                    validated_materials = self._validate_bgn_keyword_materials(materials)
                    
                    st.success("✅ BGN 브랜드 맞춤 키워드 분석 완료!")
                    return validated_materials
                else:
                    raise json.JSONDecodeError("JSON 형식 찾기 실패", result, 0)
                    
            except json.JSONDecodeError:
                st.warning("BGN 분석 결과 파싱 실패 - BGN 샘플 데이터로 대체")
                return self._get_bgn_keyword_fallback_materials()
                
        except Exception as e:
            st.error(f"BGN 키워드 분석 실패: {str(e)}")
            raise e
    
    def _validate_bgn_keyword_materials(self, materials):
        """BGN 키워드 기반 소재 품질 검증"""
        validated = {"키워드 기반 소재": []}
        
        if "키워드 기반 소재" in materials:
            for material in materials["키워드 기반 소재"]:
                # BGN 필수 필드 확인
                required_fields = ["title", "content", "keywords", "usage_point", "staff_perspective", "bgn_brand_fit"]
                if all(key in material for key in required_fields):
                    # BGN 브랜드 적합성 체크
                    if len(material["content"]) >= 100:  # BGN 최소 내용 길이
                        if len(material.get("keywords", [])) >= 4:  # BGN 키워드 수
                            # BGN 브랜드 요소 확인
                            bgn_elements = ["BGN", "따뜻", "전문", "신뢰", "케어", "소통"]
                            if any(element in material.get("bgn_brand_fit", "") for element in bgn_elements):
                                validated["키워드 기반 소재"].append(material)
        
        # BGN 최소 소재 수 보장
        if len(validated["키워드 기반 소재"]) < 4:
            st.warning("⚠️ BGN 브랜드 적합 소재가 부족합니다. BGN 샘플 소재를 추가합니다.")
            validated = self._get_bgn_keyword_fallback_materials()
        
        return validated
    
    def _get_bgn_keyword_fallback_materials(self):
        """BGN 브랜드 키워드 기반 폴백 소재"""
        return {
            "키워드 기반 소재": [
                {
                    "title": "BGN 검안사가 경험한 20대 직장인의 라식 결심기 - 마스크 시대의 새로운 선택",
                    "content": "매일 아침 안경을 찾으며 하루를 시작하고, 마스크 착용으로 더욱 불편해진 일상을 견디다 BGN을 찾아온 김OO(27세, 회사원)님의 진솔한 이야기입니다. 특히 재택근무와 마스크 착용이 일상화되면서 안경의 불편함이 더욱 커졌다고 하시더라고요.",
                    "keywords": ["BGN", "20대", "직장인", "라식", "안경", "마스크", "일상", "불편함"],
                    "timestamp": "인터뷰 초반부 15-25분 구간",
                    "usage_point": "BGN 검안사 시점에서 동일한 고민을 가진 젊은 직장인들의 공감대 형성, 라식 수술 결심 과정의 심리적 변화, BGN만의 세심한 상담 과정으로 2000자 이상 확장",
                    "staff_perspective": "검안사",
                    "target_audience": "예비 환자",
                    "direct_quote": "매일 아침에 안경부터 찾아야 하는 게 정말 스트레스였어요",
                    "bgn_brand_fit": "BGN의 환자 맞춤 상담과 공감적 소통, 젊은 층에 대한 이해",
                    "emotion_tone": "따뜻한 공감과 전문적 조언"
                },
                {
                    "title": "BGN 간호사가 본 50대 주부의 백내장 수술 후 달라진 일상 - 다시 찾은 선명한 세상",
                    "content": "요리할 때 양념통을 구분하지 못하고, TV 자막이 흐려 보이던 박OO(52세, 주부)님이 BGN에서 백내장 수술 후 20년 전처럼 선명해진 시야를 되찾으신 감동적인 회복 스토리입니다. 수술 전 불안감부터 수술 후 놀라운 변화까지의 전 과정이 생생하게 담겨있습니다.",
                    "keywords": ["BGN", "50대", "주부", "백내장", "수술후기", "회복", "일상변화", "시야개선"],
                    "timestamp": "인터뷰 중반부 30-45분 구간",
                    "usage_point": "BGN 간호사 관점에서 중장년층 환자들의 백내장 수술 불안감 해소, 수술 과정 상세 설명, 회복기간 정보, 삶의 질 개선 사례로 2000자 이상 확장",
                    "staff_perspective": "간호사",
                    "target_audience": "기존 환자",
                    "direct_quote": "수술 후 처음 밖에 나갔을 때 나뭇잎 하나하나가 다 보여서 울컥했어요",
                    "bgn_brand_fit": "BGN의 세심한 수술 후 케어와 환자 중심 서비스",
                    "emotion_tone": "감동적이고 희망적인 분위기"
                },
                {
                    "title": "BGN 원무팀이 매일 듣는 환자들의 진짜 속마음 - 불안에서 안심으로",
                    "content": "BGN 원무팀에서 근무하며 매일 다양한 환자분들의 첫 방문부터 치료 완료까지의 과정을 지켜보면서 느끼는 특별한 순간들입니다. 처음 오실 때의 걱정스러운 표정이 점차 밝아지는 모습을 보는 것이 가장 큰 보람이라고 합니다.",
                    "keywords": ["BGN", "원무팀", "환자", "상담", "불안감", "신뢰", "서비스", "케어"],
                    "timestamp": "인터뷰 후반부 50-60분 구간",
                    "usage_point": "BGN 원무팀 시점에서 환자들의 심리적 변화 과정, BGN의 차별화된 서비스 문화, 환자 중심 운영 철학으로 2000자 이상 확장",
                    "staff_perspective": "원무팀",
                    "target_audience": "일반인",
                    "direct_quote": "처음에는 많이 긴장하셨는데, 상담 후에는 표정이 완전히 달라지시더라고요",
                    "bgn_brand_fit": "BGN의 환자 중심 서비스와 신뢰 구축 과정",
                    "emotion_tone": "자연스러운 소통과 신뢰감"
                },
                {
                    "title": "BGN 신입 검안사의 첫 수술실 경험 - 긴장에서 감동까지",
                    "content": "BGN에 입사한 지 3개월 된 신입 검안사로서 처음 수술실에 들어간 날의 떨림과 점차 적응해가는 과정, 그리고 환자분들로부터 받는 감사 인사에 대한 소중한 경험담입니다. 선배들의 세심한 지도와 BGN만의 교육 시스템이 인상적이었다고 합니다.",
                    "keywords": ["BGN", "신입", "검안사", "수술실", "성장", "교육", "멘토링", "팀워크"],
                    "timestamp": "인터뷰 중반부 35-50분 구간",
                    "usage_point": "BGN 의료진의 인간적인 면모와 성장 스토리, BGN의 교육 시스템과 팀워크 문화, 환자 케어에 대한 사명감으로 2000자 이상 확장",
                    "staff_perspective": "신입 검안사",
                    "target_audience": "일반인",
                    "direct_quote": "첫 수술 참관 때 환자분이 고맙다고 하시는데 정말 울컥했어요",
                    "bgn_brand_fit": "BGN의 체계적인 교육과 따뜻한 조직문화",
                    "emotion_tone": "성장과 감동의 스토리"
                }
            ]
        }

    # 기존 메서드들 (호환성 유지)
    def analyze_interview_content(self, content):
        """기존 카테고리 기반 분석 (호환성 유지)"""
        return self.analyze_interview_content_keyword_based(content)

def get_sample_materials():
    """BGN 브랜드 샘플 소재 데이터 (업데이트)"""
    return {
        "키워드 기반 소재": [
            {
                "title": "BGN 검안사가 본 20대 직장인의 라식 여정 - 안경에서 자유로워지기까지",
                "content": "매일 아침 안경을 찾는 것부터 시작되는 일상, 운동할 때마다 흘러내리는 안경, 마스크 착용 시 서리는 불편함을 견디다가 드디어 라식을 결심한 김OO(27세, 회사원)님의 진솔한 이야기입니다.",
                "keywords": ["BGN", "20대", "직장인", "라식", "안경", "불편함", "결심", "일상"],
                "timestamp": "인터뷰 초반부 10-15분 구간",
                "usage_point": "BGN 검안사 시점에서 동일한 고민을 가진 젊은 직장인들의 공감대 형성",
                "staff_perspective": "검안사",
                "target_audience": "예비 환자",
                "direct_quote": "매일 아침에 안경부터 찾아야 하는 게 정말 스트레스였어요",
                "bgn_brand_fit": "BGN의 환자 맞춤 상담과 공감적 소통"
            },
            {
                "title": "BGN 간호사가 경험한 50대 주부의 백내장 수술 성공기 - 새로운 세상을 보다",
                "content": "일상생활이 불편할 정도로 시야가 흐려져 내원한 환자분의 치료 과정과 회복 후기입니다.",
                "keywords": ["BGN", "50대", "주부", "백내장", "수술후기", "회복", "일상변화"],
                "timestamp": "인터뷰 중반부 25-35분 구간",
                "usage_point": "BGN 간호사 관점에서 중장년층 환자들의 치료 과정과 변화",
                "staff_perspective": "간호사",
                "target_audience": "기존 환자"
            }
        ]
    }