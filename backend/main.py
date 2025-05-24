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


async def agent_stream(query: str, thread_id: str):
    """LangGraph agent의 .stream() 결과를 SSE로 변환해 Yield"""
    async for evt in supervisor_agent.astream_events(
        # async for chunk in supervisor_agent.astream(
        {"messages": [{"role": "user", "content": query}]},
        config={"configurable": {"thread_id": thread_id}},
        stream_mode="messages",
        version="v2",
    ):
        if evt["event"] == "on_chat_model_stream":
            chunk = evt["data"]["chunk"]  # ChatMessage
            if chunk.content:
                if evt["tags"] in ["place_search_agent", "place_search_agent"]:
                    # 다른 agent 응답
                    yield sse_format(chunk.content)
                else:
                    # supervisor agent 응답
                    yield sse_format(chunk.content)



@app.post("/chat")
async def agent_chat(body: dict):
    query: str = body.get("query", "")
    thread_id: str = body.get("thread_id", "")

    return StreamingResponse(
        agent_stream(query, thread_id),
        media_type="text/event-stream",
    )
