import json
import streamlit as st
from openai import OpenAI
from config import OPENAI_CONFIG, CONTENT_TYPES, QUALITY_CONFIG


# NOTE:
# - CONTENT_TYPES의 키는 material_analysis.py가 기대하는 탭 키와 '정확히' 일치해야 합니다.
#   예: "BGN 환자 에피소드형", "BGN 검사·과정형", "BGN 센터 운영/분위기형", "BGN 직원 성장기형", "BGN 환자 질문 FAQ형"
# - 아래 _categorize_bgn_materials()는 반드시 위 키로 반환합니다.


class AIAnalyzer:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.config = OPENAI_CONFIG

    # ---------------------------------------------------------------------
    # 인터뷰 → 소재 도출 (키워드 기반)  +  UI 탭 구조로 카테고리화
    # ---------------------------------------------------------------------
    def analyze_interview_content_keyword_based(self, content: str):
        """인터뷰 전문에서 BGN 브랜드 톤에 맞는 블로그 소재를 도출해
        UI 탭 키와 '정확히' 일치하는 dict로 반환합니다.
        """
        text_len = len(content or "")
        threshold = 15000
        if text_len > threshold:
            st.warning(f"📏 텍스트가 {text_len:,}자입니다. 앞 {threshold:,}자만 우선 분석합니다.")
            content = content[:threshold]

        try:
            payload = self._analyze_keywords_for_bgn(content)
        except Exception as e:
            st.warning(f"분석 실패 → 샘플 폴백 사용: {e}")
            payload = self._get_bgn_keyword_fallback_materials()

        # 1) 유효성 검증
        validated = self._validate_bgn_keyword_materials(payload)

        # 2) 카테고리화 (반드시 '...형' 키로 반환)
        categorized = self._categorize_bgn_materials(validated.get("키워드 기반 소재", []))

        # 3) 모든 탭 완전 비어있으면 샘플로 채움
        if not any(categorized.get(k) for k in [
            "BGN 환자 에피소드형", "BGN 검사·과정형", "BGN 센터 운영/분위기형",
            "BGN 직원 성장기형", "BGN 환자 질문 FAQ형"
        ]):
            fb = self._get_bgn_keyword_fallback_materials()["키워드 기반 소재"]
            categorized = self._categororize_fallback_if_empty(fb)

        st.success("✅ BGN 브랜드 맞춤 키워드 분석 완료!")
        return categorized

    def _analyze_keywords_for_bgn(self, content: str) -> dict:
        """모델 호출: 인터뷰 기반 + 공신력 있는 일반 의학 설명 보강 허용(과장/후기 금지)."""
        prompt = f"""
다음은 BGN밝은눈안과(잠실점) 직원 인터뷰 전문 일부입니다.
이 텍스트를 기반으로 블로그로 확장 가능한 '소재'를 추출하세요.

[인터뷰 내용]
{content}

[출력 형식(JSON)]
{{
  "키워드 기반 소재": [
    {{
      "title": "BGN 직원 1인칭 관점의 구체적이고 따뜻한 제목",
      "content": "인터뷰에서 실제 언급된 구체 내용(≥120자). 독자 이해를 돕기 위한 공신력 있는 일반 의학 배경설명 보강 허용(과장/후기/효능단정 금지).",
      "keywords": ["BGN","관련 키워드", "6~8개"],
      "timestamp": "인터뷰에서 언급된 구간(있다면)",
      "usage_point": "해당 소재로 2000자 이상 블로그를 구성하는 핵심 전개 포인트",
      "staff_perspective": "검안사/간호사/원무팀/의료진 중 하나",
      "target_audience": "예비 환자/기존 환자/일반인 중 하나",
      "direct_quote": "직접 인용(있다면)",
      "bgn_brand_fit": "따뜻함/전문성/신뢰와의 연결",
      "emotion_tone": "감정 톤(따뜻한 공감/전문적 신뢰/자연스러운 소통 등)"
    }}
  ]
}}

[중요 지침]
- 최소 6개 이상, 주제/관점이 서로 다른 소재.
- 인터뷰 '내용'을 중심으로 하되, 독자 이해를 돕는 '공신력 있는 일반 의학 설명'은 보강 가능.
- 후기처럼 보이는 표현, 과장된 치료 효과 단정, 모호한 일반화(예: "대부분")는 금지.
- BGN 톤: 따뜻함·전문성·신뢰.
- 반드시 JSON만 출력.
"""
        resp = self.client.chat.completions.create(
            model=self.config["model"],
            messages=[
                {"role": "system",
                 "content": "당신은 BGN 콘텐츠 기획자입니다. 사용자 요구에 따라 JSON만 정확히 출력합니다."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,  # 분석 단계는 일관성을 위해 낮춤
            max_tokens=4000,
        )
        txt = (resp.choices[0].message.content or "").strip()
        start, end = txt.find("{"), txt.rfind("}") + 1
        if start < 0 or end <= start:
            raise json.JSONDecodeError("JSON 파싱 실패", txt, 0)
        return json.loads(txt[start:end])

    def _validate_bgn_keyword_materials(self, materials: dict) -> dict:
        """필수 필드/최소 길이/키워드 수 검증. 부족하면 샘플로 보강."""
        out = {"키워드 기반 소재": []}
        items = (materials or {}).get("키워드 기반 소재", [])
        for it in items:
            req = ["title", "content", "keywords", "usage_point", "staff_perspective"]
            if not all(k in it for k in req):
                continue
            if len(it.get("content", "")) < 100:
                continue
            if len(it.get("keywords", [])) < 4:
                continue
            out["키워드 기반 소재"].append(it)

        if len(out["키워드 기반 소재"]) < 4:
            st.warning("⚠️ 유효 소재가 부족합니다. 샘플로 보강합니다.")
            out = self._get_bgn_keyword_fallback_materials()
        return out

    def _categorize_bgn_materials(self, items: list) -> dict:
        """UI 탭 구조와 '정확히' 일치하는 키로 분류하여 반환."""
        out = {
            "BGN 환자 에피소드형": [],
            "BGN 검사·과정형": [],
            "BGN 센터 운영/분위기형": [],
            "BGN 직원 성장기형": [],
            "BGN 환자 질문 FAQ형": [],
        }

        def put(cat, it):
            out[cat].append(it)

        for it in items:
            text = f"{it.get('title','')} {it.get('content','')} {', '.join(it.get('keywords', []))}".lower()
            role = (it.get("staff_perspective") or "").lower()
            audience = (it.get("target_audience") or "")

            # 1) 환자 에피소드형
            if any(k in text for k in ["수술", "회복", "후기", "변화", "감동", "울컥"]) or "예비 환자" in audience:
                put("BGN 환자 에피소드형", it); continue
            # 2) 검사·과정형
            if any(k in text for k in ["검사", "장비", "과정", "측정", "결과", "프로세스", "진단"]):
                put("BGN 검사·과정형", it); continue
            # 3) 센터 운영/분위기형
            if any(k in text for k in ["운영", "분위기", "대기시간", "예약", "서비스", "시스템", "원무"]) or "원무" in role:
                put("BGN 센터 운영/분위기형", it); continue
            # 4) 직원 성장기형
            if any(k in text for k in ["신입", "멘토", "멘토링", "교육", "배움", "첫 수술", "성장"]) or "신입" in role:
                put("BGN 직원 성장기형", it); continue
            # 5) 환자 질문 FAQ형
            if any(k in text for k in ["질문", "언제", "가능", "방법", "주의", "faq", "자주 묻는"]):
                put("BGN 환자 질문 FAQ형", it); continue

            # 기본은 에피소드형으로
            put("BGN 환자 에피소드형", it)

        return out

    def _categororize_fallback_if_empty(self, fb_items: list) -> dict:
        """전부 비었을 때 폴백 아이템으로 재분류."""
        return self._categorize_bgn_materials(fb_items)

    def _get_bgn_keyword_fallback_materials(self) -> dict:
        """최소 4개 샘플(실무자 시점). 이 리스트를 카테고리화에 투입합니다."""
        return {
            "키워드 기반 소재": [
                {
                    "title": "BGN 검안사가 경험한 20대 직장인의 라식 결심기 - 마스크 시대의 새로운 선택",
                    "content": "매일 아침 안경을 찾으며 시작한 하루, 마스크로 더 불편해진 일상에서 라식을 결심하기까지의 실제 상담 순간들. 상담 중 자주 드리는 일반적 안내(회복 일정, 건조감 관리 등)는 공신력 있는 범위 내에서 배경설명으로 보강합니다.",
                    "keywords": ["BGN", "20대", "직장인", "라식", "안경", "일상", "불편함"],
                    "timestamp": "초반 15-25분",
                    "usage_point": "검안사 시점 공감대 형성, 상담·결심 과정 확장",
                    "staff_perspective": "검안사",
                    "target_audience": "예비 환자",
                    "bgn_brand_fit": "맞춤 상담·공감적 소통",
                    "emotion_tone": "따뜻한 공감",
                },
                {
                    "title": "BGN 간호사가 본 50대 주부의 백내장 수술 후 달라진 일상",
                    "content": "요리할 때 양념통 구분이 어려웠던 환자분이 수술 후 선명한 시야를 되찾은 변화. 일반적인 수술 전후 주의사항 같은 배경설명은 과장 없이 보강합니다.",
                    "keywords": ["BGN", "50대", "주부", "백내장", "수술후기", "회복", "일상변화"],
                    "timestamp": "중반 30-45분",
                    "usage_point": "불안 해소, 수술·회복 정보 확장",
                    "staff_perspective": "간호사",
                    "target_audience": "기존 환자",
                    "bgn_brand_fit": "세심한 수술 후 케어",
                    "emotion_tone": "희망적",
                },
                {
                    "title": "BGN 원무팀이 매일 듣는 환자들의 진짜 속마음 - 불안에서 안심으로",
                    "content": "첫 방문의 긴장된 표정이 상담 후 달라지는 순간들. 접수/예약/대기 안내 등 일반적 운영 맥락을 권위 있게 설명.",
                    "keywords": ["BGN", "원무팀", "상담", "불안", "신뢰", "서비스"],
                    "timestamp": "후반 50-60분",
                    "usage_point": "상담 플로우·서비스 문화 소개",
                    "staff_perspective": "원무팀",
                    "target_audience": "일반인",
                    "bgn_brand_fit": "환자 중심 서비스",
                    "emotion_tone": "신뢰감",
                },
                {
                    "title": "BGN 신입 검안사의 첫 수술실 경험 - 긴장에서 감동까지",
                    "content": "처음 수술실에 들어간 날의 떨림과 적응, 선배 멘토링. 수술실 표준 절차 같은 일반적 배경도 과장 없이 설명.",
                    "keywords": ["BGN", "신입", "검안사", "수술실", "성장", "멘토링"],
                    "timestamp": "중반 35-50분",
                    "usage_point": "교육 시스템·팀워크 문화 소개",
                    "staff_perspective": "검안사",
                    "target_audience": "일반인",
                    "bgn_brand_fit": "체계적 교육·따뜻한 문화",
                    "emotion_tone": "감동",
                },
            ]
        }

    # ---------------------------------------------------------------------
    # (옛 코드 호환) 예전 호출 지점이 이 메서드를 찾습니다.
    # material_analysis.py에서 analyzer.analyze_interview_content(...)로 부르므로 유지합니다.
    # ---------------------------------------------------------------------
    def analyze_interview_content(self, content: str):
        return self.analyze_interview_content_keyword_based(content)

    # ---------------------------------------------------------------------
    # 블로그 본문 생성(2-step) — 필요 시 사용: OUTLINE → DRAFT → 사후 보강
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

        length_cfg = {
            "표준 BGN (2,000자)": {"min_chars": 2000, "target_chars": 2200, "max_tokens": 4500},
            "고품질 BGN (2,500자)": {"min_chars": 2500, "target_chars": 2700, "max_tokens": 6000},
            "프리미엄 BGN (3,000자)": {"min_chars": 3000, "target_chars": 3200, "max_tokens": 7000},
        }
        cfg = length_cfg.get(length, length_cfg["표준 BGN (2,000자)"])

        # 입력 과대 방지
        if len(material.get("content", "")) > 8000:
            material["content"] = material["content"][:8000]

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
        _ = self._validate_bgn_style(draft, cfg["min_chars"])  # 점수는 UI 참고용
        return draft

    # -------------------- helpers for blog generation --------------------
    def _make_outline(self, material, style, staff_role, staff_name, min_chars, additional_request, temperature, top_p):
        prompt = f"""
다음 내용을 바탕으로 블로그 아웃라인을 작성하세요.
- 병원: BGN밝은눈안과(잠실점)
- 화자: {staff_role} {staff_name} (1인칭)
- 글 최소 분량: {min_chars}자 이상
- 분위기: 따뜻함과 전문성, 과장/권유 금지
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

    def _draft_from_outline(self, outline, material, target_chars, staff_role, staff_name, temperature, top_p, max_tokens):
        import json as _json
        prompt = f"""
아래 JSON 아웃라인과 소재로 블로그 초안을 작성하세요.

규칙(필수 최소화):
- 시작 멘트: "안녕하세요, BGN밝은눈안과(잠실점) {staff_role} {staff_name}입니다."
- 1인칭 시점 유지, 과장/권유 금지, 자연스러운 구어체 허용
- 총 분량 목표: 약 {target_chars}자
- H2/H3 구조 유지
- 후기형 과장 문구 금지
- 인터뷰 실제 언급 내용을 중심으로 하되,
  독자 이해를 돕기 위한 공신력 있는 일반 의학 배경설명은 보강 가능(효능 단정/후기 금지)

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
- 목표: 과도한 반복 없이 구체성/경험담을 추가하여 {shortage}자 이상 보강
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
        """BGN 톤앤매너 간단 검증 (UI 참고용)"""
        bgn_score = 0.5
        improvement = []

        bgn_elements = {
            "has_bgn_intro": "BGN밝은눈안과(잠실점)" in blog_content[:300],
            "has_bgn_outro": "BGN밝은눈안과(잠실점)" in blog_content[-300:],
            "has_staff_intro": any(k in blog_content[:200] for k in ["검안사", "간호사", "원무팀", "의료진"]),
            "has_daily_episode": ("오늘도 이런 일이" in blog_content) or ("오늘" in blog_content[:500]),
        }
        if sum(bgn_elements.values()) >= 3: bgn_score += 0.2
        else: improvement.append("BGN 브랜드 요소 강화")

        ending_variety = len([e for e in ["해요", "습니다", "죠", "거든요", "더라고요", "라고요", "네요"] if e in blog_content])
        if ending_variety >= 4: bgn_score += 0.15
        elif ending_variety >= 2: bgn_score += 0.1
        else: improvement.append("종결어미 다양성 부족")

        if any(x in blog_content for x in [":)", "ㅠㅠ", "...", "웃음이", "울컥"]): bgn_score += 0.1
        else: improvement.append("감정 표현 부족")

        if any(x in blog_content for x in ["괜찮", "함께", "옆에 있", "이해", "공감"]): bgn_score += 0.05
        else: improvement.append("공감 표현 부족")

        bgn_phrases = ["저희도 많이 배워요", "특별한 걸 한 건 아니에요", "무리하게 권하지", "편하게 물어보세요"]
        if sum(1 for p in bgn_phrases if p in blog_content) >= 2: bgn_score += 0.1
        else: improvement.append("BGN 특화 표현 부족")

        return {
            "bgn_score": min(bgn_score, 1.0),
            "improvement_suggestions": improvement or ["BGN 톤앤매너가 잘 적용되었습니다"],
            "bgn_elements": bgn_elements,
        }

# 샘플 데이터 (테스트 버튼 용)
def get_sample_materials():
    return {
        "키워드 기반 소재": [
            {
                "title": "BGN 검안사가 본 20대 직장인의 라식 여정 - 안경에서 자유로워지기까지",
                "content": "매일 아침 안경을 찾는 것부터 시작되는 일상, 운동 중 흘러내리는 안경과 마스크 김서림의 불편함까지. 상담 시 자주 안내하는 일반적 배경을 과장 없이 곁들여 자연스럽게 보강합니다.",
                "keywords": ["BGN", "20대", "직장인", "라식", "안경", "불편함", "결심", "일상"],
                "timestamp": "인터뷰 초반 10-15분",
                "usage_point": "검안사 시점 공감대 형성",
                "staff_perspective": "검안사",
                "target_audience": "예비 환자",
            }
        ]
    }
