# utils/ai_analyzer.py
import json
import streamlit as st
from openai import OpenAI
from config import OPENAI_CONFIG, CONTENT_TYPES, QUALITY_CONFIG, FILE_CONFIG


class AIAnalyzer:
    def __init__(self, api_key: str | None = None):
        api_key = api_key or OPENAI_CONFIG.get("api_key")
        self.client = OpenAI(api_key=api_key)
        self.config = OPENAI_CONFIG

    # ===================== 인터뷰 → 소재 도출 =====================
    def analyze_interview_content_keyword_based(self, content: str):
        """인터뷰 전문에서 BGN 톤의 블로그 소재를 도출하고 탭 키에 맞게 분류."""
        content = content or ""
        max_len = FILE_CONFIG.get("max_chars_for_analysis", 15000)
        if len(content) > max_len:
            st.warning(f"📏 텍스트가 {len(content):,}자입니다. 앞 {max_len:,}자만 분석합니다.")
            content = content[:max_len]

        try:
            payload = self._analyze_keywords_for_bgn(content)
        except Exception as e:
            st.warning(f"분석 실패 → 샘플로 대체: {e}")
            payload = self._get_bgn_keyword_fallback_materials()

        validated = self._validate_bgn_keyword_materials(payload)
        categorized = self._categorize_bgn_materials(validated.get("키워드 기반 소재", []))

        # 모든 탭이 비었으면 샘플로 채움
        if not any(categorized.get(k) for k in CONTENT_TYPES):
            fb = self._get_bgn_keyword_fallback_materials()["키워드 기반 소재"]
            categorized = self._categorize_bgn_materials(fb)

        st.success("✅ BGN 키워드 분석 완료")
        return categorized

    def _analyze_keywords_for_bgn(self, content: str) -> dict:
        """모델 호출: 인터뷰 ‘근거 문장’을 포함하도록 강제 + 공신력 있는 일반설명 보강 허용(과장/후기 금지)"""
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
      "content": "인터뷰에서 실제 언급된 구체 내용(≥120자). 독자 이해를 돕는 공신력 있는 일반 의학 설명 보강 허용(과장/후기/효능단정 금지).",
      "keywords": ["BGN","관련 키워드", "6~8개"],
      "timestamp": "인터뷰 구간(있다면)",
      "usage_point": "2000자 이상 블로그 전개 포인트",
      "staff_perspective": "검안사/간호사/원무팀/의료진",
      "target_audience": "예비 환자/기존 환자/일반인",
      "direct_quote": "직접 인용(있다면)",
      "source_quote": "인터뷰 본문에서 해당 소재를 뒷받침하는 문장(필수)",
      "evidence_span": [시작_문자_인덱스, 끝_문자_인덱스], 
      "bgn_brand_fit": "따뜻함/전문성/신뢰 연결",
      "emotion_tone": "감정 톤"
    }}
  ]
}}

[중요 지침]
- 최소 6개 이상, 주제/관점이 서로 다른 소재.
- 인터뷰 '내용' 중심 + 공신력 있는 일반 의학 설명 보강(새로운 환자/사례 창작 금지).
- 각 아이템은 반드시 `source_quote`를 포함하고, 그 문장이 `content` 안에 그대로 들어가야 하며,
  `evidence_span`이 content 내 인덱스와 일치해야 함.
- 반드시 JSON만 출력.
"""
        resp = self.client.chat.completions.create(
            model=self.config["model"],
            messages=[
                {"role": "system", "content": "BGN 콘텐츠 기획자. 반드시 JSON만 출력."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=4000,
        )
        txt = (resp.choices[0].message.content or "").strip()
        start, end = txt.find("{"), txt.rfind("}") + 1
        if start < 0 or end <= start:
            raise json.JSONDecodeError("JSON 파싱 실패", txt, 0)
        return json.loads(txt[start:end])

    def _validate_bgn_keyword_materials(self, materials: dict) -> dict:
        """필수 필드/길이/키워드 수 + 근거 문장 포함/인덱스 일치 여부 검증."""
        out = {"키워드 기반 소재": []}
        items = (materials or {}).get("키워드 기반 소재", [])
        for it in items:
            req = ["title", "content", "keywords", "usage_point", "staff_perspective", "source_quote", "evidence_span"]
            if not all(k in it for k in req):
                continue
            c = it.get("content", "")
            q = it.get("source_quote", "")
            span = it.get("evidence_span", [])
            if len(c) < 120 or len(it.get("keywords", [])) < 4:
                continue
            if q not in c:
                continue
            if (not isinstance(span, list)) or len(span) != 2:
                continue
            s, e = span
            if not (isinstance(s, int) and isinstance(e, int)):  # 숫자형 보장
                continue
            if not (0 <= s < e <= len(c)):
                continue
            if c[s:e] != q:
                continue
            out["키워드 기반 소재"].append(it)

        if len(out["키워드 기반 소재"]) < 4:
            st.warning("⚠️ 유효 소재 부족 → 샘플 보강")
            out = self._get_bgn_keyword_fallback_materials()
        return out

    def _categorize_bgn_materials(self, items: list) -> dict:
        """UI 탭 구조와 동일한 키로 분류."""
        out = {k: [] for k in CONTENT_TYPES}

        def put(cat, it):
            out[cat].append(it)

        for it in items:
            text = f"{it.get('title','')} {it.get('content','')} {', '.join(it.get('keywords', []))}".lower()
            role = (it.get("staff_perspective") or "").lower()
            audience = (it.get("target_audience") or "")

            if any(k in text for k in ["수술", "회복", "후기", "변화", "감동", "울컥"]) or "예비 환자" in audience:
                put("BGN 환자 에피소드형", it); continue
            if any(k in text for k in ["검사", "장비", "과정", "측정", "결과", "프로세스", "진단"]):
                put("BGN 검사·과정형", it); continue
            if any(k in text for k in ["운영", "분위기", "대기시간", "예약", "서비스", "시스템", "원무"]) or "원무" in role:
                put("BGN 센터 운영/분위기형", it); continue
            if any(k in text for k in ["신입", "멘토", "멘토링", "교육", "배움", "첫 수술", "성장"]) or "신입" in role:
                put("BGN 직원 성장기형", it); continue
            if any(k in text for k in ["질문", "언제", "가능", "방법", "주의", "faq", "자주 묻는"]):
                put("BGN 환자 질문 FAQ형", it); continue

            put("BGN 환자 에피소드형", it)  # 기본 라우팅
        return out

    # ----- 옛 API 호환 (기존 코드가 이 이름을 호출) -----
    def analyze_interview_content(self, content: str):
        return self.analyze_interview_content_keyword_based(content)

    # ===================== 블로그 초안 생성 =====================
    def _infer_role_name_from_filename(self, filename: str):
        """
        예) '검안사_김서연_인터뷰.txt' → ('검안사','김서연')
        실패 시 (None, None)
        """
        try:
            base = filename.rsplit("/", 1)[-1].rsplit("\\", 1)[-1]
            stem = base.rsplit(".", 1)[0]
            parts = [p for p in stem.replace("-", "_").split("_") if p]
            if len(parts) >= 2:
                return parts[0], parts[1]
        except Exception:
            pass
        return None, None

    def generate_blog_content_bgn_style(
        self,
        selected_material: dict,
        style: str,
        length: str,
        additional_request: str,
        bgn_style_params: dict,
        *,
        source_filename: str | None = None,
        temperature: float = 0.9,
        top_p: float = 0.9,
    ):
        material = selected_material["data"]

        # 기본값
        staff_role = bgn_style_params.get("staff_role", "검안사")
        staff_name = bgn_style_params.get("staff_name", "김서연")

        # 파일명에서 추론되면 우선 적용
        if source_filename:
            r, n = self._infer_role_name_from_filename(source_filename)
            if r: staff_role = r
            if n: staff_name = n

        cfg = QUALITY_CONFIG.get(length, QUALITY_CONFIG["표준 BGN (2,000자)"])

        # 입력 길이 제한
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
        return draft

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

요청: H2/H3 헤딩 구조의 JSON 아웃라인만 출력.
필드: title, h2_sections[{{"h2": str, "bullets": [str], "h3": [str]}}]
"""
        res = self.client.chat.completions.create(
            model=self.config["model"],
            messages=[
                {"role": "system", "content": "간결한 편집자. JSON만 출력."},
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

규칙:
- 시작 멘트: "안녕하세요, BGN밝은눈안과(잠실점) {staff_role} {staff_name}입니다."
- 1인칭 시점 유지, 과장/권유 금지, 자연스러운 구어체 허용
- 목표 분량: 약 {target_chars}자
- H2/H3 구조 유지
- 후기형 과장 문구 금지
- 인터뷰 실제 언급 내용을 중심으로 하되,
  독자 이해를 돕는 공신력 있는 일반 의학 배경설명은 보강 가능(효능 단정/후기 금지)

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


# 샘플(테스트용)
def get_sample_materials():
    return {
        "키워드 기반 소재": [
            {
                "title": "BGN 검안사가 본 20대 직장인의 라식 여정 - 안경에서 자유로워지기까지",
                "content": "매일 아침 안경을 찾는 일상, 운동 중 흘러내리는 안경, 마스크 김서림의 불편함. 상담 중 자주 안내하는 일반적 배경을 과장 없이 덧붙입니다.",
                "keywords": ["BGN", "20대", "직장인", "라식", "안경", "불편함", "결심", "일상"],
                "timestamp": "초반 10-15분",
                "usage_point": "검안사 시점 공감대 형성",
                "staff_perspective": "검안사",
                "target_audience": "예비 환자",
                "source_quote": "마스크 때문에 안경 김이 서려서 너무 불편했어요.",
                "evidence_span": [0, 20],
            }
        ]
    }
