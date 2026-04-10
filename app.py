import streamlit as st

pages = [
    # st.Page("pages/DataLoad.py", title="数据加载", icon="🕸️"),
    st.Page("pages/KgView.py", title="知识图谱", icon="🕸️"),
    st.Page("pages/FailureTest.py", title="故障检测", icon="🕸️"),
    st.Page("pages/DiagnosisRecord.py", title="诊断记录", icon="🕸️"),
    # st.Page("pages/four.py", title="四元组", icon="🕸️"),
    # st.Page("pages/four_display.py", title="四元组展示", icon="🕸️"),
]

# 创建导航对象
pg = st.navigation(pages)

# 运行导航
pg.run()