import streamlit as st
import pandas as pd
import json
import os

# -------------------------- 页面配置 --------------------------
st.set_page_config(page_title="设备检测系统", page_icon="🏭", layout="wide")
st.title("诊断记录")


history_file = "./data/record_history.csv"

try:
    if os.path.exists(history_file) and os.path.getsize(history_file) > 0:
        df = pd.read_csv(history_file)

        if not df.empty:
            df = df.sort_values(by="检测时间", ascending=False)

            for index, row in df.iterrows():
                with st.expander(f"{row.检测时间} - {row.用户问题}"):
                    st.markdown(f"**检测时间：** {row.检测时间}")
                    st.markdown(f"**用户问题：** {row.用户问题}")
                    st.markdown(f"**检测结果：** {row.检测结果}")
                    st.markdown(f"**参考依据：** {row.参考依据}")
        else:
            st.info("暂无记录")
except:
    st.info("暂无记录")