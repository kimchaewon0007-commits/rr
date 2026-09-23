import streamlit as st
from openai import OpenAI

# 페이지 기본 설정 (제목과 아이콘)
st.set_page_config(page_title="정보 선생님 AI 채팅", page_icon="💬")

# 페이지 제목 표시
st.title("💬 친절한 정보 선생님")
st.write("중고등학생의 눈높이에 맞춰 무엇이든 쉽게 알려주는 AI 선생님이야!")

# 스트림릿 시크릿(secrets)에서 Gemini API 키 불러오기
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.error("비밀 금고(secrets)에 GEMINI_API_KEY가 설정되어 있지 않아. 설정을 확인해 줘!")
    st.stop()

# OpenAI 라이브러리를 사용하여 Gemini API 클라이언트 초기화 (OpenAI 호환 엔드포인트 사용)
client = OpenAI(
    api_key=api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

# AI 선생님의 성격 정의 (시스템 프롬프트)
system_prompt = (
    "너는 중고등학생에게 설명하는 친절한 정보 선생님이야. "
    "어려운 말은 쉬운 말로 바꿔 주고, 반드시 순수 한국어로만 답해"
)

# 대화 기록을 저장할 세션 상태 초기화 (이전 대화를 기억하기 위함)
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": system_prompt}
    ]

# 화면에 이전 대화 기록들(말풍선) 다시 출력하기 (시스템 프롬프트는 화면에 표시하지 않음)
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# 사용자로부터 채팅 입력 받기
if user_input := st.chat_input("선생님께 궁금한 점을 물어보세요!"):
    
    # 사용자가 입력한 메시지를 대화 기록에 추가
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # 사용자의 메시지를 화면에 말풍선으로 바로 출력
    with st.chat_message("user"):
        st.markdown(user_input)

    # AI 선생님의 답변을 출력할 영역과 실시간 스트리밍 처리
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            # Gemini API(gemini-3.5-flash-lite)에 대화 내용 전달 및 스트리밍 응답 요청
            response = client.chat.completions.create(
                model="gemini-3.5-flash-lite",
                messages=st.session_state.messages,
                stream=True,  # 글자가 실시간으로 흘러나오도록 설정
            )
            
            # 받아온 조각(chunk)들을 이어 붙이며 실시간으로 화면에 갱신
            for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")
            
            # 최종 완성된 답변을 말풍선에 확정 표시
            message_placeholder.markdown(full_response)
            
            # AI의 답변도 대화 기록에 추가 (다음 대화에서 기억할 수 있도록)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception:
            # 오류 발생 시 빨간 화면 대신 친절한 안내 문구 한 줄 출력
            message_placeholder.error("앗, 선생님과의 연결에 문제가 생겼어. 잠시 후에 다시 시도해 줘!")

