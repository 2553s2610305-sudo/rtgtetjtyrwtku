pip install streamlit pandas
import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(page_title="스케줄 앱")

st.title("📅 간단 스케줄 앱")

# 세션 상태 초기화
if "schedule" not in st.session_state:
    st.session_state.schedule = []

# 입력 폼
with st.form("schedule_form"):
    task = st.text_input("할 일")
    task_date = st.date_input("날짜", value=date.today())
    submitted = st.form_submit_button("추가")

# 저장
if submitted:
    if task.strip() != "":
        st.session_state.schedule.append({
            "날짜": str(task_date),
            "할 일": task
        })
        st.success("추가 완료")
    else:
        st.warning("할 일을 입력하세요")

# 데이터 표시
if st.session_state.schedule:
    df = pd.DataFrame(st.session_state.schedule)
    st.subheader("스케줄 목록")
    st.dataframe(df, use_container_width=True)

    # 전체 삭제
    if st.button("전체 삭제"):
        st.session_state.schedule = []
        st.rerun()
else:
    st.info("등록된 스케줄이 없습니다.")
  streamlit run app.py
