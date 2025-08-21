# components/wordpress_publisher.py
import streamlit as st
import requests

# 안전 import: 설정 누락시 기본값
try:
    from config import WORDPRESS_CONFIG
except Exception:
    WORDPRESS_CONFIG = {
        "endpoint": "",
        "username": "",
        "application_password": "",
        "default_status": "draft",
        "default_categories": ["BGN 블로그"],
        "default_tags": [],
    }


def display_final_review():
    st.subheader("최종 점검")
    draft = st.session_state.get("blog_draft", "")
    if not draft:
        st.info("③에서 블로그 초안을 생성해 주세요.")
        return
    st.text_area("블로그 초안", draft, height=400)


def configure_publish_settings():
    st.subheader("발행 설정")
    # KeyError 방지: get() + 기본값
    cats = WORDPRESS_CONFIG.get("default_categories", ["BGN 블로그"])
    st.session_state.category = st.selectbox("카테고리", cats, key="category_select")

    tags_default = WORDPRESS_CONFIG.get("default_tags", [])
    tags_text = st.text_input("태그(쉼표 구분)", ",".join(tags_default))
    st.session_state.tags = [t.strip() for t in tags_text.split(",") if t.strip()]


def configure_wordpress_settings():
    st.subheader("워드프레스 연동")
    st.write("환경변수 또는 설정파일의 값을 사용합니다.")
    st.json(
        {
            "endpoint": WORDPRESS_CONFIG.get("endpoint", ""),
            "username": WORDPRESS_CONFIG.get("username", ""),
            "status": WORDPRESS_CONFIG.get("default_status", "draft"),
        }
    )


def publish_to_wordpress(title: str, content: str, categories: list[str], tags: list[str]):
    endpoint = (WORDPRESS_CONFIG.get("endpoint") or "").rstrip("/")
    if not endpoint:
        raise ValueError("WORDPRESS_CONFIG.endpoint가 비어 있습니다. config.py를 확인하세요.")

    # WP REST: /wp-json/wp/v2/posts
    url = f"{endpoint}/posts"
    auth = (
        WORDPRESS_CONFIG.get("username", ""),
        WORDPRESS_CONFIG.get("application_password", ""),
    )
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

    # 1) 리뷰
    display_final_review()

    # 2) 발행 설정
    configure_publish_settings()

    # 3) 워드프레스 설정 표시
    configure_wordpress_settings()

    # 4) 발행
    title = st.text_input("게시물 제목", st.session_state.get("blog_title", "BGN 블로그"))
    if st.button("워드프레스 발행", type="primary"):
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
