import streamlit as st
import requests

# 페이지 레이아웃 설정
st.set_page_config(layout="wide")
st.title("✈️ 여행 일정 도우미")

# API 엔드포인트 설정
AGENT_SERVER = "http://localhost:8000"
AGENT_CHAT_ENDPOINT = f"{AGENT_SERVER}/chat"


st.markdown("### 여행 계획 채팅")

# 채팅 기록 초기화
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "여행을 계획 중이시군요!🤗  제가 여행 계획 세우기를 도와드릴게요!✈️ \n\n 어디로 여행을 떠나시나요? 😊",
        }
    ]

# 채팅 기록 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"], unsafe_allow_html=True)

# 사용자 입력 처리
if prompt := st.chat_input("여행 계획에 대해 물어보세요..."):
    # 사용자 메시지 추가
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # AI 응답 생성
    with st.chat_message("assistant"):
        try:
            placeholder = st.empty()

            session_id = st.session_state.get("session_id", "")

            # FastAPI 서버로 스트리밍 요청
            with st.spinner("응답 생성 중..."):
                # 이전 대화 기록과 함께 요청 보내기
                session_id = st.session_state.get("session_id", "")

                # 스트리밍 생성기 함수 정의
                def response_generator():
                    response = requests.post(
                        AGENT_CHAT_ENDPOINT,
                        json={"query": prompt, "session_id": session_id},
                        stream=True,
                        headers={"Content-Type": "application/json"}
                    )

                    if response.status_code == 200:
                        full_response = ""
                        for line in response.iter_lines():
                            if line:
                                line_text = line.decode('utf-8')
                                if line_text.startswith("data: "):
                                    content = line_text[6:]  # "data: " 제거
                                    full_response += content
                                    yield content

                        return full_response
                    else:
                        yield f"서버 오류: {response.status_code}"

                # 스트리밍 응답 표시
                full_response = st.write_stream(response_generator())

                # 최종 응답 저장
                st.session_state.messages.append({"role": "assistant", "content": full_response})

        except Exception as e:
            st.error(f"오류가 발생했습니다: {str(e)}")
            st.warning(
                "FastAPI 서버가 실행 중인지 확인해주세요. (http://localhost:8000)"
            )