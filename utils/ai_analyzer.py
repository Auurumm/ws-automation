import json
import time
import streamlit as st
from openai import OpenAI
from config import OPENAI_CONFIG, CONTENT_TYPES, QUALITY_CONFIG


class AIAnalyzer:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.config = OPENAI_CONFIG

    # ---------------------------------------------------------------------
    # 블로그 생성 (2-step: OUTLINE → DRAFT) + 사후 톤 보정
    # ---------------------------------------------------------------------
    def generate_blog_content_bgn_style(
        self,
        selected_material,
        style,
        length,
        additional_request,
        bgn_style_params,
        *,
        temperature=0.9,
        top_p=0.9,
    ):
        material = selected_material["data"]
        staff_role = bgn_style_params.get("staff_role", "검안사")
        staff_name = bgn_style_params.get("staff_name", "김서연")

        length_config = {
            "표준 품질 (2,000자 이상)": {"min_chars": 2000, "target_chars": 2200, "max_tokens": 4500},
            "고품질 (2,500자 이상)": {"min_chars": 2500, "target_chars": 2800, "max_tokens": 6000},
            "프리미엄 (3,000자 이상)": {"min_chars": 3000, "target_chars": 3300, "max_tokens": 7000},
        }
        cfg = length_config.get(length, length_config["표준 품질 (2,000자 이상)"])

        # 입력 과대 방지 (토큰 초과 방지)
        if len(material.get("content", "")) > 8000:
            material["content"] = material["content"][:8000]

        # 1) OUTLINE
        outline = self._make_outline(
            material=material,
            style=style,
            staff_role=staff_role,
            staff_name=staff_name,
            min_chars=cfg["min_chars"],
            additional_request=additional_request,
            temperature=temperature,
            top_p=top_p,
        )

        # 2) DRAFT
        draft = self._draft_from_outline(
            outline=outline,
            material=material,
            target_chars=cfg["target_chars"],
            staff_role=staff_role,
            staff_name=staff_name,
            temperature=temperature,
            top_p=top_p,
            max_tokens=cfg["max_tokens"],
        )

        # 3) 사후 톤 보정
        if len(draft) < cfg["min_chars"]:
            shortage = cfg["min_chars"] - len(draft)
            draft = self._style_pass(
                text=draft,
                staff_role=staff_role,
                staff_name=staff_name,
                shortage=shortage,
                temperature=min(temperature, 0.8),
                top_p=top_p,
                max_tokens=cfg["max_tokens"],
            )

        # 최종 검증(점수는 UI 참고용)
        _ = self._validate_bgn_style(draft, cfg["min_chars"])
        return draft

    # -------------------- helpers --------------------
    def _make_outline(
        self, material, style, staff_role, staff_name, min_chars, additional_request, temperature, top_p
    ):
        prompt = f"""
다음 내용을 바탕으로 블로그 아웃라인을 작성하세요.

- 병원: BGN밝은눈안과(잠실점)
- 화자: {staff_role} {staff_name} (1인칭)
- 글 최소 분량: {min_chars}자 이상
- 글 분위기: 따뜻함과 전문성의 균형, 과장/권유 금지
- 스타일: {style}
- 소재 제목: {material.get('title','')}
- 핵심 내용: {material.get('content','')}
- 활용 포인트: {material.get('usage_point','')}
- 추가 요청: {additional_request or '없음'}

요청: H2/H3 헤딩 구조의 JSON 아웃라인을 출력.
필드: title, h2_sections[{{"h2": str, "bullets": [str], "h3": [str]}}]
JSON만 출력.
"""
        res = self.client.chat.completions.create(
            model=self.config["model"],
            messages=[
                {"role": "system", "content": "간결한 편집자. 사용자 요청만 JSON으로 응답."},
                {"role": "user", "content": prompt},
            ],
            temperature=temperature,
            top_p=top_p,
            max_tokens=1200,
        ).choices[0].message.content

        try:
            start, end = res.find("{"), res.rfind("}") + 1
            return json.loads(res[start:end])
        except Exception:
            # 최소 안전 아웃라인
            return {
                "title": material.get("title", "BGN 블로그"),
                "h2_sections": [
                    {"h2": "오늘도 이런 일이 있었어요", "bullets": [], "h3": []},
                    {"h2": "사실 저희도 많이 배워요", "bullets": [], "h3": []},
                    {"h2": "그래서 더 세심하게 봐드렸어요", "bullets": [], "h3": []},
                    {"h2": "비슷한 고민을 하고 계신다면", "bullets": [], "h3": []},
                    {"h2": "마지막으로 하고 싶은 말", "bullets": [], "h3": []},
                ],
            }

    def _draft_from_outline(
        self, outline, material, target_chars, staff_role, staff_name, temperature, top_p, max_tokens
    ):
        import json as _json

        prompt = f"""
아래 JSON 아웃라인과 소재로 블로그 초안을 작성하세요.

규칙(필수 최소화):
- 시작 멘트: "안녕하세요, BGN밝은눈안과(잠실점) {staff_role} {staff_name}입니다."
- 1인칭 시점 유지, 과장/권유 금지, 자연스러운 구어체 허용
- 총 분량 목표: 약 {target_chars}자 (모자라면 상관없음)
- H2/H3 구조 유지
- 후기형 과장 문구 금지

아웃라인 JSON:
{_json.dumps(outline, ensure_ascii=False)}

소재 요약:
- 제목: {material.get('title','')}
- 내용: {material.get('content','')}
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
            max_tokens=max_tokens,
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
            max_tokens=max_tokens,
        )
        return res.choices[0].message.content

    def _validate_bgn_style(self, blog_content: str, min_chars: int):
        """BGN 톤앤매너 간단 검증 (UI 참고용 점수)"""
        bgn_score = 0.5
        improvement_suggestions = []

        bgn_elements = {
            "has_bgn_intro": "BGN밝은눈안과(잠실점)" in blog_content[:300],
            "has_bgn_outro": "BGN밝은눈안과(잠실점)" in blog_content[-300:],
            "has_staff_intro": any(role in blog_content[:200] for role in ["검안사", "간호사", "원무팀", "의료진"]),
            "has_daily_episode": ("오늘도 이런 일이" in blog_content) or ("오늘" in blog_content[:500]),
        }
        if sum(bgn_elements.values()) >= 3:
            bgn_score += 0.2
        else:
            improvement_suggestions.append("BGN 브랜드 요소 강화 필요")

        tone_variety = {
            "ending_variety": len([end for end in ["해요", "습니다", "죠", "거든요", "더라고요", "라고요"] if end in blog_content]),
            "emotion_expressions": any(expr in blog_content for expr in [":)", "ㅠㅠ", "...", "웃음이", "울컥"]),
            "empathy_words": any(word in blog_content for word in ["괜찮", "함께", "옆에 있", "이해"]),
        }
        if tone_variety["ending_variety"] >= 4:
            bgn_score += 0.15
        elif tone_variety["ending_variety"] >= 2:
            bgn_score += 0.1
        else:
            improvement_suggestions.append("종결어미 다양성 부족")

        if tone_variety["emotion_expressions"]:
            bgn_score += 0.1
        else:
            improvement_suggestions.append("감정 표현 부족")

        if tone_variety["empathy_words"]:
            bgn_score += 0.05
        else:
            improvement_suggestions.append("공감 표현 부족")

        bgn_phrases = ["저희도 많이 배워요", "별거 아닌 것 같아도", "무리하게 권하지", "편하게 물어보세요", "특별한 걸 한 건 아니에요"]
        if sum(1 for phrase in bgn_phrases if phrase in blog_content) >= 2:
            bgn_score += 0.1
        else:
            improvement_suggestions.append("BGN 특화 표현 부족")

        return {
            "bgn_score": min(bgn_score, 1.0),
            "improvement_suggestions": improvement_suggestions or ["BGN 톤앤매너가 잘 적용되었습니다"],
            "bgn_elements": bgn_elements,
            "tone_variety": tone_variety,
        }

    # ---------------------------------------------------------------------
    # 인터뷰 → 소재 도출 (키워드 기반)  +  UI 탭 구조로 카테고리화
    # ---------------------------------------------------------------------
    def analyze_interview_content_keyword_based(self, content: str):
        content_length = len(content)
        if content_length <= 15000:
            st.info(f"📄 텍스트 길이: {content_length:,}자 - BGN 맞춤 키워드 분석")
            return self._analyze_keywords_for_bgn(content)
        else:
            st.warning(f"📄 텍스트 길이: {content_length:,}자 - BGN 앞부분 분석으로 진행")
            return self._analyze_keywords_for_bgn(content[:15000])

    def _analyze_keywords_for_bgn(self, content: str):
        prompt = f"""
BGN밝은눈안과(잠실점) 직원 인터뷰에서 BGN 브랜드에 맞는 블로그 소재를 추출해주세요.

📋 인터뷰 내용:
{content}

📝 결과 형식(JSON):
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
      "direct_quote": "직접 인용구(있다면)",
      "bgn_brand_fit": "따뜻함/전문성/신뢰 연결",
      "emotion_tone": "감정 톤"
    }}
  ]
}}

⚠️ 조건:
- 6개 이상, 서로 다른 관점/주제
- 인터뷰에 실제 언급된 내용만 사용
- BGN 톤앤매너로 2000자 이상 확장 가능
"""
        try:
            response = self.client.chat.completions.create(
                model=self.config["model"],
                messages=[
                    {
                        "role": "system",
                        "content": "당신은 BGN밝은눈안과 전문 콘텐츠 기획자입니다. 인터뷰에서 실 사례 기반 소재만 추출하세요.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                max_tokens=4000,
            )
            result = response.choices[0].message.content or ""
            start = result.find("{")
            end = result.rfind("}") + 1
            if start == -1 or end <= start:
                raise json.JSONDecodeError("JSON 형식 찾기 실패", result, 0)

            materials = json.loads(result[start:end])

            # 1) 유효성 검사
            validated_materials = self._validate_bgn_keyword_materials(materials)

            # 2) 카테고리화 (UI 탭 구조에 맞춤)
            categorized = self._categorize_bgn_materials(validated_materials.get("키워드 기반 소재", []))

            st.success("✅ BGN 브랜드 맞춤 키워드 분석 완료!")
            return categorized

        except json.JSONDecodeError:
            st.warning("BGN 분석 결과 파싱 실패 - BGN 샘플 데이터로 대체")
            return self._categorize_bgn_materials(self._get_bgn_keyword_fallback_materials()["키워드 기반 소재"])
        except Exception as e:
            st.error(f"BGN 키워드 분석 실패: {str(e)}")
            return self._categorize_bgn_materials(self._get_bgn_keyword_fallback_materials()["키워드 기반 소재"])

    def _validate_bgn_keyword_materials(self, materials: dict):
        validated = {"키워드 기반 소재": []}
        items = materials.get("키워드 기반 소재", [])
        for it in items:
            required = ["title", "content", "keywords", "usage_point", "staff_perspective"]
            if not all(k in it for k in required):
                continue
            if len(it.get("content", "")) < 100:
                continue
            if len(it.get("keywords", [])) < 4:
                continue
            validated["키워드 기반 소재"].append(it)

        if len(validated["키워드 기반 소재"]) < 4:
            st.warning("⚠️ BGN 브랜드 적합 소재가 부족합니다. 샘플을 보강합니다.")
            validated = self._get_bgn_keyword_fallback_materials()
        return validated

    def _get_bgn_keyword_fallback_materials(self) -> dict:
        """최소 4개 샘플"""
        return {
            "키워드 기반 소재": [
                {
                    "title": "BGN 검안사가 경험한 20대 직장인의 라식 결심기 - 마스크 시대의 새로운 선택",
                    "content": "매일 아침 안경을 찾으며 하루를 시작하고, 마스크 착용으로 더욱 불편해진 일상을 견디다 BGN을 찾아온 김OO(27세, 회사원)님의 이야기입니다.",
                    "keywords": ["BGN", "20대", "직장인", "라식", "안경", "일상", "불편함"],
                    "timestamp": "초반 15-25분",
                    "usage_point": "검안사 시점 공감대 형성, 상담 과정, 결심 과정으로 확장",
                    "staff_perspective": "검안사",
                    "target_audience": "예비 환자",
                    "bgn_brand_fit": "맞춤 상담·공감적 소통",
                    "emotion_tone": "따뜻한 공감",
                },
                {
                    "title": "BGN 간호사가 본 50대 주부의 백내장 수술 후 달라진 일상",
                    "content": "요리할 때 양념통을 구분하지 못하고 TV 자막이 흐려 보이던 환자분이 수술 후 선명한 시야를 되찾은 회복 스토리.",
                    "keywords": ["BGN", "50대", "주부", "백내장", "수술후기", "회복", "일상변화"],
                    "timestamp": "중반 30-45분",
                    "usage_point": "불안 해소, 수술 과정·회복 정보로 확장",
                    "staff_perspective": "간호사",
                    "target_audience": "기존 환자",
                    "bgn_brand_fit": "세심한 수술 후 케어",
                    "emotion_tone": "희망적",
                },
                {
                    "title": "BGN 원무팀이 매일 듣는 환자들의 진짜 속마음 - 불안에서 안심으로",
                    "content": "첫 방문의 걱정스런 표정이 상담 뒤 밝아지는 과정에서 느낀 보람과 관찰 기록.",
                    "keywords": ["BGN", "원무팀", "상담", "불안", "신뢰", "서비스"],
                    "timestamp": "후반 50-60분",
                    "usage_point": "상담 플로우, 서비스 문화 소개로 확장",
                    "staff_perspective": "원무팀",
                    "target_audience": "일반인",
                    "bgn_brand_fit": "환자 중심 서비스",
                    "emotion_tone": "신뢰감",
                },
                {
                    "title": "BGN 신입 검안사의 첫 수술실 경험 - 긴장에서 감동까지",
                    "content": "처음 수술실에 들어간 날의 떨림과 적응, 선배들의 지도, 환자 감사 인사에서 느낀 성장.",
                    "keywords": ["BGN", "신입", "검안사", "수술실", "성장", "멘토링"],
                    "timestamp": "중반 35-50분",
                    "usage_point": "교육 시스템·팀워크 문화 소개로 확장",
                    "staff_perspective": "검안사",
                    "target_audience": "일반인",
                    "bgn_brand_fit": "체계적 교육·따뜻한 문화",
                    "emotion_tone": "감동",
                },
            ]
        }

    def _categorize_bgn_materials(self, items: list) -> dict:
        """UI 탭 구조로 분류"""
        out = {
            "BGN 환자 에피소드": [],
            "BGN 검사·과정": [],
            "BGN 센터 운영/분위기": [],
            "BGN 직원 성장기": [],
            "BGN 환자 질문 FAQ": [],
            "키워드 기반 소재": items[:],
        }

        def put(cat, it):
            out[cat].append(it)

        for it in items:
            text = f"{it.get('title','')} {it.get('content','')} {', '.join(it.get('keywords', []))}".lower()
            role = (it.get("staff_perspective") or "").lower()
            audience = (it.get("target_audience") or "")

            if any(k in text for k in ["수술", "회복", "후기", "변화", "감동", "울컥"]) or "예비 환자" in audience:
                put("BGN 환자 에피소드", it)
                continue
            if any(k in text for k in ["검사", "장비", "과정", "측정", "결과", "프로세스", "진단"]):
                put("BGN 검사·과정", it)
                continue
            if any(k in text for k in ["운영", "분위기", "대기시간", "예약", "서비스", "시스템", "원무"]) or "원무" in role:
                put("BGN 센터 운영/분위기", it)
                continue
            if any(k in text for k in ["신입", "멘토", "멘토링", "교육", "배움", "첫 수술", "성장"]) or "신입" in role:
                put("BGN 직원 성장기", it)
                continue
            if any(k in text for k in ["질문", "언제", "가능", "방법", "주의", "faq", "자주 묻는"]):
                put("BGN 환자 질문 FAQ", it)
                continue

            put("BGN 환자 에피소드", it)

        # 모두 비면 샘플로 채움
        if not any(out[k] for k in ["BGN 환자 에피소드", "BGN 검사·과정", "BGN 센터 운영/분위기", "BGN 직원 성장기", "BGN 환자 질문 FAQ"]):
            fb = self._get_bgn_keyword_fallback_materials()["키워드 기반 소재"]
            return self._categorize_bgn_materials(fb)

        return out

    # ---------------------------------------------------------------------
    # 호환용 진입점 (옛 코드 호출 대비)
    # ---------------------------------------------------------------------
    def analyze_interview_content(self, content: str):
        return self.analyze_interview_content_keyword_based(content)


# (선택) 샘플 데이터 제공 함수
def get_sample_materials():
    return {
        "키워드 기반 소재": [
            {
                "title": "BGN 검안사가 본 20대 직장인의 라식 여정 - 안경에서 자유로워지기까지",
                "content": "매일 아침 안경을 찾는 것부터 시작되는 일상…",
                "keywords": ["BGN", "20대", "직장인", "라식", "안경", "불편함", "결심", "일상"],
                "timestamp": "초반 10-15분",
                "usage_point": "검안사 시점 공감대 형성",
                "staff_perspective": "검안사",
                "target_audience": "예비 환자",
            }
        ]
    }
