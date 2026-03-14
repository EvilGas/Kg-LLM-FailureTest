import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import kurtosis
from scipy.fft import fft
import json
import os
from datetime import datetime
from pyvis.network import Network
import tempfile

# -------------------------- 页面配置 --------------------------
st.set_page_config(page_title="设备检测系统", page_icon="🏭", layout="wide")
st.title("诊断记录")

# -------------------------- 路径配置 --------------------------
DATA_PATH = "./data/output/cwru_structured_metadata.csv"
KG_PATH = "data/kg.json"
RECORD_PATH = "data/records.json"
os.makedirs("data", exist_ok=True)

# -------------------------- 自动初始化所有文件 --------------------------
def init_files():
    # 初始化模拟数据
    if not os.path.exists(DATA_PATH):
        np.random.seed(42)
        normal_signal = np.random.normal(0, 0.1, 5000)
        fault_signal = np.random.normal(0, 0.5, 5000)
        df = pd.DataFrame({"normal_vib": normal_signal, "fault_vib": fault_signal})
        df.to_csv(DATA_PATH, index=False)

    # 初始化空记录文件
    if not os.path.exists(RECORD_PATH):
        with open(RECORD_PATH, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=2)

    # 如果文件为空，重置
    if os.path.getsize(RECORD_PATH) == 0:
        with open(RECORD_PATH, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=2)

init_files()

# -------------------------- 工具函数 --------------------------
def load_kg():
    try:
        with open(KG_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {"entities": [], "relations": []}

def save_record(record):
    try:
        # 安全读取
        records = []
        if os.path.exists(RECORD_PATH) and os.path.getsize(RECORD_PATH) > 0:
            with open(RECORD_PATH, 'r', encoding='utf-8') as f:
                try:
                    records = json.load(f)
                except:
                    records = []

        records.append(record)

        # 安全写入
        with open(RECORD_PATH, 'w', encoding='utf-8') as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
    except:
        pass

def extract_features(signal):
    try:
        signal = np.asarray(signal, dtype=np.float64)
        signal = signal[~np.isnan(signal)]
        signal = signal[np.isfinite(signal)]

        features = {}
        features['均值'] = float(np.mean(signal))
        features['有效值'] = float(np.sqrt(np.mean(signal**2)))
        features['峰值'] = float(np.max(np.abs(signal)))
        features['峭度'] = float(kurtosis(signal))

        if features['有效值'] > 1e-6:
            features['峰值因子'] = float(features['峰值'] / features['有效值'])
        else:
            features['峰值因子'] = 0.0

        fft_vals = np.abs(fft(signal))
        features['频谱均值'] = float(np.mean(fft_vals))
        return features
    except:
        return {"均值": 0, "有效值": 0, "峰值": 0, "峭度": 3, "峰值因子": 0, "频谱均值": 0}

def kg_reasoning(features, kg):
    try:
        k = features['峭度']
        c = features['峰值因子']
        if k > 4:
            if c > 3:
                return "内圈故障", "安装偏心", "重新校准安装、更换轴承"
            else:
                return "外圈/滚动体故障", "润滑不足、过载", "补充润滑、检查负载"
        elif c > 3:
            return "内圈早期故障", "安装精度不足", "重新校准"
    except:
        pass
    return "正常", "", "正常运行"

def llm_diagnose(features, fault):
    try:
        from openai import OpenAI
        client = OpenAI(api_key=st.session_state.get("llm_key", "none"), base_url="https://api.openai.com/v1")
        prompt = f"""你是轴承故障专家，诊断：{features}，类型：{fault}"""
        res = client.chat.completions.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt}], temperature=0.1)
        return res.choices[0].message.content
    except:
        return f"""
**📌 诊断结果（KG 规则）**
1. 故障类型：{fault}
2. 根因：特征异常
3. 建议：检查设备状态
4. 预防：定期维护"""

def plot_kg(kg):
    try:
        net = Network(height="500px", width="100%", bgcolor="#222222", font_color="white")
        colors = {"故障模式": "red", "特征": "blue", "状态": "green", "根因": "orange", "解决方案": "purple"}
        for e in kg['entities']:
            net.add_node(e['id'], label=e['name'], color=colors.get(e['type'], "gray"))
        for r in kg['relations']:
            net.add_edge(r['source'], r['target'], label=r['relation'], color="white")
        tmp = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.html', encoding='utf-8')
        net.write_html(tmp.name)
        return tmp.name
    except:
        return ""





try:
    if os.path.exists(RECORD_PATH) and os.path.getsize(RECORD_PATH) > 0:
        with open(RECORD_PATH, 'r', encoding='utf-8') as f:
            records = json.load(f)
        if not records:
            st.info("暂无记录")
        else:
            for r in reversed(records):
                with st.expander(r['time']):
                    st.write("特征：", r['features'])
                    st.write("故障：", r['kg_fault'])
                    st.write("诊断：", r['llm_result'])
    else:
        st.info("暂无记录")
except:
    st.info("暂无记录")