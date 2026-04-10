import ast
import re

def parse_entities_relations(s: str):
    """
    安全解析：ts_entities = [...], ts_relations = [...]
    不会被数组内部的逗号干扰
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


# 测试用例（你的原字符串）
a = """ts_entities = ['直升机'], ts_relations = []"""

# 解析
ts_entities, ts_relations = parse_entities_relations(a)

# 输出
print("实体数组：", ts_entities)
print("关系数组：", ts_relations)