# 知识图谱

import streamlit as st
from pyvis.network import Network
import streamlit.components.v1 as components
import pandas as pd
import json
import os
import random

st.set_page_config(page_title="设备检测系统", page_icon="🏭", layout="wide")
st.title("知识图谱")

def generate_graph(nodes, edges):
    # 只保留最基础、最稳定的参数
    net = Network(directed=True, height="600px", width="90%")

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
    # 定义数据文件路径
    entities_file = "./data/entities.csv"
    triples_file = "./data/triples.csv"

    nodes = []
    edges = []

    # -------------------------- 从文件中读取节点和边 --------------------------
    if os.path.exists(entities_file) and os.path.exists(triples_file):
        df_entities = pd.read_csv(entities_file)
        nodes = df_entities['entity_name'].dropna().unique().tolist()

        df_triples = pd.read_csv(triples_file)

        for _, row in df_triples.iterrows():
            source_name = row['head_entity']
            target_name = row['tail_entity']
            relation = row['relation']
            timestamp = row['timestamp']

            relation_label = f"{relation} ({timestamp})"
            edges.append((source_name, target_name, relation_label))

    else:
        st.error(f"未找到文件：请确保该文件存在于当前目录。")

    # -------------------------- 展示图谱 --------------------------

    col_ctrl1, col_ctrl2 = st.columns([2, 1])
    with col_ctrl2:
        sample_size = st.slider("选择最少展示的节点数量", min_value=30, max_value=100, value=30, step=10)

    part_nodes, part_edges = [], []

    if len(nodes) > 0:
        # 随机选50个
        sampled_nodes = random.sample(nodes, sample_size)
        # 找到它们的关联节点 & 关联边
        sampled_edges = []
        related_nodes = set(sampled_nodes)

        for s, t, r in edges:
            if s in sampled_nodes or t in sampled_nodes:
                sampled_edges.append((s, t, r))
                related_nodes.add(s)
                related_nodes.add(t)

        part_nodes = list(related_nodes)
        part_edges = sampled_edges

    if part_nodes or part_edges:
        html_code = generate_graph(part_nodes, part_edges)
        components.html(html_code, height=650)
    else:
        st.warning("⚠️ 没有数据可展示...")

    # -------------------------- 展示数据 --------------------------
    col1, col2 = st.columns([2, 4])
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
        st.subheader("时序三元组列表")
        if edges:
            df_edges = pd.DataFrame(edges, columns=["源节点", "目标节点", "关系类型"])

            st.dataframe(
                df_edges,
                hide_index=True,
                height=400
            )
        else:
            st.info("暂无关系数据")
