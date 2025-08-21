#!/bin/bash

# Python 의존성 설치
pip install -r requirements.txt

# Streamlit 설정 파일 생성
mkdir -p ~/.streamlit
echo "[server]
headless = true
port = 8501
enableCORS = false
enableXsrfProtection = false

[theme]
primaryColor = '#4CAF50'
backgroundColor = '#FFFFFF'
secondaryBackgroundColor = '#F0F2F6'
textColor = '#262730'

[browser]
gatherUsageStats = false
" > ~/.streamlit/config.toml