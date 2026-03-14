# 知识图谱

import streamlit as st
from pyvis.network import Network
import streamlit.components.v1 as components
import pandas as pd
import json
import os

st.set_page_config(page_title="设备检测系统", page_icon="🏭", layout="wide")
st.title("知识图谱")

def generate_graph(nodes, edges):
    # 只保留最基础、最稳定的参数
    net = Network(directed=True, height="600px", width="100%")

    # 添加节点
    for n in nodes:
        net.add_node(n, label=n, shape='circle')

    # 添加边
    for s, t, l in edges:
        net.add_edge(s, t, label=l)

    # 最简单的布局
    net.set_options("""{"physics": {"solver": "forceAtlas2Based"}}""")

    html_content = net.generate_html()  # 生成html
    return html_content


if __name__ == '__main__':
    data_file = "./data/kg.json"
    nodes = []
    edges = []

    # -------------------------- 从文件中读取节点和边 --------------------------
    if os.path.exists(data_file):
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        nodes = [item['name'] for item in data['entities']]
        id_to_name = {item['id']: item['name'] for item in data['entities']}

        for rel in data['relations']:
            source_name = id_to_name.get(rel['source'])
            target_name = id_to_name.get(rel['target'])
            if source_name and target_name:
                edges.append((source_name, target_name, rel['relation']))
    else:
        st.error(f"未找到文件：{data_file}，请确保该文件存在于当前目录。")
        nodes = []
        edges = []

    # -------------------------- 展示图谱 --------------------------
    if nodes or edges:
        html_code = generate_graph(nodes, edges)
        components.html(html_code, height=650)
    else:
        st.warning("⚠️ 没有数据可展示...")

    # -------------------------- 展示数据 --------------------------
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("节点列表")
        if nodes:
            df_nodes = pd.DataFrame(nodes, columns=["节点名称"])
            df_nodes.insert(0, "ID", range(1, len(df_nodes) + 1))

            st.dataframe(
                df_nodes,
                hide_index=True,
                height=400
            )
        else:
            st.info("暂无节点数据")

    with col2:
        st.subheader("关系列表")
        if edges:
            df_edges = pd.DataFrame(edges, columns=["源节点", "目标节点", "关系类型"])

            st.dataframe(
                df_edges,
                hide_index=True,
                height=400
            )
        else:
            st.info("暂无关系数据")
