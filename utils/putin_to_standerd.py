#### llm 将用户的自然语言输入限制在列表里

import pandas as pd
from utils.Zhipu_LLM import ZhipuLLM
from dotenv import load_dotenv, find_dotenv
from utils.prompts import prompt_analyze_user_query
import os

def llm_analyze_query(query):
    file_path = os.path.abspath(__file__)
    print(file_path)


    # 加载模型
    _ = load_dotenv(find_dotenv())
    api_key = os.environ["ZHIPUAI_API_KEY"]
    llm = ZhipuLLM(api_key=api_key)

    # 读取 entities.csv 文件
    df = pd.read_csv('./data/entities.csv')
    entity_list = df["entity_name"].tolist()

    # 读取 relations.csv 文件
    df = pd.read_csv('./data/relations.csv')
    relation_list = df["relation_name"].tolist()

    prompt = prompt_analyze_user_query(query, entity_list, relation_list)
    response = llm.get_completion(prompt)

    return response