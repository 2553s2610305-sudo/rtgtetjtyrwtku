import streamlit as st
from google import genai
from google.genai import types
from google.genai.errors import APIError

# 1. 페이지 설정 및 제목
st.set_page_config(page_title="달콤살벌 연애상담소", page_icon="💌")
st.title("💌 달콤살벌 연애상담소")
st.caption("연애 고민, 썸, 이별... 혼자 끙끙 앓지 말고 무엇이든 물어보세요!")

# 2. Streamlit Secrets에서 API 키 불러오기 및 클라이언트 초기화
try:
    # Streamlit Cloud 배포 시 Secrets에 등록한 값을 가져옵니다.
    gemini_api_key = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=gemini_api_key)
except KeyError:
    st.error("❌ API 키를 찾을 수 없습니다. Streamlit Secrets에 'GEMINI_API_KEY'를 등록해주세요.")
    st.stop()

# 3. 세션 상태(Session State)로 채팅 기록 유지
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "안녕하세요! 당신의 연애 고민을 들어줄 전문 상담사입니다. 어떤 고민이 있으신가요?"}
    ]

# 4. 기존 채팅 기록 화면에 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# 5. 사용자 입력 받기
if user_input := st.chat_input("고민을 이야기해주세요... (예: 썸남이 선톡을 안 해요)"):
    # 사용자 메시지 화면에 표시 및 세션에 저장
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    # 6. 챗봇의 답변 생성 (오류 처리 포함)
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("🔄 답변을 생각 중입니다...")
        
        try:
            # 대화 맥락을 유치하기 위해 기존 대화 기록을 Gemini API 형식에 맞게 변환
            # (단, 시스템 프롬프트나 가벼운 처리를 위해 구조화)
            contents = []
            for msg in st.session_state.messages[:-1]: # 현재 입력 제외한 이전 기록들
                # genai 라이브러리는 롤을 'user'와 'model'로 구분합니다.
                role_mapping = "user" if msg["role"] == "user" else "model"
                contents.append(types.Content(
                    role=role_mapping,
                    parts=[types.Part.from_text(text=msg["content"])]
                ))
            # 현재 사용자 입력 추가
            contents.append(user_input)

            # Gemini 2.5 Flash Lite 모델 호출 및 역할 부여 (System Instruction)
            response = client.models.generate_content(
                model='gemini-2.5-flash-lite',
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=(
                        "당신은 공감 능력이 뛰어나면서도 때로는 뼈를 때리는 현실적인 조언을 해주는 "
                        "전문 연애 상담사입니다. 친구처럼 친근하고 다정한 말투를 사용하되, "
                        "상황에 맞춰 진지하게 조언해주세요. 이모티콘을 적절히 섞어 써주세요."
                    ),
                    temperature=0.7,
                )
            )
            
            # 결과 출력 및 세션 저장
            ai_response = response.text
            message_placeholder.markdown(ai_response)
            st.session_state.messages.append({"role": "assistant", "content": ai_response})
            
        except APIError as e:
            message_placeholder.markdown("❌ Gemini API 오류가 발생했습니다. 잠시 후 다시 시도해주세요.")
            st.sidebar.error(f"API Error 상세 정보: {e}")
        except Exception as e:
            message_placeholder.markdown("❌ 알 수 없는 오류가 발생했습니다.")
            st.sidebar.error(f"Error 상세 정보: {e}")
