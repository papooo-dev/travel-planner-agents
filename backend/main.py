from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.agents.supervisor import supervisor_agent
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# 모든 Origin 허용 – 배포 시엔 도메인 화이트리스트로 좁혀 주세요
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def sse_format(data: str) -> str:
    """SSE 프로토콜에 맞춰 data 라인 구성"""
    return f"data: {data}\n\n"

async def agent_stream(query: str, session_id: str):
    """LangGraph agent의 .stream() 결과를 SSE로 변환해 Yield"""
    async for token, metadata in supervisor_agent.astream(
        {"messages": [{"role": "user", "content": query}]},
        config={"configurable": {"thread_id": session_id}},
        stream_mode="messages",
    ):
        msg = token.content
        if msg:
            yield sse_format(msg)


@app.post("/chat")
async def agent_chat(body: dict):
    query: str = body.get("query", "")
    session_id: str = body.get("session_id", "")

    return StreamingResponse(
        agent_stream(query, session_id),
        media_type="text/event-stream",
    )
