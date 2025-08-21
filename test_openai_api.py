import os
from openai import OpenAI

def test_openai_connection():
    """OpenAI API 연결 테스트 (환경변수 사용)"""
    
    # 환경변수에서 API 키 가져오기
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print('❌ OPENAI_API_KEY 환경변수가 설정되지 않았습니다.')
        print('다음 명령어로 설정하세요:')
        print('PowerShell: $env:OPENAI_API_KEY = "your_api_key_here"')
        return False
    
    try:
        client = OpenAI(api_key=api_key)
        
        # 간단한 테스트 요청
        response = client.chat.completions.create(
            model='gpt-3.5-turbo',
            messages=[{'role': 'user', 'content': 'Hello!'}],
            max_tokens=10
        )
        
        print('✅ OpenAI API 연결 성공!')
        print(f'응답: {response.choices[0].message.content}')
        return True
        
    except Exception as e:
        print(f'❌ API 연결 실패: {e}')
        return False

if __name__ == '__main__':
    test_openai_connection()
