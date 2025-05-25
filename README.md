# 여행 일정 도우미

대화형 인터페이스를 통해 여행 장소를 검색하고 여행 일정을 생성할 수 있는 애플리케이션입니다.

## 기능

-   대화형 인터페이스로 자연스러운 여행 일정 계획
-   여행지 검색 및 추천
-   일정 생성 및 최적화
-   여행 일정 캘린더 반영 및 이메일 공유 기능

## 기술 스택

### 백엔드

-   FastAPI: API 서버
-   LangGraph: AI 에이전트 오케스트레이션
-   LangChain: 대규모 언어 모델(LLM) 애플리케이션 프레임워크
-   OpenAI: 자연어 처리 및 생성 AI

### 프론트엔드

-   Streamlit: 대화형 데이터 애플리케이션 구축 프레임워크

## 설치 및 실행

1. 저장소 클론

```bash
git clone https://github.com/yourusername/travel-planner-agents.git
cd travel-planner-agents
```

2. uv 설치

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
irm https://astral.sh/uv/install.ps1 | iex
```

3. 환경 변수 설정
   `.env` 파일을 생성하고 필요한 API 키 설정 (OpenAI API 키 등)

4. 서버 실행

-   백엔드 + 프론트엔드 동시 실행

```bash
# 또는 한 번에 모두 실행하기
bash scripts/run_all.sh
```

-   백엔드 서버 실행

```bash
uvicorn backend.main:app --reload --port 8000
```

-   프론트엔드 실행

```bash
streamlit run frontend/streamlit_app.py
```

## 사용 방법

1. 웹 브라우저에서 `http://localhost:8501` 접속
2. 대화창에 여행 관련 질문이나 요청 입력
3. AI 에이전트가 응답하며 여행 계획 작성 지원

## 프로젝트 구조

```
travel-planner-agents/
├── backend/                # 백엔드 코드
│   ├── agents/             # AI 에이전트 모듈
│   │   ├── supervisor.py   # 에이전트 관리자
│   │   ├── place_search.py # 장소 검색 에이전트
│   │   ├── calendar.py     # 일정 관리 에이전트
│   │   ├── planner.py      # 여행 계획 에이전트
│   │   └── share.py        # 공유 기능 에이전트
│   ├── prompts/            # 프롬프트 템플릿
│   ├── main.py             # FastAPI 메인 애플리케이션
│   └── store.py            # 여행 정보 중앙 저장소
├── frontend/               # 프론트엔드 코드
│   └── streamlit_app.py    # Streamlit 애플리케이션
├── requirements.txt        # 프로젝트 의존성
├── pyproject.toml          # 프로젝트 메타데이터
└── README.md               # 프로젝트 설명서
```
