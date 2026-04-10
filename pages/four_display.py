# 知识图谱

import streamlit as st
from pyvis.network import Network
import streamlit.components.v1 as components
import pandas as pd
import json
import os

st.set_page_config(page_title="设备检测系统", page_icon="🏭", layout="wide")
st.title("时序知识图谱")


def generate_graph(nodes, edges):
    # 初始化网络图
    net = Network(directed=True, height="600px", width="100%")

    # 添加节点
    # 为了美观，可以给不同颜色的节点，这里暂时保持统一，或者根据type区分颜色
    for n in nodes:
        net.add_node(n, label=n, shape='circle', color='#97C2FC')

    # 添加边
    # 这里的 edges 现在包含了时间信息
    for s, t, l, time_val in edges:
        # 将标签设置为 "关系 (时间)" 的格式，以便在图上直观展示时序
        edge_label = f"{l} ({time_val})"
        net.add_edge(s, t, label=edge_label, title=f"时间: {time_val}")

    # 设置物理布局
    net.set_options("""
    {
        "physics": {
            "solver": "forceAtlas2Based",
            "forceAtlas2Based": {
                "gravitationalConstant": -50,
                "centralGravity": 0.01,
                "springLength": 150,
                "springConstant": 0.08
            },
            "stabilization": {"iterations": 150}
        }
    }
    """)

    html_content = net.generate_html()
    return html_content


if __name__ == '__main__':
    # 修改文件路径为 four.json
    data_file = "./data/four.json"
    nodes = []
    edges = []

    # -------------------------- 从文件中读取节点和边 --------------------------
    if os.path.exists(data_file):
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 提取节点
        nodes = [item['name'] for item in data['entities']]

        # 提取边（关系），并处理时间信息
        for rel in data['relations']:
            source_name = rel.get('source')
            target_name = rel.get('target')
            relation_type = rel.get('relation', '未知')
            # 获取时间信息，如果没有则默认为"未知"
            time_val = rel.get('time', '未知')

            # 只要源和目标名称存在，就添加到边列表
            if source_name and target_name:
                # 边的结构变为：(源, 目标, 关系, 时间)
                edges.append((source_name, target_name, relation_type, time_val))


    else:
        st.error(f"未找到文件：{data_file}，请先在'数据加载'页面入库数据。")
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
        st.subheader("关系列表 (四元组)")
        if edges:
            # 修改表头，增加时间列
            df_edges = pd.DataFrame(edges, columns=["源节点", "目标节点", "关系类型", "时间"])

            st.dataframe(
                df_edges,
                hide_index=True,
                height=400
            )
        else:
            st.info("暂无关系数据")