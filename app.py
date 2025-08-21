#!/usr/bin/env python3
"""
Vercel용 BGN 밝은눈안과 블로그 자동화 시스템 진입점
"""

import sys
import os
from pathlib import Path

# 현재 디렉토리를 Python 경로에 추가
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Streamlit 실행
if __name__ == "__main__":
    import streamlit.web.cli as stcli
    import streamlit.web.bootstrap as bootstrap
    
    # main.py 실행
    main_script = str(current_dir / "main.py")
    
    # Streamlit 서버 설정
    os.environ["STREAMLIT_SERVER_HEADLESS"] = "true"
    os.environ["STREAMLIT_SERVER_PORT"] = "8501"
    os.environ["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"
    
    # Streamlit 앱 실행
    sys.argv = ["streamlit", "run", main_script, "--server.port=8501", "--server.headless=true"]
    stcli.main()