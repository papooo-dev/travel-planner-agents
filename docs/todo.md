



- 기본 UI 구현

  - [x] Streamlit을 활용한 채팅 인터페이스 구현

  - [x] Agent가 있는 FastAPI에 스트리밍 응답 구현

- 멀티 에이전트 구현
  - [ ] Supervisor Agent 구현
  - [ ] Search Agent
  - [ ] Planning Agent
  - 대화 소통 잘 안되면 State Memory?방식 공부해서 구현해보기
  - [ ] Calendar Agent 
  - [ ] Share Agent

- 테스트 시나리오 생성

  - 테스트 시나리오 만들어보기 (LLM 답변의 지속적인 품질 테스트 방법을 구축합니다.)

- 문서화

  -   README 작성

  -   아키텍처 문서 작성

  -   사용된 AI 개발 도구 설명 문서 작성

  -   대화 내역 캡처 및 정리





---

-   요구 사항 구체화
    -   에이전트와의 대화를 통해 여행 장소를 검색합니다.
        -   대화에 질문을 고정해둔다.
        -   "어디로", "몇박며칠", "누구와", "어떤 목적"으로 여행을 떠나는지 질문
        -   추가적으로 사용자의 일정 파악 전에
    -   대화를 통해 여행 계획서를 작성합니다.
        -   에이전트가 초안을 짠다. => 여행계획서에 표시됨 (숙소, 맛집, 즐길거리) (\* 이때 동선 고려?)
    -   대화를 통해 여행 일정을 캘린더에 등록, 조회, 수정, 삭제합니다.
        -   여행 계획서에서 각 항목별 api를 통해 CRUD 가능 (이동시간, 휴식, 숙소는 X)
    -   대화를 통해 여행 계획서를 외부에 공유합니다.
        -   md 포맷으로 작성된 여행 계획서를 pdf로 다운로드받기, 이메일로 공유하기 가능
    -   에이전트가 거짓 정보를 제공하지 않도록 합니다.

Agent 구성과 요구사항 분석을 통해 Agent flow 아키텍쳐와 전체 프로그램의 아키텍쳐를 작성해줘. 

참고 코드 사이트:
- 나는 langgraph의 prebuilt를 이용해서 에이전트를 구현할거야. (https://langchain-ai.github.io/langgraph/agents/overview/)
- 멀티에이전트는 supervisor 방식으로 구현할거야. (참고: https://langchain-ai.github.io/langgraph/agents/multi-agent/)

정리:
### [Agent 구성]
1. Supervisor Agent (create_supervisor을 통해 구현)
    - 주요책임:
        - 대화 기록·상태 보존
        - 사용자 의도 분석 후 워커 호출 결정
        - 응답 스트리밍 통합
    - 사용 Tool/API: 미정
    - 메모: 에러 핸들링·리트라이·가드레일 중앙집중
2. Info Collector Agent:
    - 주요책임:
        - 여행지 정보 탐색
        - 질문 템플릿 5개 내외: 여행지·기간·동행·목적·추가정보
    - 사용 Tool/API: LangGraph LLM
3. Place Search Agent
    - 주요책임:
        - 키워드·좌표 기반 장소 탐색
        - 평점·리뷰·이동시간 수집
    - 사용 Tool/API: Kakao map API
    - 메모:결과를 json으로 반환
4. Itinerary Planner Agent
    - 주요책임
        - 여행 일정(계획)표 생성
        - 사용자 제약 조건 반영
    - 사용 Tool/API: 미정
    - 메모: 지도, 거리, 오픈시간 고려
5. Calendar Agent
    - 주요책임
        - Google Calendar CRUD
        - 일정 조회/업데이트/삭제
    - 사용 Tool/API
        - google calendar toolkit
    - 메모: 타임존은 한국(서울) 시간
6. Validator Agent
    - 주요책임
        - Place Search Agent의 응답에서 사실여부 확인하고, 수정 필요 시 수정
        - 장소 존재 여부, 운영시간 실제 값 교차 검증
        - LLM Hallucination 감시
    - 사용 Tool/API: Naver map API
    - 메모: 검증 실패 시 수정된 정보로 반환
    7.Share Agent
    - 주요책임
        - 이메일을 요청하여 받음
        - 생성된 여행 일정(계획)표를 이메일로 전송
    - 사용 Tool/API: Gmail Toolkit
    - 메모: 이메일 전송 실패 시, 메시지로 전송 실패하였다고 보내줌

### [Agent 흐름도]
1. Supervisor Agents는 상태메모리에 여행기본정보가 없는 경우 Info Collector Agent를 통해 기본정보를 수집한다.(질문은 미리 템플릿으로 정해진 질문을 한다.) 수집된 기본정보는 상태메모리에 저장한다. 완료 시, supervisor agent는 이제 여행지에 대해 탐색해보자고 user에게 말한다.
2. User가 여행지에 대해 정보를 탐색하고자 한다면, Place Search Agent 를 통해 User의 질문과 기본정보를 통해 여행지의 정보를 탐색한다. 이때 여행지 정보 json 파일이 생성되면 Validator Agent에게 보내져서 장소 존재 여부, 운영 시간을 확인하여, Validation Agent가 재작성한다. 완료된 json 파일을 supervisor agent에게 전송하고, 요약한 내용을 user에게 전달해준다.
3. User가 여행계획서 작성을 원한다면, Calendar Agent를 통해 기존 사용자의 해당 일정의 내용을 읽어오고, 이 내용을 supervisor에게 전달해. 그리고 supervisor는 Itinerary Planner Agent를 호출해서 이 내용과 여행지정보를 통해 일정표를 작성해.
4. User가 일정을 캘린더에 반영해주기를 요청하면 Calendar Agent를 통해 일정표를 가지고, 사용자의 구글캘린더에 일정을 추가해. 
5. User가 일정을 외부로 공유하기를 요청하면 이메일을 요청해서, 해당 이메일로 일정표를 전송해.


### [요구사항 분석]:
* UI(streamlit으로 구현) : 두 개의 창으로 표현되고, 왼쪽은 대화, 오른쪽은 여행계획서.
1. 사용자로부터 여행 일정 작성에 필요한 기본정보 획득
   - 어디로, 몇박며칠일정으로, 누구와, 어떤목적으로 여행을 떠나는지 질문해서 답을 받아
   - 추가적으로 받으면 좋은 정보가 있다면 물어보도록해.
2. 여행지 정보 탐색 (Place Search Agent + Validator Agent)
   - 여행 장소, 기간, 누구와, 목적, 추가정보를 통해 여행지의 장소를 탐색해서 여행지의 정보를 탐색한다.
   - 평점, 리뷰, 이동시간 등
3. 여행일정(계획표) 작성 
    - 1에서 받은 여행기간을 통해 사용자의 google calendar와 연동해서 그 기간동안의 일정을 받아와 (Calendar Agent)
    - 기존일정과 탐색된 여행정보를 통해 지도, 거리, 오픈시간 고려해서 일정 초안을 생성해줘. (Itinerary Planner Agent)
    - 세운 일정을 여행계획서에 보여줘
4. 여행일정 상세화 (Place Search Agent + Validator Agent + Itinerary Planner Agent)
    - 2-3 과정을 반복하며 여행일정을 수정할 수 있어.
    - 사용자와 대화를 통해 여행일정을 수정해줘. (이때 대화를 통해 여행지를 탐색하고, 탐색된 정보를 검증하고, 검증된 정보를 일정표로 만들어줘)
5. 일정 반영 (Calendar Agent)
    - 사용자가 원하는 여행계획을 다 세운 후, 사용자가 "여행 일정을 캘린더에 등록하기"를 요청하면 여행계획서의 일정을 google calendar에 반영해줘.
6. 일정 공유
    - 사용자가 "여행 일정 공유"를 요청하면, 이메일을 요청한 후 받아서 여행계획서를 입력받은 이메일로 전송해줘.

