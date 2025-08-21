# components/wordpress_publisher.py
import streamlit as st
import requests
from config import WORDPRESS_CONFIG

def display_final_review():
    st.subheader("최종 점검")
    draft = st.session_state.get("blog_draft", "")
    if not draft:
        st.info("③에서 블로그 초안을 생성해 주세요.")
        return
    st.text_area("블로그 초안", draft, height=400)

def configure_publish_settings():
    st.subheader("발행 설정")
    cats = WORDPRESS_CONFIG.get("default_categories", ["BGN 블로그"])
    st.session_state.category = st.selectbox("카테고리", cats, key="category_select")

    tags_default = WORDPRESS_CONFIG.get("default_tags", [])
    tags_text = st.text_input("태그(쉼표로 구분)", ",".join(tags_default))
    st.session_state.tags = [t.strip() for t in tags_text.split(",") if t.strip()]

def configure_wordpress_settings():
    st.subheader("워드프레스 연동")
    st.write("환경변수 또는 설정파일의 값을 사용합니다.")
    st.json({
        "endpoint": WORDPRESS_CONFIG.get("endpoint", ""),
        "username": WORDPRESS_CONFIG.get("username", ""),
        "status": WORDPRESS_CONFIG.get("default_status", "draft"),
    })

def publish_to_wordpress(title: str, content: str, categories: list[str], tags: list[str]):
    endpoint = WORDPRESS_CONFIG.get("endpoint", "").rstrip("/")
    if not endpoint:
        raise ValueError("WORDPRESS_CONFIG.endpoint가 비어 있습니다.")

    url = f"{endpoint}/posts"
    auth = (WORDPRESS_CONFIG.get("username", ""), WORDPRESS_CONFIG.get("application_password", ""))
    status = WORDPRESS_CONFIG.get("default_status", "draft")

    payload = {
        "title": title,
        "content": content,
        "status": status,
        "categories": categories or WORDPRESS_CONFIG.get("default_categories", ["BGN 블로그"]),
        "tags": tags or WORDPRESS_CONFIG.get("default_tags", []),
    }
    r = requests.post(url, auth=auth, json=payload, timeout=30)
    r.raise_for_status()
    return r.json()

def render_wordpress_publisher_page():
    st.header("⑤ 워드프레스 발행")

    display_final_review()
    configure_publish_settings()
    configure_wordpress_settings()

    title = st.text_input("게시물 제목", st.session_state.get("blog_title", "BGN 블로그"))
    if st.button("워드프레스 발행"):
        try:
            res = publish_to_wordpress(
                title=title,
                content=st.session_state.get("blog_draft", ""),
                categories=[st.session_state.get("category")],
                tags=st.session_state.get("tags", []),
            )
            st.success("발행(또는 초안 저장) 완료!")
            st.json(res)
        except Exception as e:
            st.error(f"발행 중 오류: {e}")
