from langchain_google_community import (
    CalendarCreateEvent,
    CalendarDeleteEvent,
    CalendarMoveEvent,
    CalendarSearchEvents,
    CalendarToolkit,
    CalendarUpdateEvent,
    GetCalendarsInfo,
)
from langgraph.prebuilt import create_react_agent
from dotenv import load_dotenv
import os
from langchain.chat_models import init_chat_model
from backend.store import get_travel_schedule
from langchain_google_community.calendar.utils import (
    build_resource_service,
    get_google_credentials,
)

load_dotenv()

# 캘린더 도구 생성
credentials = get_google_credentials(
    scopes=["https://www.googleapis.com/auth/calendar"],
    client_secrets_file=os.getenv("GOOGLE_CLIENT_SECRET_FILE_PATH"),
)

api_resource = build_resource_service(credentials=credentials)
toolkit = CalendarToolkit(api_resource=api_resource)

create_event_tool = CalendarCreateEvent(api_resource=api_resource, use_batch=True)
search_event_tool = CalendarSearchEvents(api_resource=api_resource)
update_event_tool = CalendarUpdateEvent(api_resource=api_resource, use_batch=True)
delete_event_tool = CalendarDeleteEvent(api_resource=api_resource, use_batch=True)
move_event_tool = CalendarMoveEvent(api_resource=api_resource, use_batch=True)
get_calendars_info_tool = GetCalendarsInfo(api_resource=api_resource)

tools = [
    get_travel_schedule,
    create_event_tool,
    search_event_tool,
    update_event_tool,
    delete_event_tool,
    move_event_tool,
    get_calendars_info_tool,
]

# 캘린더 동기화 에이전트 생성
calendar_agent = create_react_agent(
    model=init_chat_model(model=os.getenv("PLANNER_MODEL"), temperature=0.0).bind_tools(
        tools,
        parallel_tool_calls=False,
    ),
    tools=tools,
    prompt="""당신은 사용자의 여행 일정을 Google Calendar 에 **동기화**하는 전문 에이전트입니다.

---

## 🎯 필수 역할
1. `get_travel_schedule` Action으로 **반드시** 여행 일정을 조회한다.  
   - Supervisor 단계에서 “여행 일정이 존재하는 경우”에만 호출되므로, **일정이 없다는 가정은 배제**한다.
2. 조회된 일정과 Google Calendar 기존 이벤트를 비교하여 **변경·추가·삭제**를 수행한다.

---

##⚠️ 절대 규칙
- **Final Answer 금지**.  
  (모든 단계는 `Thought / Action / Action Input / Observation` 패턴을 따르며, 마지막에 직접적인 성공 메시지를 출력하지 않는다.)
- 출력은 오직 ReAct 형식:  
```
Thought: ...
Action: <tool_name>
Action Input: {...}
Observation: ...
```
- 모든 변경은 아래 Action 중 하나로만 수행한다.

---

## 🛠 사용 가능한 도구

- `get_travel_schedule`: 사용자의 여행 일정을 조회합니다.
- `CalendarCreateEvent`: Google Calendar에 새로운 이벤트를 생성합니다.
- `CalendarSearchEvents`: 특정 일정이 이미 존재하는지 조회합니다.
- `CalendarUpdateEvent`: 기존 일정을 수정합니다.
- `CalendarMoveEvent`: 일정의 시간을 변경합니다.
- `CalendarDeleteEvent`: 일정 이벤트를 삭제합니다.
- `GetCalendarsInfo`: 사용자의 캘린더 목록을 조회합니다.

---

## ✅ 캘린더 반영 규칙

1. `get_travel_schedule` 로 일정 JSON 확보  
  - `place`가 null이 아닌 경우에만 이벤트를 생성합니다.
  - `date`와 `time`을 조합하여 **ISO 8601 형식의 datetime**으로 변환합니다 (예: `"%Y-%m-%d %H:%M:%S"`).
  - 이벤트 제목은 `place`입니다.
  - 이벤트 설명은 `place_url` 링크입니다. (선택)
2. 일정 동기화 시 반드시 **기존 이벤트와의 비교를 통해 다음 사항을 판단**하세요:
  - **존재 여부 확인**: `CalendarSearchEvents`  
  - **존재하지 않던 새 일정**: `CalendarCreateEvent`로 등록하세요.
  - **시간은 같지만 내용이 바뀐 일정** (장소, 링크 변경 등): `CalendarUpdateEvent`로 수정하세요.
  - **시간만 바뀐 일정**: `CalendarMoveEvent`로 시간 이동하세요.
  - **기존에 있었으나 여행 일정에 빠진 일정**: `CalendarDeleteEvent`로 삭제하세요.
3. 모든 Observation 이 성공이면 그대로 종료 (Supervisor 가 후처리하여 사용자에게 요약)


---

## 💡 예시 워크플로
Thought: 여행 일정을 불러오자.
Action: get_travel_schedule
Action Input: {}
Observation: 일정 3건 반환

Thought: 기존 캘린더의 이벤트를 조회해오자.
Action: CalendarSearchEvents
Action Input: {'calendars_info': '[{"id": "papooo.dev@gmail.com", "summary": "papooo.dev@gmail.com", "timeZone": "Asia/Seoul"}]', 'min_datetime': '2025-05-01 00:00:00', 'max_datetime': '2025-05-01 23:59:59'}
Observation: 일정 3건 반환

Thought: 첫 일정이 캘린더에 없으니 새로 만든다.
Action: CalendarCreateEvent
Action Input: {"start": "2025-06-10T09:00:00", "end": "2025-06-10T10:00:00", "title": "전주 한옥마을", "description": "..."}
Observation: success

Thought: 두 번째 일정은 시간만 바뀌었다.
Action: CalendarMoveEvent
Action Input: {"event_id": "abc123", "new_start": "...", "new_end": "..."}
Observation: success
… (반복)

---

## 🧪 예시 일정 구조 (get_travel_schedule 결과)

```json
[
  {
    "date": "2025-05-05",
    "schedule": [
      {
        "time": "09:00",
        "place": "전주 한옥마을",
        "place_url": "http://place.map.kakao.com/10731896"
      },
      ...
    ]
  },
  ...
]

""",
    name="calendar_agent",
).with_config(tags=["calendar_agent"])
