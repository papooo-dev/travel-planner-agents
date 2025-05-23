# Agent Architecture
```mermaid
flowchart TB
 subgraph subGraph0["검증 프로세스"]
        V["Validator Agent"]
        IP["Planner Agent"]
        NM["Kakao Map API"]
  end
    U[/"User"/] <-- 자연어 요청 / 응답 / 질문 --> S["Supervisor"]
    S -- 장소 탐색 요청 --> PS["Place Search Agent"]
    PS -- 키워드 질문 --> S
    PS -- 여행장소 검색 --> KM["Search Tool"]
    KM -- 장소 리스트 --> PS
    PS -- 후보 장소 리스트 --> S
    S -- 여행 계획서 작성 요청(+후보 장소 리스트) --> IP
    IP -- 일정 관련 추가 질문 --> S
    IP -- 선정된 여행지 검증 요청 --> V
    V -- 장소 검증 --> NM
    NM -- 검증 결과 --> V
    V -- 검증된 장소 --> IP
    IP -- 검증 실패 시 재선정 --> IP
    IP -- 여행 계획서 --> S
    S -- 캘린더 일정 요청(+여행 계획서) --> CA["Calendar Agent"]
    CA -- Google Calendar CRUD --> GC["Google Calendar API"]
    CA -- 완료 상태 --> S
    S -- 공유 요청(+여행 계획서) --> SH["Share Agent"]
    SH -- 이메일 발송 --> EM["Email Service"]
    SH -- 완료 상태 --> S

     V:::agent
     IP:::agent
     NM:::api
     U:::agent
     S:::agent
     PS:::agent
     KM:::api
     CA:::agent
     GC:::api
     SH:::agent
     EM:::api
    classDef agent fill:#f3f4f6,stroke:#333,stroke-width:1px,rx:8,ry:8
    classDef data fill:#e0f7fa,stroke:#0aa,stroke-width:1px,rx:8,ry:8,font-style:italic
    classDef api fill:#fff8e1,stroke:#fb8c00,stroke-width:1px,rx:8,ry:8
```

### 핵심 동작 흐름

**사용자 요청→Supervisor**

- 사용자는 자연어로 "여행지를 추천해줘", "일정을 만들어줘" 같은 요청을 보냅니다.
- Supervisor(create_supervisor 기반 LLM + 라우팅 로직)은 사용자의 의도를 분류한 뒤, 호출해야 할 하나의 에이전트와 전달할 파라미터(JSON)를 결정합니다.
- 실패하거나 애매할 경우 "추가 질문"을 만들어 사용자에게 되묻습니다.

**장소 탐색 및 검증 단계 – Place Search Agent**

- 사용자가 여행 장소의 검색을 요청하면 Supervisor는 Place Search Agent를 호출합니다.

- 여행지 검색에 필요한 키워드를 사용자에게 추가 질문을 통해 되묻습니다.

- 사용자가 입력한 키워드를 통해 여행장소를 검색합니다. (Tool 사용)

- Supervisor는 요약된 여행정보를 사용자에게 전달합니다.

- >  Google Place API(운영시간) + Kakao Local API로 후보 장소 리스트(JSON)를 반환 - [참고](https://developers.kakao.com/docs/latest/ko/local/dev-guide#search-by-keyword) 이름, 주소, place_url, 카테고리명, 전화번호

**여행 계획서 작성 및 검증 단계 – Planner Agent → Validator Agent**

- 사용자가 일정표(여행 계획서) 작성을 요청하면 Supervisor는 Planner Agent를 호출합니다.
- 계획서 작성을 위한 정보(일정-며칠부터 며칠까지, 차 여부)를 사용자에게 추가 질문을 통해 되묻습니다. 
- 후보 장소리스트를 통해 일정 계획서에 올릴 여행지를 선정합니다
- 오픈시간을 고려하여 일자별 타임라인을 생성하여 여행계획서를 작성합니다. (날씨고려?) . (w/ Google Place API)
- supervisor는 planner Agent로부터 여행계획서를 받아서 Validator Agent를 통해 검증을 실행합니다. (상호명, 주소 존재 여부 검증)
- 검증에 성공한 경우, 검증된 여행계획서를 supervisor agent에게 전달합니다.
- 검증에 실패한 경우 수정된 여행지에 대한 정보로 다시 planner Agent에게 전달해서 planner agent는 여행계획서를 다시 작성합니다.
- agent가 작업이 완료되면, Supervisor는 여행계획서 완료가 되었다고 채팅에 알리고, 화면 우측에 여행계획서에 데이터를 전송합니다. 

**캘린더 일정 생성 단계 - Calendar Agent**

- 사용자가 여행 일정을 캘린더에 반영해달라고 요청하면, Supervisor는 Calendar Agent를 호출합니다.
- 여행계획서를 통해 Google Calendar API를 통해 CRUD를 합니다.
- agent의 작업 완료 후, supervisor는 성공·실패 상태를 사용자에게 전달합니다.

**여행 계획서 공유 단계 - Share Agent**

- 사용자가 여행 계획서를 공유를 요청하면,  Supervisor는 Share Agent를 호출합니다.
- 사용자의 이메일로 여행계획서를 전송합니다.



# System Architecture
```mermaid
flowchart LR
    %% ───────────────── Frontend ─────────────────
    subgraph Streamlit UI
        direction TB
        A1[채팅 창]:::ui
        A2[여행계획서 패널]:::ui
    end

    %% ───────────────── Backend ─────────────────
    subgraph FastAPI Backend
        B1[LangGraph Runtime - Supervisor & Agents]:::backend
        B2[Session State Store - Redis]:::storage
        B3[Vector Store - Chroma/PGVector]:::storage
        B4[PDF/Email Service]:::backend
        B5[Observability - LangSmith Tracing + Prom / Grafana]:::ops
    end

    %% ───────────────── External APIs ─────────────────
    subgraph External APIs
        C1[Kakao Map REST]:::api
        C2[Naver Map REST]:::api
        C3[Google Calendar API]:::api
        C4[SMTP - E-mail]:::api
    end

    %% ───────────────── Edges ─────────────────
    A1 -- SSE / WebSocket 스트리밍 --> B1
    A2 <-- Markdown / JSON patch --> B1

    B1 <--> B2
    B1 <--> B3
    B1 -->|장소 탐색| C1
    B1 -->|검증| C2
    B1 -->|캘린더 CRUD| C3
    B4 -->|메일| C4
    B1 --> B4
    B1 --> B5
```