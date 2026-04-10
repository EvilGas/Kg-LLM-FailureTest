### llm 根据处理后的需求，去图谱中查找有关的数据
import pandas as pd
import ast
import re

## 解析字符串到数组
def parse_lists(s: str):
    """
    解析字符串："ts_entities = [xxx], ts_relations = [xxx]"
    返回：entities_list, relations_list
    """
    # 用正则精准提取两个数组内容
    entities_match = re.search(r"ts_entities\s*=\s*(\[.*?\])", s)
    relations_match = re.search(r"ts_relations\s*=\s*(\[.*?\])", s)

    entities_str = entities_match.group(1) if entities_match else "[]"
    relations_str = relations_match.group(1) if relations_match else "[]"

    # 安全转成列表
    entities = ast.literal_eval(entities_str)
    relations = ast.literal_eval(relations_str)

    return entities, relations

# ---------------------- 检索函数 ----------------------
def retrieve_kg_message(standard_message):
    """
    输入：llm提取出的实体列表、关系列表
    输出：用于图片推理/问答的增强prompt
    """

    ts_entities, ts_relations = parse_lists(standard_message)


    # 读取图谱
    triple_df = pd.read_csv("./data/triples.csv", encoding="utf-8")

    # 筛选匹配的三元组
    matched = triple_df[
        (triple_df["head_entity"].isin(ts_entities) | triple_df["tail_entity"].isin(ts_entities)) &
        triple_df["relation"].isin(ts_relations)
    ]

    # 拼接知识
    kg_info = []
    for _, row in matched.iterrows():
        kg_info.append(
            f"[{row['head_entity']} {row['tail_entity']} {row['relation']}，时间：{row['timestamp']}]"
        )

    knowledge_str = "\n".join(kg_info) if kg_info else "无相关时序知识图谱信息"

    return knowledge_str