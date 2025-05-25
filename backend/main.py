from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.agents.supervisor import supervisor_agent
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
import json

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
    return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"


async def agent_stream(query: str, thread_id: str):
    """LangGraph agent의 .stream() 결과를 SSE로 변환해 Yield"""
    try:
        async for evt in supervisor_agent.astream_events(
            {"messages": [{"role": "user", "content": query}]},
            config={"configurable": {"thread_id": thread_id}},
            stream_mode="messages",
            version="v2",
        ):
            if evt["event"] == "on_chat_model_stream":
                chunk = evt["data"]["chunk"]  # ChatMessage
                if chunk.content != "" and len(evt['tags']) == 1:
                    yield sse_format(chunk.content)
    except Exception as e:
        # 오류 발생 시 클라이언트에게 오류 정보 전달
        error_data = {
            "agent_type": "error",
            "content": f"오류가 발생했습니다: {str(e)}"
        }
        yield sse_format(json.dumps(error_data, ensure_ascii=False))


@app.post("/chat")
async def agent_chat(body: dict):
    query: str = body.get("query", "")
    thread_id: str = body.get("thread_id", "")

    return StreamingResponse(
        agent_stream(query, thread_id),
        media_type="text/event-stream",
    )
