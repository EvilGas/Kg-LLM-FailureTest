import streamlit as st
import pandas as pd
import json
import os  # 引入 os 模块用于检查文件路径
from dotenv import load_dotenv, find_dotenv
from utils.Zhipu_LLM import ZhipuLLM
from data_clean import *

st.set_page_config(page_title="设备检测系统", page_icon="🏭", layout="wide")
st.title("数据加载")


def load_llm():
    _ = load_dotenv(find_dotenv())
    # 从环境变量获取 API Key
    api_key = os.environ["ZHIPUAI_API_KEY"]
    llm = ZhipuLLM(api_key=api_key)
    return llm


if __name__ == '__main__':
    llm = load_llm()

    if 'temp_save_data' not in st.session_state:
        st.session_state.temp_save_data = {"new_entities": [], "new_relations": []}

    ##########################################
    st.subheader("1. 上传文件")
    uploaded_file = st.file_uploader(" ", type=["txt", "csv"], label_visibility="collapsed")

    ##########################################
    st.subheader("2. 文件内容预览")
    if uploaded_file is None:
        st.warning("⚠️ 请先上传一个文件")
    else:
        st.success("✅ 系统已成功加载数据")
        DATA_PATH = "./data/output/cwru_structured_metadata.csv"
        df = pd.read_csv(DATA_PATH)
        st.dataframe(df)

    ##########################################
    st.subheader("3. 本体定义")
    default_template = """{
        "Equipment": ["电机", "轴承"],
        "FaultMode": ["内圈故障", "外圈故障", "滚动体故障", "正常"],
        "Feature": ["峭度", "有效值", "峰值因子", "RMS", "BPFO", "BPFI", "BSF"],
        "RootCause": ["润滑不足", "安装偏心", "过载", "疲劳"],
        "Maintenance": ["更换轴承", "补充润滑", "重新校准"],
         "TimePoint": ["2023年1月", "2023年2月", "2023年3月", "上午", "下午", "第一季度", "第二季度"]
}"""
    ontology_define = st.text_area(
        " ",
        value=default_template,
        placeholder="本体定义",
        height=200,
        key="ontology_define",
        label_visibility="collapsed"
    )
    _, btn_gen_1, btn_sub_1 = st.columns([10, 1, 1])
    with btn_gen_1:
        gen_1 = st.button("一键生成", key="gen_1")
    with btn_sub_1:
        sub_1 = st.button("加载", key="sub_1")

    ##########################################
    st.subheader("4. 实体抽取")
    default_template = """轴承在2023年1月峭度很大，判定为内圈故障，原因是润滑不足，建议更换轴承。"""
    entity_extract = st.text_area(
        " ",
        value=default_template,
        placeholder="待抽取文本",
        height=200,
        key="entity_extract",
        label_visibility="collapsed"
    )
    _, btn_gen_2 = st.columns([10, 1])
    with btn_gen_2:
        gen_2 = st.button("一键抽取", key="gen_2")
    if gen_2:
        with st.spinner('正在根据本体定义进行实体抽取...'):
            prompt = f"""你是装备故障实体抽取系统。
                必须从下面文本中，只抽取以下类型的实体：
            - Equipment
            - FaultMode
            - Feature
            - RootCause
            - Maintenance
            - TimePoint

                请严格按照本体定义抽取，不要抽取其他内容。

                文本：{entity_extract}

                输出JSON格式：
                {{
                    "Equipment": [],
                    "FaultMode": [],
                    "Feature": [],
                    "RootCause": [],
                    "Maintenance": [],
                    "TimePoint": []
                }}"""
            response = llm.get_completion(prompt)
            response = llmoutput_to_json(response)
            st.success("实体抽取完成！")
            new_entities = []
            for key, values in response.items():
                # 这里的逻辑稍微调整了一下，防止空列表报错，但保持原意
                if values:
                    new_entities.append({"name": values[0], "type": "notfound"})
            st.session_state.temp_save_data["new_entities"] = new_entities
            with st.expander("查看 JSON 格式结果"):
                st.json(json.dumps(response))

    ##########################################
    st.subheader("5. 关系获取")
    if gen_2:
        with st.spinner('正在分析实体间的关系...'):
            prompt = f"""你是装备故障知识图谱构建专家。
            请分析文本，抽取实体之间的关系。

            ### 1. 已定义的实体
            {{
                "Equipment": ["轴承"],
                "FaultMode": ["内圈故障"],
                "Feature": ["峭度很大"],
                "RootCause": ["润滑不足"],
                "Maintenance": ["更换轴承"],
                "TimePoint": ["2023年1月"]   
            }}

            ### 2. 允许的关系类型 (逻辑约束)
            请严格遵循以下逻辑进行抽取，不要编造关系：
            - (Equipment) --[发生]--> (FaultMode)  *例如：轴承 -> 发生 -> 内圈故障*
            - (FaultMode) --[导致]--> (Feature)    *例如：内圈故障 -> 导致 -> 峭度很大*
            - (RootCause) --[导致]--> (FaultMode)  *例如：润滑不足 -> 导致 -> 轴承故障*
            - (FaultMode) --[建议措施]--> (Maintenance) *例如：磨损 -> 建议措施 -> 更换轴承*
            - (Equipment) --[包含]--> (Component)  *例如：电机 -> 包含 -> 轴承*

            ### 3. 时间关系约束
            - 所有关系必须关联一个时间点或时间段
            - 时间信息用于描述事件发生的时间
            
            ### 4. 输入文本
            {entity_extract}

            ### 5. 输出格式
            仅输出 JSON 格式            
            {
            {   "头实体": "x", 
                "头类型": "x", 
                "关系": "x", 
                "尾实体": "x", 
                "尾类型": "x", 
                "时间": "x",
                "置信度": "x"},
            {...}
            }"""

            response = llm.get_completion(prompt)
            response = llmoutput_to_json(response)
            st.success("关系获取完成！")
            new_relations = []
            for item in response:
                new_relations.append({"source": item['头实体'], "target": item['尾实体'], "relation": item['关系'], "time": item["时间"]})
            st.session_state.temp_save_data["new_relations"] = new_relations
            with st.expander("查看 JSON 格式结果"):
                st.json(json.dumps(response))

    ##########################################
    st.subheader("知识映射")
    st.subheader("知识融合")

    ##########################################
    st.subheader("存入图谱")
    in_database = st.button("入库")
    if in_database:
        with st.spinner('正在入库...'):
            try:
                kg_data = {"entities": [], "relations": []}
                file_path = './data/four.json'

                # --- 修改开始：增加文件存在性和非空检查 ---
                entities_array = []
                relations_array = []
                if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                    # 文件存在且不为空，则读取
                    with open(file_path, 'r', encoding='utf-8') as file:
                        data = json.load(file)
                        # 提取旧数据
                        entities_array = data.get('entities', [])
                        relations_array = data.get('relations', [])
                # --- 修改结束 ---

                for entity in st.session_state.temp_save_data["new_entities"]:
                    entities_array.append(entity)

                for relation in st.session_state.temp_save_data["new_relations"]:
                    relations_array.append(relation)

                # 重新组装数据字典
                kg_data = {
                    "entities": entities_array,
                    "relations": relations_array
                }

                # 写回文件
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(kg_data, f, ensure_ascii=False, indent=4)

                st.success("✅ 数据已成功存入 ./data/four.json")

            except Exception as e:
                st.error(f"入库发生错误: {e}")