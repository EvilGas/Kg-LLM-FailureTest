"""
智谱 AI 大模型封装
使用 LangChain 集成智谱 AI
"""
from zhipuai import ZhipuAI
import os
from dotenv import load_dotenv, find_dotenv
# from vector_db_establish import Text_Embedding


class ZhipuLLM:
    """智谱 AI 大模型封装类"""
    def __init__(self, api_key: str = None, model: str = "glm-4-flash", temperature: float = 0.01):
        """
        初始化智谱 AI 模型
        Args:
            api_key: 智谱 AI API Key
            model: 模型名称，默认为 glm-4
        """
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.client = ZhipuAI(api_key=api_key)
        # self.rag = Text_Embedding(api_key=api_key)

    def get_rag_text(self, prompt:str):
        # 再向量空间库中检索
        text_1 = self.rag.similarity_search(prompt, k=3)
        text_2 = self.rag.max_marginal_relevance_search(prompt, k=3)

        # 将检索内容全部转换成 str
        str_text_1 = f"文档 text_1 检索到的内容数：{len(text_1)}\n"
        for i, sim_doc in enumerate(text_1):
            content_preview = sim_doc.page_content
            str_text_1 += f"检索到的第{i}个内容: \n{content_preview}\n--------------\n"

        str_text_2 = f"文档 text_2 检索到的内容数：{len(text_2)}\n"
        for i, sim_doc in enumerate(text_2):
            content_preview = sim_doc.page_content
            str_text_2 += f"检索到的第{i}个内容: \n{content_preview}\n--------------\n"
        return str_text_1 + str_text_2



    def get_completion(self, prompt: str = "hello") -> str:
        """
        发送消息并获取回复
        Args:
        Returns:
            模型回复内容
        """
        messages = messages = [{"role": "user", "content": prompt}]
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature
        )
        if len(response.choices) > 0:
            return response.choices[0].message.content
        return "generate answer error"

# 使用示例
if __name__ == "__main__":
    _ = load_dotenv(find_dotenv())

    # 从环境变量获取 API Key
    api_key=os.environ["ZHIPUAI_API_KEY"]

    llm = ZhipuLLM(api_key=api_key)

    if llm.api_key is None:
        print("请设置 ZHIPUAI_API_KEY 环境变量")
    else:
        response = llm.get_completion("机器学习")
        print(response)

        text = f"""
            在⼀个迷⼈的村庄⾥，兄妹杰克和吉尔出发去⼀个⼭顶井⾥打⽔。\
            他们⼀边唱着欢乐的歌，⼀边往上爬，\
            然⽽不幸降临——杰克绊了⼀块⽯头，从⼭上滚了下来，吉尔紧随其后。\
            虽然略有些摔伤，但他们还是回到了温馨的家中。\
            尽管出了这样的意外，他们的冒险精神依然没有减弱，继续充满愉悦地探索。
            """

        prompt = f"""
            1-⽤⼀句话概括下⾯⽤<>括起来的⽂本。
            2-将摘要翻译成英语。
            3-在英语摘要中列出每个名称。
            4-输出⼀个 JSON 对象，其中包含以下键：English_summary，num_names。
            请使⽤以下格式：
            摘要：<摘要>
            翻译：<摘要的翻译>
            名称：<英语摘要中的名称列表>
            输出 JSON 格式：<带有 English_summary 和 num_names 的 JSON 格式>
            Text: <{text}>
            """

        response = llm.get_completion(prompt)
        print(response)



