import json
import streamlit as st
from openai import OpenAI
from config import OPENAI_CONFIG, CONTENT_TYPES, QUALITY_CONFIG
import time

class AIAnalyzer:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)
        self.config = OPENAI_CONFIG
    
    # --- ai_analyzer.py: drop-in replacement for generate_blog_content_bgn_style ---

def generate_blog_content_bgn_style(
    self,
    selected_material,
    style,
    length,
    additional_request,
    bgn_style_params,
    *,
    temperature=0.9,
    top_p=0.9
):
    """
    2-step 생성(아웃라인→본문) + 사후 톤 보정.
    - 프롬프트를 간결화해 모델을 과도하게 제약하지 않음
    - 글자수/톤 검증은 사후 처리
    """

    material = selected_material['data']
    staff_role = bgn_style_params.get('staff_role', '검안사')
    staff_name = bgn_style_params.get('staff_name', '김서연')

    length_config = {
        "표준 품질 (2,000자 이상)": {"min_chars": 2000, "target_chars": 2200, "max_tokens": 4500},
        "고품질 (2,500자 이상)": {"min_chars": 2500, "target_chars": 2800, "max_tokens": 6000},
        "프리미엄 (3,000자 이상)": {"min_chars": 3000, "target_chars": 3300, "max_tokens": 7000}
    }
    cfg = length_config.get(length, length_config["표준 품질 (2,000자 이상)"])
    
    # 🔽 이 부분에 추가
    # 너무 긴 입력은 잘라내기 (토큰 초과 방지)
    if len(material['content']) > 8000:
        material['content'] = material['content'][:8000]

    # ---- 1) OUTLINE (짧고 명확) ----
    outline = self._make_outline(
        material=material,
        style=style,
        staff_role=staff_role,
        staff_name=staff_name,
        min_chars=cfg["min_chars"],
        additional_request=additional_request,
        temperature=temperature,
        top_p=top_p
    )

    # ---- 2) DRAFT 본문 ----
    draft = self._draft_from_outline(
        outline=outline,
        material=material,
        target_chars=cfg["target_chars"],
        staff_role=staff_role,
        staff_name=staff_name,
        temperature=temperature,
        top_p=top_p,
        max_tokens=cfg["max_tokens"]
    )

    # ---- 3) 사후 톤 보정(필요 시) ----
    if len(draft) < cfg["min_chars"]:
        shortage = cfg["min_chars"] - len(draft)
        draft = self._style_pass(
            text=draft,
            staff_role=staff_role,
            staff_name=staff_name,
            shortage=shortage,
            temperature=min(temperature, 0.8),
            top_p=top_p,
            max_tokens=cfg["max_tokens"]
        )

    # 최종 검증 및 리턴
    bgn_validation = self._validate_bgn_style(draft, cfg["min_chars"])
    return draft

# --- helpers ---

def _make_outline(self, material, style, staff_role, staff_name, min_chars, additional_request, temperature, top_p):
    prompt = f"""
다음 내용을 바탕으로 블로그 아웃라인을 작성하세요.

- 병원: BGN밝은눈안과(잠실점)
- 화자: {staff_role} {staff_name} (1인칭)
- 글 최소 분량: {min_chars}자 이상
- 글 분위기: 따뜻함과 전문성의 균형, 과장/권유 금지
- 스타일: {style}
- 소재 제목: {material['title']}
- 핵심 내용: {material['content']}
- 활용 포인트: {material.get('usage_point','')}
- 추가 요청: {additional_request or '없음'}

요청: H2/H3 헤딩 구조의 JSON 아웃라인을 출력.
필드: title, h2_sections[{ {{"h2": str, "bullets": [str], "h3": [str]}} }]
JSON만 출력.
"""
    res = self.client.chat.completions.create(
        model=self.config["model"],
        messages=[
            {"role": "system", "content": "간결한 편집자. 사용자 요청만 JSON으로 응답."},
            {"role": "user", "content": prompt}
        ],
        temperature=temperature,
        top_p=top_p,
        max_tokens=1200,
    ).choices[0].message.content

    try:
        import json
        start, end = res.find("{"), res.rfind("}") + 1
        return json.loads(res[start:end])
    except Exception:
        # 최소 안전 아웃라인
        return {
            "title": material["title"],
            "h2_sections": [
                {"h2": "오늘도 이런 일이 있었어요", "bullets": [], "h3": []},
                {"h2": "사실 저희도 많이 배워요", "bullets": [], "h3": []},
                {"h2": "그래서 더 세심하게 봐드렸어요", "bullets": [], "h3": []},
                {"h2": "비슷한 고민을 하고 계신다면", "bullets": [], "h3": []},
                {"h2": "마지막으로 하고 싶은 말", "bullets": [], "h3": []},
            ],
        }

def _draft_from_outline(self, outline, material, target_chars, staff_role, staff_name, temperature, top_p, max_tokens):
    import json
    prompt = f"""
아래 JSON 아웃라인과 소재로 블로그 초안을 작성하세요.

규칙(필수 최소화):
- 시작 멘트: "안녕하세요, BGN밝은눈안과(잠실점) {staff_role} {staff_name}입니다."
- 1인칭 시점 유지, 과장/권유 금지, 자연스러운 구어체 허용
- 총 분량 목표: 약 {target_chars}자 (모자라면 상관없음)
- H2/H3 구조 유지
- 이미지 ALT/홍보 멘트/후기형 과장 문구 금지

아웃라인 JSON:
{json.dumps(outline, ensure_ascii=False)}

소재 요약:
- 제목: {material['title']}
- 내용: {material['content']}
- 키워드: {', '.join(material.get('keywords', [])[:8])}
"""
    res = self.client.chat.completions.create(
        model=self.config["model"],
        messages=[
            {"role": "system", "content": "따뜻하고 담백한 의료 콘텐츠 작가."},
            {"role": "user", "content": prompt},
        ],
        temperature=temperature,
        top_p=top_p,
        max_tokens=max_tokens
    )
    return res.choices[0].message.content

def _style_pass(self, text, staff_role, staff_name, shortage, temperature, top_p, max_tokens):
    prompt = f"""
다음 글을 BGN 톤으로 자연스럽게 보강하세요.

- 병원: BGN밝은눈안과(잠실점)
- 화자: {staff_role} {staff_name} 1인칭
- 목표: 과도한 반복 없이 내용의 구체성/경험담을 추가하여 {shortage}자 이상 보강
- 금지: 과장된 치료효과 단정, 후기형 홍보, 과도한 이모티콘
- 유지: 기존 문장과 흐름

원문:
{text}
"""
    res = self.client.chat.completions.create(
        model=self.config["model"],
        messages=[
            {"role": "system", "content": "세심한 카피에디터."},
            {"role": "user", "content": prompt},
        ],
        temperature=temperature,
        top_p=top_p,
        max_tokens=max_tokens
    )
    return res.choices[0].message.content

    
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
                    categorized = self._categorize_bgn_materials(validated_materials.get("키워드 기반 소재", []))

                    st.success("✅ BGN 브랜드 맞춤 키워드 분석 완료!")
                    return categorized
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

    def _categorize_bgn_materials(self, items):
        """
        UI 탭 구조에 맞게 소재를 분류해서 반환.
        반환 구조:
        {
        "BGN 환자 에피소드": [...],
        "BGN 검사·과정": [...],
        "BGN 센터 운영/분위기": [...],
        "BGN 직원 성장기": [...],
        "BGN 환자 질문 FAQ": [...],
        "키워드 기반 소재": [...]  # 원본도 유지(선택)
        }
        """
        # 기본 컨테이너
        out = {
            "BGN 환자 에피소드": [],
            "BGN 검사·과정": [],
            "BGN 센터 운영/분위기": [],
            "BGN 직원 성장기": [],
            "BGN 환자 질문 FAQ": [],
            "키워드 기반 소재": items[:]  # 원본 보존(원하시면 삭제 가능)
        }

        # 간단한 규칙 기반 분류(키워드/내용/직무)
        def put(cat, it): out[cat].append(it)

        for it in items:
            text = f"{it.get('title','')} {it.get('content','')} {', '.join(it.get('keywords', []))}".lower()
            role = (it.get('staff_perspective') or "").lower()

            # 1) 환자 에피소드: 수술/회복/후기/변화/감정
            if any(k in text for k in ["수술", "회복", "후기", "일상 변화", "감동", "울컥"]) \
            or "예비 환자" in (it.get("target_audience","")):
                put("BGN 환자 에피소드", it); continue

            # 2) 검사·과정: 검사/장비/과정/측정/결과/프로세스
            if any(k in text for k in ["검사", "장비", "과정", "측정", "결과", "프로세스", "진단"]):
                put("BGN 검사·과정", it); continue

            # 3) 센터 운영/분위기: 대기시간/예약/서비스/분위기/운영/시스템
            if any(k in text for k in ["운영", "분위기", "대기시간", "예약", "서비스", "시스템", "원무"]) \
            or "원무" in role:
                put("BGN 센터 운영/분위기", it); continue

            # 4) 직원 성장기: 신입/멘토링/교육/배움/첫 경험/성장
            if any(k in text for k in ["신입", "멘토", "멘토링", "교육", "배움", "첫 수술", "성장"]) \
            or "신입" in role:
                put("BGN 직원 성장기", it); continue

            # 5) 환자 질문 FAQ: 언제/가능/방법/주기/주의/자주 묻는 질문
            if any(k in text for k in ["질문", "언제", "가능", "방법", "주의", "faq", "자주 묻는"]):
                put("BGN 환자 질문 FAQ", it); continue

            # 아무 데도 안 들어가면, 내용 기반으로 안전 분류
            put("BGN 환자 에피소드", it)

        # 비어있는 탭 최소 채우기(폴백 재활용)
        if not any(out[cat] for cat in ["BGN 환자 에피소드","BGN 검사·과정","BGN 센터 운영/분위기","BGN 직원 성장기","BGN 환자 질문 FAQ"]):
            # 전부 빈 경우: 폴백 생성
            fb = self._get_bgn_keyword_fallback_materials()["키워드 기반 소재"]
            return self._categorize_bgn_materials(fb)

        return out
    
# 클래스 AIAnalyzer 내부에 존재해야 함
def analyze_interview_content(self, content: str):
    """
    (호환용) 예전 코드가 호출하는 진입점.
    내부적으로 최신 키워드 기반/카테고리화 로직을 호출합니다.
    """
    return self.analyze_interview_content_keyword_based(content)
