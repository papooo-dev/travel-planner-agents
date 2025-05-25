from langchain_google_community.gmail.create_draft import GmailCreateDraft
from langchain_google_community.gmail.send_message import GmailSendMessage
from langchain_google_community.gmail.utils import (
    build_resource_service,
    get_gmail_credentials,
)
from langgraph.prebuilt import create_react_agent
from dotenv import load_dotenv
import os
from langchain.chat_models import init_chat_model
from backend.store import get_travel_info, get_travel_schedule
from backend.prompts import SHARE_PROMPT

load_dotenv()

# Gmail 인증 및 툴킷 초기화
try:
    credentials = get_gmail_credentials(
        token_file=os.getenv("GOOGLE_GMAIL_TOKEN_FILE_PATH"),
        scopes=["https://mail.google.com/"],
        client_secrets_file=os.getenv("GOOGLE_CLIENT_SECRET_FILE_PATH"),
    )
    api_resource = build_resource_service(credentials=credentials)
    create_gmail_draft = GmailCreateDraft(api_resource=api_resource)
    send_gmail_message = GmailSendMessage(api_resource=api_resource)
except Exception as e:
    print(f"Gmail 인증 오류: {e}")

# 일정표 공유 에이전트 생성
share_agent = create_react_agent(
    model=init_chat_model(model=os.getenv("SHARE_MODEL"), temperature=0.0),
    tools=[
        get_travel_schedule,
        get_travel_info,
        create_gmail_draft,
        send_gmail_message,
    ],
    prompt=SHARE_PROMPT,
    name="share_agent",
).with_config(tags=["share_agent"])
