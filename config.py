# BGN 밝은눈안과 블로그 자동화 시스템 설정 (BGN 톤앤매너 완전 적용)

# Streamlit 앱 설정
APP_CONFIG = {
    "page_title": "BGN 밝은눈안과 블로그 자동화",
    "page_icon": "👁️",
    "layout": "wide",
    "sidebar_state": "expanded",
    "main_title": "👁️ BGN 밝은눈안과(잠실점) 블로그 자동화 시스템",
    "footer_text": "💡 **BGN 밝은눈안과 블로그 자동화 시스템** | BGN 브랜드 톤앤매너 적용 | Made with ❤️"
}

# OpenAI API 설정 (BGN 최적화)
OPENAI_CONFIG = {
    "model": "gpt-4o",  # BGN 톤앤매너 생성에 최적화된 모델
    "temperature": 0.7,  # BGN의 자연스러운 톤 구현
    "analysis_config": {
        "max_tokens": 4000,  # BGN 상세 분석을 위한 확장
        "temperature": 0.3  # BGN 브랜드 일관성을 위한 정확성
    },
    "bgn_blog_config": {
        # BGN 톤앤매너 적용된 옵션들
        "표준 BGN (2,000자)": {"min_chars": 2000, "max_tokens": 3500, "temperature": 0.7},
        "고품질 BGN (2,500자)": {"min_chars": 2500, "max_tokens": 4000, "temperature": 0.7},
        "프리미엄 BGN (3,000자)": {"min_chars": 3000, "max_tokens": 4500, "temperature": 0.7}
    },
    "bgn_image_prompt_config": {
        "max_tokens": 600,  # BGN 브랜드 이미지 설명 확장
        "temperature": 0.5
    }
}

# 파일 업로드 설정
FILE_CONFIG = {
    "allowed_types": ['txt', 'docx', 'pdf', 'hwp'],
    "max_size_mb": 10,
    "upload_help": "BGN 인터뷰 파일 지원 형식: TXT, DOCX, PDF, HWP"
}

# 워드프레스 설정 (BGN 블로그)
WORDPRESS_CONFIG = {
    "default_url": "https://bgnblog.com/",  # BGN 공식 블로그
    "api_endpoint": "/wp-json/wp/v2",
    "bgn_categories": ["BGN 환자후기", "BGN 직원이야기", "BGN 의료정보", "BGN 병원소식"],
    "bgn_tags": "BGN, 밝은눈안과, 잠실점, 안과, 라식, 백내장, 환자중심"
}

# BGN 블로그 작성 설정 (톤앤매너 중심)
BLOG_CONFIG = {
    "bgn_styles": [
        "검안사의 일상 경험담 (친근한 1인칭)",
        "간호사의 따뜻한 케어 스토리",  
        "원무팀의 고객 응대 에피소드",
        "의료진의 전문적이면서도 따뜻한 조언"
    ],
    "bgn_staff_roles": {
        "검안사의 일상 경험담": {
            "role": "검안사",
            "names": ["김서연", "박지혜", "이민정", "최수현"],
            "tone": "전문적이면서도 친근한",
            "specialty": "시력검사, 라식상담, 환자 케어"
        },
        "간호사의 따뜻한 케어": {
            "role": "간호사", 
            "names": ["박지현", "이수민", "김하늘", "정예은"],
            "tone": "따뜻하고 세심한",
            "specialty": "수술 케어, 환자 관리, 회복 지원"
        },
        "원무팀의 고객 응대": {
            "role": "원무팀",
            "names": ["이미소", "김예린", "박소영", "정하연"],
            "tone": "친근하고 신뢰할 수 있는",
            "specialty": "고객 상담, 접수, 일정 관리"
        },
        "의료진의 전문적이면서도": {
            "role": "의료진",
            "names": ["정하늘", "김준석", "이도현", "박서준"],
            "tone": "전문적이지만 따뜻한",
            "specialty": "진료, 수술, 의학적 조언"
        }
    },
    "bgn_lengths": [
        "표준 BGN (2,000자)",
        "고품질 BGN (2,500자)",
        "프리미엄 BGN (3,000자)"
    ],
    "bgn_length_config": {
        "표준 BGN (2,000자)": {
            "min_chars": 2000,
            "target_chars": 2200,
            "description": "BGN 기본 톤앤매너로 2,000자 이상"
        },
        "고품질 BGN (2,500자)": {
            "min_chars": 2500,
            "target_chars": 2700,
            "description": "BGN 고품질 톤앤매너로 2,500자 이상"
        },
        "프리미엄 BGN (3,000자)": {
            "min_chars": 3000,
            "target_chars": 3200,
            "description": "BGN 프리미엄 톤앤매너로 3,000자 이상"
        }
    }
}

# BGN 톤앤매너 설정 (핵심)
BGN_TONE_CONFIG = {
    "brand_identity": {
        "따뜻함": "기계적이지 않은 인간적 케어",
        "전문성": "의학적 정확성과 신뢰성",
        "진솔함": "과장 없는 솔직하고 담담한 소통",
        "접근성": "부담 없이 편하게 다가갈 수 있는 분위기"
    },
    "tone_characteristics": {
        "자연스러운_말투": ["해요", "습니다", "죠", "거든요", "네요", "더라고요", "라고요", "이에요"],
        "감정_표현": [":)", "ㅠㅠ", "...", "웃음이 나왔어요", "울컥했습니다", "마음이 아팠어요"],
        "공감_표현": ["괜찮으세요", "저희가 옆에 있잖아요", "이해해요", "함께 해결해봐요"],
        "겸손_표현": ["저희도 많이 배워요", "특별한 걸 한 건 아니에요", "당연한 일이었어요"],
        "강요없는_조언": ["무리하게 권하지는 않을 거예요", "편하게 물어보세요", "부담없이 연락주세요"]
    },
    "opening_formats": [
        "안녕하세요, **BGN밝은눈안과(잠실점)** {role} **{name}**입니다.",
        "안녕하세요! **BGN밝은눈안과(잠실점)** {role} **{name}**입니다."
    ],
    "closing_formats": [
        "이상으로 **BGN밝은눈안과(잠실점)** {role} **{name}**이었습니다. 오늘도 여러분의 소중한 눈을 생각하며...",
        "이상으로 **BGN밝은눈안과(잠실점)** {role} **{name}**이었습니다. 항상 여러분의 눈 건강을 응원하겠습니다.",
        "이상으로 **BGN밝은눈안과(잠실점)** {role} **{name}**이었습니다. 궁금한 점 있으시면 언제든 연락주세요!"
    ],
    "section_starters": [
        "오늘도 이런 일이 있었어요",
        "사실 저희도 많이 배워요", 
        "그래서 더 세심하게 봐드렸어요",
        "며칠 후에 연락이 왔어요",
        "생각해보니 당연한 일이었어요",
        "비슷한 고민을 하고 계신다면"
    ]
}

# BGN 이미지 생성 설정 (브랜드 맞춤)
IMAGE_CONFIG = {
    "bgn_auto_generation": True,  # BGN 브랜드 자동 생성
    "bgn_base_style": "warm and professional Korean medical photography, BGN brand identity",
    "bgn_default_settings": {
        "quality": "high",
        "lighting": "bright and natural",
        "atmosphere": "clean, modern, and caring BGN medical facility in Jamsil",
        "people": "Korean patients and BGN medical staff",
        "emotion": "warm, trustworthy, and professional interaction"
    },
    "bgn_scene_types": [
        "BGN 의료진과 환자 따뜻한 상담",
        "BGN 안과 검사 장면 (전문적이고 세심한)",
        "BGN 병원 내부 (밝고 깨끗한 분위기)",
        "BGN 치료 과정 (신뢰할 수 있는)",
        "BGN 환자 회복 모습 (희망적이고 밝은)"
    ],
    "bgn_mood_types": [
        "따뜻하고 전문적인 BGN 스타일",
        "신뢰할 수 있고 친근한 BGN 분위기",
        "희망적이고 밝은 BGN 케어 정신"
    ]
}

# BGN 콘텐츠 분석 방식 설정
ANALYSIS_CONFIG = {
    "bgn_default_method": "bgn_keyword_based",  # BGN 맞춤 키워드 분석
    "methods": {
        "bgn_keyword_based": {
            "name": "BGN 브랜드 키워드 분석",
            "description": "BGN 브랜드 정체성에 맞는 키워드와 톤앤매너 소재 발굴",
            "icon": "🏥"
        },
        "bgn_category_based": {
            "name": "BGN 직무별 카테고리 분석", 
            "description": "BGN 직무(검안사, 간호사, 원무팀)별 관점 분류",
            "icon": "👥"
        }
    },
    "bgn_text_length_threshold": 15000,
    "bgn_chunk_size": 6000,
    "bgn_max_analysis_attempts": 3
}

# BGN 콘텐츠 소재 유형 (브랜드 맞춤)
BGN_CONTENT_TYPES = {
    "BGN 환자 에피소드형": {
        "description": "BGN에서 실제 경험한 환자 치료 경험담, BGN만의 특별한 케이스",
        "icon": "👥",
        "staff_perspective": ["검안사", "간호사", "의료진"],
        "tone": "따뜻한 공감과 전문성"
    },
    "BGN 검사·과정형": {
        "description": "BGN의 검사 방법, 치료 과정, 의료 절차를 환자 시선에서 설명", 
        "icon": "🔍",
        "staff_perspective": ["검안사", "의료진"],
        "tone": "전문적이면서도 이해하기 쉬운"
    },
    "BGN 센터 운영/분위기형": {
        "description": "BGN 병원 문화, 직원 이야기, 잠실점 시설과 서비스 소개",
        "icon": "🏥",
        "staff_perspective": ["원무팀", "간호사", "모든 직원"],
        "tone": "자연스럽고 친근한"
    },
    "BGN 직원 성장기형": {
        "description": "BGN 직원의 실수·배움 중심 성장 스토리, 팀워크와 멘토링",
        "icon": "🌱",
        "staff_perspective": ["신입직원", "모든 직원"],
        "tone": "진솔하고 격려하는"
    },
    "BGN 환자 질문 FAQ형": {
        "description": "BGN 상담 시 자주 나오는 질문과 BGN만의 친근한 답변",
        "icon": "❓",
        "staff_perspective": ["원무팀", "검안사", "간호사"],
        "tone": "친근하고 이해하기 쉬운"
    }
}

# BGN 키워드 분류 템플릿 (브랜드 특화)
BGN_KEYWORD_CATEGORIES = {
    "BGN_환자_관련": ["나이", "성별", "증상", "감정", "직업", "생활패턴", "불안감", "만족도"],
    "BGN_의료진_관련": ["경험", "전문성", "소통", "성장", "케어", "팀워크", "멘토링"],
    "BGN_병원_운영": ["잠실점", "시설", "서비스", "시스템", "문화", "환경", "접근성"],
    "BGN_치료_과정": ["검사", "진단", "라식", "백내장", "회복", "사후관리", "결과"],
    "BGN_감정_경험": ["불안", "기대", "만족", "감사", "신뢰", "안도", "감동", "위로"],
    "BGN_기술_장비": ["최신기술", "정밀장비", "정확도", "안전성", "효과", "차별화"],
    "BGN_브랜드_가치": ["따뜻함", "전문성", "신뢰", "케어", "소통", "공감", "진솔함"]
}

# 단계 정보 (BGN 브랜드 반영)
STEP_INFO = [
    "1️⃣ BGN 인터뷰 업로드",
    "2️⃣ BGN 브랜드 소재 도출", 
    "3️⃣ BGN 톤앤매너 블로그 작성",
    "4️⃣ BGN 브랜드 이미지 생성",
    "5️⃣ BGN 블로그 발행"
]

# BGN 품질 검증 설정 (톤앤매너 중심)
BGN_QUALITY_CONFIG = {
    "bgn_min_char_counts": {
        "표준 BGN (2,000자)": 2000,
        "고품질 BGN (2,500자)": 2500, 
        "프리미엄 BGN (3,000자)": 3000
    },
    "bgn_forbidden_phrases": [
        "일반적으로", "보통", "대부분", "많은 환자들이", "흔히", "대개", "통상적으로"
    ],
    "bgn_required_elements": {
        "bgn_brand_intro": True,  # BGN 시작 멘트
        "bgn_brand_outro": True,  # BGN 종료 멘트
        "staff_perspective": True,  # 직원 관점
        "natural_tone": True,  # 자연스러운 톤
        "emotion_expression": True,  # 감정 표현
        "empathy_tone": True,  # 공감 표현
        "concrete_examples": True,  # 구체적 사례
        "professional_info": True  # 전문 정보
    },
    "bgn_tone_indicators": {
        "ending_variety": ["해요", "습니다", "죠", "거든요", "더라고요", "라고요", "네요"],
        "emotion_words": [":)", "ㅠㅠ", "...", "웃음이", "울컥", "마음이"],
        "empathy_words": ["괜찮", "함께", "옆에 있", "이해", "공감"],
        "humble_words": ["배워요", "특별한 건 아니", "당연한"],
        "gentle_words": ["편하게", "부담없이", "언제든", "궁금하면"]
    },
    "bgn_image_requirements": {
        "korean_people": True,
        "bgn_medical_setting": True,
        "warm_professional_atmosphere": True,
        "brand_consistency": True
    }
}

# 에러 처리 설정 (BGN 맞춤)
ERROR_CONFIG = {
    "max_retries": 3,
    "fallback_to_bgn_sample": True,
    "timeout_seconds": 30,
    "bgn_error_messages": {
        "api_key_missing": "BGN 블로그 생성을 위해 OpenAI API 키가 필요합니다.",
        "content_too_long": "인터뷰 텍스트가 너무 깁니다. BGN 요약 후 분석을 진행합니다.",
        "analysis_failed": "BGN 브랜드 분석에 실패했습니다. BGN 샘플 데이터로 진행합니다.",
        "generation_failed": "BGN 톤앤매너 블로그 생성에 실패했습니다. 다시 시도해주세요.",
        "tone_mismatch": "BGN 톤앤매너가 일치하지 않습니다. 재생성을 권장합니다."
    }
}

# BGN 밝은눈안과(잠실점) 정보
BGN_HOSPITAL_INFO = {
    "name": "BGN 밝은눈안과",
    "branch": "잠실점",
    "full_name": "BGN 밝은눈안과(잠실점)",
    "phone": "02-1234-5678",
    "website": "www.brighteye.co.kr",
    "blog_url": "https://bgnblog.com/",
    "address": "서울시 송파구 잠실동 BGN빌딩 3층",
    "location_landmark": "잠실역 2번 출구 도보 3분",
    "hours": "평일 09:00~18:00, 토요일 09:00~13:00",
    "specialties": ["라식", "라섹", "백내장", "안구건조증", "망막질환", "소아안과"],
    "brand_values": ["환자 중심", "따뜻한 케어", "전문적 진료", "신뢰할 수 있는 의료"],
    "staff_count": {
        "의료진": 4,
        "검안사": 6, 
        "간호사": 8,
        "원무팀": 4
    }
}

# BGN 톤앤매너 체크리스트
BGN_TONE_CHECKLIST = {
    "필수_요소": [
        "BGN밝은눈안과(잠실점) 시작 멘트",
        "직원 이름과 직무 명시",
        "1인칭 실무자 시점",
        "다양한 종결어미 사용",
        "자연스러운 감정 표현",
        "BGN밝은눈안과(잠실점) 종료 멘트"
    ],
    "권장_요소": [
        "일상 에피소드 시작",
        "환자와의 구체적 대화",
        "의료진의 겸손한 자세",
        "강요 없는 조언",
        "따뜻한 공감 표현",
        "전문성과 친근함의 균형"
    ],
    "금지_요소": [
        "과도한 영업성 멘트",
        "일반적이고 모호한 표현",
        "단조로운 종결어미 반복",
        "형식적인 구조적 제목",
        "BGN 브랜드와 맞지 않는 톤"
    ]
}


# 기존 코드 호환성을 위한 변수들 (BGN 설정을 기본값으로 사용)
CONTENT_TYPES = BGN_CONTENT_TYPES
QUALITY_CONFIG = BGN_QUALITY_CONFIG

# 기존 블로그 설정 호환성
BLOG_CONFIG.update({
    "styles": BLOG_CONFIG["bgn_styles"],
    "lengths": BLOG_CONFIG["bgn_lengths"]
})