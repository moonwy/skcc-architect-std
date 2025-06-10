# 🔍 AI 코드 리뷰 & 최적화 Agent

실무에서 활용 가능한 AI 기반 코드 리뷰 및 최적화 시스템입니다. LangChain, LangGraph, RAG를 활용한 Multi-Agent 아키텍처로 구현되었습니다.

## 🎯 주요 기능

### 🤖 Multi-Agent 코드 리뷰 시스템
- **분석 Agent**: 코드 구조 및 언어 감지
- **품질 검사 Agent**: 코드 품질 및 가독성 분석  
- **보안 검토 Agent**: 보안 취약점 검사
- **성능 최적화 Agent**: 성능 개선 방안 제시
- **문서화 Agent**: 문서화 상태 분석
- **최종 검토 Agent**: 종합적인 리뷰 및 추천사항 제공

### 📚 RAG 기반 지식베이스
- 코딩 베스트 프랙티스 데이터베이스
- 언어별 특화 가이드라인
- 보안, 성능, 품질 관련 지식
- 사용자 정의 규칙 추가 가능

### 🌐 지원 언어
- Python
- JavaScript/TypeScript
- Java
- C/C++
- C#, Go, Rust, PHP, Ruby, Swift, Kotlin

### 🎨 사용자 인터페이스
- Streamlit 기반 웹 인터페이스
- 실시간 코드 분석 및 결과 시각화
- 리뷰 히스토리 관리
- 대화형 지식베이스 검색

## 🏗️ 시스템 아키텍처

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Streamlit UI  │────│  Multi-Agent     │────│  RAG System     │
│                 │    │  Orchestrator    │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                        │
                       ┌────────┴────────┐              │
                       │   LangGraph     │              │
                       │   Workflow      │              │
                       └─────────────────┘              │
                                │                        │
                    ┌───────────┼───────────┐           │
                    │           │           │           │
            ┌───────▼───┐ ┌─────▼─────┐ ┌──▼────┐     │
            │ Analyzer  │ │ Quality   │ │ Security│     │
            │ Agent     │ │ Agent     │ │ Agent   │     │
            └───────────┘ └───────────┘ └─────────┘     │
                                                        │
                    ┌───────────┼───────────┐           │
                    │           │           │           │
            ┌───────▼───┐ ┌─────▼─────┐ ┌──▼────┐     │
            │Performance│ │Documentation│ │ Final │     │
            │ Agent     │ │ Agent     │ │ Agent │     │
            └───────────┘ └───────────┘ └─────────┘     │
                                                        │
                                              ┌─────────▼─────────┐
                                              │   FAISS Vector    │
                                              │   Database        │
                                              └───────────────────┘
```

## 🚀 설치 및 실행

### 1. 환경 설정

```bash
# 저장소 클론
git clone <repository-url>
cd ai-code-review-agent

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 패키지 설치
pip install -r requirements.txt
```

### 2. 환경변수 설정

`.env` 파일을 생성하고 다음 정보를 입력하세요:

```env
# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY=your_azure_openai_api_key
AZURE_OPENAI_ENDPOINT=your_azure_openai_endpoint
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=your_embedding_deployment

# 또는 OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key
```

### 3. 애플리케이션 실행

```bash
streamlit run app.py
```

브라우저에서 `http://localhost:8501`로 접속하세요.

## 📖 사용법

### 1. 코드 리뷰
1. 메인 페이지의 "코드 리뷰" 탭에서 분석할 코드를 입력
2. 파일명을 입력하면 더 정확한 언어 감지 가능
3. "코드 리뷰 시작" 버튼 클릭
4. Multi-Agent가 순차적으로 코드를 분석
5. 결과를 카테고리별로 확인

### 2. 지식베이스 활용
1. "지식베이스" 탭에서 베스트 프랙티스 검색
2. 사용자 정의 규칙 추가 가능
3. 팀별 코딩 표준 관리

### 3. 결과 해석
- **전체 점수**: 1-10점 (높을수록 좋음)
- **이슈 심각도**: Critical > Warning > Info
- **추천사항**: RAG 시스템 기반 맞춤형 제안

## 🔧 기술 스택

### Core Technologies
- **LangChain**: LLM 통합 및 체인 구성
- **LangGraph**: Multi-Agent 워크플로우 관리
- **Streamlit**: 웹 인터페이스
- **FAISS**: 벡터 데이터베이스
- **Azure OpenAI/OpenAI**: 언어 모델

### Analysis & Visualization
- **AST (Abstract Syntax Tree)**: Python 코드 분석
- **Plotly**: 데이터 시각화
- **Pandas**: 데이터 처리

### Development Tools
- **Python 3.8+**
- **dotenv**: 환경변수 관리
- **logging**: 로깅 시스템

## 📁 프로젝트 구조

```
ai-code-review-agent/
├── app.py                      # Streamlit 메인 애플리케이션
├── config.py                   # 설정 관리
├── requirements.txt            # 패키지 의존성
├── README.md                   # 프로젝트 문서
├── agents/
│   └── code_review_agents.py   # Multi-Agent 시스템
├── utils/
│   ├── llm_manager.py         # LLM 연결 관리
│   ├── code_analyzer.py       # 코드 분석 유틸리티
│   └── rag_system.py          # RAG 시스템
└── data/
    ├── vector_db/             # FAISS 벡터 데이터베이스
    └── knowledge_base/        # 지식베이스 파일
```

## 🎨 주요 특징

### 1. Prompt Engineering
- 역할 기반 프롬프트 설계
- Chain-of-Thought 추론
- 언어별 특화 프롬프트

### 2. Multi-Agent Architecture
- LangGraph 기반 워크플로우
- 각 Agent의 전문화된 역할
- 순차적 분석 프로세스

### 3. RAG 시스템
- 코딩 베스트 프랙티스 지식베이스
- 의미 기반 검색
- 동적 지식 확장

### 4. 사용자 경험
- 직관적인 웹 인터페이스
- 실시간 분석 결과
- 시각적 데이터 표현

## 🔒 보안 고려사항

- 환경변수를 통한 API 키 관리
- 코드 데이터 프라이버시 보호
- 안전한 파일 처리

## 🚀 확장 가능성

### 추가 가능한 기능
- **CI/CD 통합**: GitHub Actions, Jenkins 연동
- **팀 협업**: 코드 리뷰 공유 및 토론
- **커스텀 규칙**: 회사별 코딩 표준 적용
- **성능 모니터링**: 코드 품질 트렌드 분석
- **다국어 지원**: 더 많은 프로그래밍 언어 추가

### API 확장
- REST API 제공
- 웹훅 지원
- 외부 도구 통합

## 📊 성능 최적화

- 벡터 데이터베이스 캐싱
- 비동기 처리
- 메모리 효율적인 코드 분석

## 🤝 기여 방법

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 📞 지원

문제가 발생하거나 제안사항이 있으시면 이슈를 생성해주세요.

---

**개발자**: AI Talent Lab 과제 프로젝트  
**버전**: 1.0.0  
**최종 업데이트**: 2024년 6월 