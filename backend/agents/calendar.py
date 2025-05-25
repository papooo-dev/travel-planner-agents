from langchain_google_community import (
    CalendarCreateEvent,
    CalendarDeleteEvent,
    CalendarMoveEvent,
    CalendarSearchEvents,
    CalendarUpdateEvent,
    GetCalendarsInfo,
)
from langgraph.prebuilt import create_react_agent
from dotenv import load_dotenv
import os
from langchain.chat_models import init_chat_model
from backend.store import get_travel_schedule
from backend.prompts import CALENDAR_PROMPT
from langchain_google_community.calendar.utils import (
    build_resource_service,
    get_google_credentials,
)

load_dotenv()

# 캘린더 도구 생성
credentials = get_google_credentials(
    token_file=os.getenv("GOOGLE_CALENDAR_TOKEN_FILE_PATH"),
    scopes=["https://www.googleapis.com/auth/calendar"],
    client_secrets_file=os.getenv("GOOGLE_CLIENT_SECRET_FILE_PATH"),
)

api_resource = build_resource_service(credentials=credentials)

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
    model=init_chat_model(model=os.getenv("CALENDAR_MODEL"), temperature=0.0).bind_tools(
        tools,
        parallel_tool_calls=False,
    ),
    tools=tools,
    prompt=CALENDAR_PROMPT,
    name="calendar_agent",
).with_config(tags=["calendar_agent"])
