from langgraph_supervisor import create_supervisor
from langchain.chat_models import init_chat_model
from backend import store
from backend.agents.place_search import place_search_agent
from backend.agents.planner import planner_agent
from backend.agents.calendar import calendar_agent
from backend.agents.share import share_agent
from backend.prompts import SUPERVISOR_PROMPT
import os

supervisor_agent = create_supervisor(
    agents=[place_search_agent, planner_agent, calendar_agent, share_agent],
    tools=[store.get_place_info, store.save_travel_info, store.get_travel_info, store.get_travel_schedule],
    model=init_chat_model(
        model=os.getenv("SUPERVISOR_MODEL"),
        streaming=True,
    ),
    output_mode="last_message",
    supervisor_name="supervisor",
    prompt=SUPERVISOR_PROMPT,
).compile(store=store.store)
