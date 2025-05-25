from langgraph.prebuilt import create_react_agent
from dotenv import load_dotenv
import os
from langchain.chat_models import init_chat_model
from backend.prompts import PLANNER_PROMPT

from backend.store import get_place_info, get_travel_schedule, save_travel_schedule

load_dotenv()

# 여행 일정 에이전트 생성
planner_agent = create_react_agent(
    model=init_chat_model(model=os.getenv("PLANNER_MODEL"), temperature=0.0),
    tools=[save_travel_schedule, get_travel_schedule, get_place_info],
    prompt=PLANNER_PROMPT,
    name="planner_agent",
).with_config(tags=["planner_agent"])
