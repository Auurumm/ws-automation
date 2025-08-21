# components/image_generator.py
import streamlit as st
import hashlib
import random
from openai import OpenAI
from config import OPENAI_CONFIG, IMAGE_CONFIG

BASE_MODS = [
    "documentary clinical close-up, natural lighting",
    "editorial style, clean background, soft shadows",
    "isometric vector illustration, flat design, labels",
    "infographic style, minimal icons, high contrast"
]
COMPOSITION = [
    "centered composition",
    "rule of thirds",
    "45-degree angle",
    "top-down view"
]

def _unique_key(s: str):
    return hashlib.sha1(s.encode("utf-8")).hexdigest()

def _gen_variants(client: OpenAI, base_prompt: str, n: int):
    used = set()
    results = []
    tries = n * 3  # 여유 시도
    for _ in range(tries):
        style = random.choice(BASE_MODS)
        comp  = random.choice(COMPOSITION)
        seed  = random.randint(1, 2_000_000) if IMAGE_CONFIG.get("allow_seed", True) else None
        full_prompt = f"{base_prompt} | {style} | {comp}"

        resp = client.images.generate(
            model="gpt-image-1",
            prompt=full_prompt,
            size=IMAGE_CONFIG.get("size", "1024x1024"),
            **({"seed": seed} if seed is not None else {})
        )
        url = resp.data[0].url
        key = _unique_key(url)
        if key in used:
            continue
        used.add(key)
        results.append({"url": url, "prompt": full_prompt, "seed": seed})
        if len(results) >= n:
            break
    return results

def render_image_generator_page():
    st.header("④ 이미지 생성")
    client = OpenAI(api_key=OPENAI_CONFIG.get("api_key"))

    base_prompt = st.text_area("기본 프롬프트", placeholder="예: 안구건조증 검사 과정 인포그래픽, ...")
    n = st.slider("생성 개수", 1, 8, IMAGE_CONFIG.get("n", 4))
    if st.button("이미지 생성", type="primary"):
        with st.spinner("이미지 생성 중..."):
            variants = _gen_variants(client, base_prompt, n)
            if not variants:
                st.error("이미지 생성에 실패했습니다.")
            else:
                st.session_state["image_variants"] = variants
                st.success("이미지 생성 완료!")

    variants = st.session_state.get("image_variants", [])
    if variants:
        st.markdown("#### 결과")
        cols = st.columns(min(4, len(variants)))
        for i, v in enumerate(variants):
            with cols[i % len(cols)]:
                st.image(v["url"], use_container_width=True)
                st.caption(f"seed: {v.get('seed')}") 
                st.code(v["prompt"])
