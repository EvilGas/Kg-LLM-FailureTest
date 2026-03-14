import streamlit as st
import pandas as pd

st.set_page_config(page_title="设备检测系统", page_icon="🏭", layout="wide")
st.title("数据加载")

if __name__ == '__main__':
    st.success("✅ 系统已成功加载数据")

    DATA_PATH = "./data/output/cwru_structured_metadata.csv"
    df = pd.read_csv(DATA_PATH)
    st.dataframe(df)