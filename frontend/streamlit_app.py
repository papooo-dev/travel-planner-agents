import streamlit as st
import requests
import uuid
import json

# 페이지 레이아웃 설정
st.set_page_config(layout="wide")
st.title("✈️ 여행 일정 도우미")

# API 엔드포인트 설정
AGENT_SERVER = "http://localhost:8000"
AGENT_CHAT_ENDPOINT = f"{AGENT_SERVER}/chat"


# 채팅 기록 초기화
if "messages" not in st.session_state:
    thread_id = str(uuid.uuid4())
    st.session_state.thread_id = thread_id
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "여행을 준비 중이시군요!🤗  제가 즐거운 여행 계획 세우기를 도와드릴게요!✈️ \n\n 어디로 여행을 떠나시나요? 😊",
        }
    ]

# CSS 스타일 추가
st.markdown("""
<style>
.message-container p {
    margin-bottom: 10px !important;
}
.message-container ul {
    margin-bottom: 10px !important;
    padding-left: 20px !important;
}
.message-container li {
    margin-bottom: 5px !important;
}
</style>
""", unsafe_allow_html=True)

# 채팅 기록 표시
with st.container():
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"], unsafe_allow_html=True)

# 사용자 입력 처리
if prompt := st.chat_input("질문을 입력하세요."):
    # 사용자 메시지 추가
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # AI 응답 생성
    with st.chat_message("assistant"):
        st.session_state.response = ""
        placeholder = st.empty()

        # FastAPI 서버로 스트리밍 요청
        with st.spinner("응답 생성 중..🧑‍💻"):

            # 이전 대화 기록과 함께 요청 보내기
            def response_generator():
                try:
                    response = requests.post(
                        AGENT_CHAT_ENDPOINT,
                        json={"query": prompt, "thread_id": st.session_state.thread_id},
                        stream=True,
                        headers={"Content-Type": "application/json"}
                    )

                    if response.status_code == 200:
                        for line in response.iter_lines():
                            if line:
                                line_text = line.decode('utf-8')
                                if line_text.startswith("data: "):
                                    content = line_text[6:]  # "data: " 제거
                                    try:
                                        # JSON 문자열을 파싱
                                        json_content = json.loads(content)
                                        # 파싱된 JSON에서 실제 내용 추출
                                        actual_content = json_content
                                        st.session_state.response += actual_content
                                        placeholder.markdown(st.session_state.response, unsafe_allow_html=True)
                                        yield actual_content
                                    except json.JSONDecodeError:
                                        # JSON 파싱에 실패하면 원본 내용 사용
                                        st.session_state.response += content
                                        placeholder.markdown(st.session_state.response, unsafe_allow_html=True)
                                        yield content
                    else:
                        error_msg = f"서버 오류: {response.status_code}"
                        placeholder.error(error_msg)
                        yield {"type": "error", "content": error_msg}
                except Exception as e:
                    error_msg = f"오류가 발생했습니다: {str(e)}"
                    st.error(error_msg)
                    yield {"type": "error", "content": error_msg}

            # 스트리밍 응답 처리
            responses = []
            for resp in response_generator():
                responses.append(resp)
            
            # 오류가 발생하지 않았을 때만 최종 응답 저장
            st.session_state.messages.append({"role": "assistant", "content": st.session_state.response})
