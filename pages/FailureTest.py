import streamlit as st
import os
from dotenv import load_dotenv, find_dotenv
from utils.Zhipu_LLM import ZhipuLLM
from utils.putin_to_standerd import llm_analyze_query
from utils.find_kg_message import retrieve_kg_message
from utils.prompts import prompt_enhanced_relative_kg_message
import pandas as pd
from datetime import datetime

st.markdown("""
    <style>
    /* 加宽表单容器 */
    [data-testid="stForm"] {
        max-width: 90% !important;
        width: 90% !important;
    }
    /* 加宽文本框 */
    [data-testid="stTextArea"] {
        max-width: 100% !important;
    }
    </style>
""", unsafe_allow_html=True)

_ = load_dotenv(find_dotenv())
api_key = os.environ["ZHIPUAI_API_KEY"]
llm = ZhipuLLM(api_key)


if __name__ == '__main__':
    st.title('故障检测')


    with st.form('my_form'):
        text = st.text_area('Enter text:',
                            height=200,
                            placeholder='What can i do for you?')

        # 3 个辅助输入
        st.markdown('<spa>A330 电气系统出现客舱灯光闪烁，哪里故障？后果？</span>',unsafe_allow_html=True)
        st.markdown('<span>B737-300 液压系统出现起落架无法放下异响，哪里故障？后果？</span>',unsafe_allow_html=True)
        st.markdown('<span>直升机尾桨控制系统出现异常偏航响动，哪里可能故障？会导致什么？该如何做？</span>',unsafe_allow_html=True)

        col1, col2= st.columns([4, 1])
        with col2:
            submitted = st.form_submit_button('Submit')

        if not llm.api_key:
            st.warning('Please enter your OpenAI API key!', icon='⚠')
        if submitted and llm.api_key:
            with st.spinner("正在思考中..."):
                analyze_message = llm_analyze_query(text)
                st.success(analyze_message)

                find_message = retrieve_kg_message(analyze_message)
                st.success(find_message)

                prompt = prompt_enhanced_relative_kg_message(text, find_message)
                #st.success(prompt)

                response = llm.get_completion(prompt)
                st.info(response)

                # -------------------------- 保存问答记录 --------------------------
                history_file = "./data/record_history.csv"
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
                new_record = {
                    "检测时间": [current_time],
                    "用户问题": [text],
                    "检测结果": [response],
                    "参考依据": [find_message]
                }
                new_df = pd.DataFrame(new_record)
                try: # 如果文件存在，读取原有数据并追加；不存在则直接创建
                    if os.path.exists(history_file) and os.path.getsize(history_file) > 0:
                        existing_df = pd.read_csv(history_file)
                        combined_df = pd.concat([existing_df, new_df], ignore_index=True)
                        combined_df.to_csv(history_file, index=False, encoding='utf-8-sig')
                    else:
                        new_df.to_csv(history_file, index=False, encoding='utf-8-sig')
                except Exception as e:
                    st.error(f"保存历史记录出错: {e}")

