import streamlit as st
import hashlib
import os
from datetime import datetime, timedelta

class AuthManager:
    def __init__(self):
        # 환경변수에서 관리자 계정 정보 로드
        self.admin_users = self._load_admin_users()
        
    def _load_admin_users(self):
        """환경변수에서 관리자 계정 정보 로드"""
        # 기본 관리자 계정 (환경변수에서 설정)
        admin_username = os.getenv('ADMIN_USERNAME', 'admin')
        admin_password = os.getenv('ADMIN_PASSWORD', 'bgn2024!')
        
        # 추가 직원 계정들 (환경변수에서 설정)
        staff_accounts = os.getenv('STAFF_ACCOUNTS', '')
        
        users = {
            admin_username: self._hash_password(admin_password)
        }
        
        # 직원 계정 파싱 (username:password,username:password 형식)
        if staff_accounts:
            for account in staff_accounts.split(','):
                if ':' in account:
                    username, password = account.strip().split(':')
                    users[username] = self._hash_password(password)
        
        return users
    
    def _hash_password(self, password):
        """비밀번호 해시화"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def authenticate(self, username, password):
        """사용자 인증"""
        hashed_password = self._hash_password(password)
        return username in self.admin_users and self.admin_users[username] == hashed_password
    
    def login(self):
        """로그인 페이지 렌더링"""
        if self.is_authenticated():
            return True
        
        st.markdown("""
        <div style="text-align: center; padding: 2rem;">
            <h1>👁️ BGN 밝은눈안과</h1>
            <h2>블로그 자동화 시스템</h2>
            <p style="color: #666;">직원 전용 시스템입니다. 로그인하여 접속하세요.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 로그인 폼
        with st.container():
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col2:
                with st.form("login_form"):
                    st.markdown("### 🔐 로그인")
                    
                    username = st.text_input("사용자명", placeholder="사용자명을 입력하세요")
                    password = st.text_input("비밀번호", type="password", placeholder="비밀번호를 입력하세요")
                    
                    submitted = st.form_submit_button("로그인", use_container_width=True, type="primary")
                    
                    if submitted:
                        if username and password:
                            if self.authenticate(username, password):
                                st.session_state.authenticated = True
                                st.session_state.username = username
                                st.session_state.login_time = datetime.now()
                                st.success("✅ 로그인 성공!")
                                st.rerun()
                            else:
                                st.error("❌ 사용자명 또는 비밀번호가 올바르지 않습니다.")
                        else:
                            st.warning("⚠️ 사용자명과 비밀번호를 모두 입력해주세요.")
        
        
        return False
    
    def is_authenticated(self):
        """인증 상태 확인"""
        if not hasattr(st.session_state, 'authenticated'):
            return False
        
        if not st.session_state.authenticated:
            return False
        
        # 세션 만료 확인 (24시간)
        if hasattr(st.session_state, 'login_time'):
            if datetime.now() - st.session_state.login_time > timedelta(hours=24):
                self.logout()
                return False
        
        return True
    
    def logout(self):
        """로그아웃"""
        st.session_state.authenticated = False
        if hasattr(st.session_state, 'username'):
            del st.session_state.username
        if hasattr(st.session_state, 'login_time'):
            del st.session_state.login_time
        st.rerun()
    
    def get_current_user(self):
        """현재 로그인한 사용자 정보"""
        if self.is_authenticated():
            return st.session_state.get('username', 'Unknown')
        return None
    
    def render_user_info(self):
        """사용자 정보 표시 (사이드바용)"""
        if self.is_authenticated():
            username = self.get_current_user()
            with st.sidebar:
                st.markdown("---")
                st.markdown(f"**👤 로그인 사용자**: {username}")
                
                login_time = st.session_state.get('login_time')
                if login_time:
                    time_diff = datetime.now() - login_time
                    hours = int(time_diff.total_seconds() // 3600)
                    minutes = int((time_diff.total_seconds() % 3600) // 60)
                    st.markdown(f"**⏰ 접속 시간**: {hours}시간 {minutes}분")
                
                if st.button("🚪 로그아웃", use_container_width=True):
                    self.logout()

# 전역 인증 관리자 인스턴스
auth_manager = AuthManager()