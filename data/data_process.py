import os
import json
import numpy as np
import pandas as pd
import scipy.io as sio
from scipy.fft import fft
from sklearn.preprocessing import StandardScaler

# ====================== 配置 ======================
DATA_PATH = "./CWRU/"
FILE_LABEL_MAP = {
    "97.mat": "正常",
    "105.mat": "内圈故障",
    "118.mat": "滚珠故障",
    "130.mat": "外圈故障"
}


# ====================== 读取CWRU数据（稳定版） ======================
def load_cwru_mat(filepath, label):
    data = sio.loadmat(filepath)
    vibration = None
    for k in data.keys():
        if "DE_time" in k:
            vibration = data[k].reshape(-1)
            break
    if vibration is None:
        raise ValueError("未找到振动数据")

    sample_freq = 12000
    df = pd.DataFrame({
        "timestamp": np.arange(len(vibration)) / sample_freq,
        "vibration": vibration,
        "label": label,
        "bearing_model": "SKF 6205-2RS JEM",
        "rpm": 1797
    })
    return df


# ====================== 数据清洗（无警告版） ======================
def clean_data(df):
    # 复制一份 → 彻底消除 Pandas 警告
    df = df.copy()

    # 3σ 去异常
    sigma = df["vibration"].std()
    mean = df["vibration"].mean()
    df = df[(df["vibration"] >= mean - 3 * sigma) &
            (df["vibration"] <= mean + 3 * sigma)]

    # 标准化
    scaler = StandardScaler()
    df.loc[:, "vibration_norm"] = scaler.fit_transform(df["vibration"].values.reshape(-1, 1))
    return df, scaler


# ====================== 特征提取 ======================
def extract_features(vibration, sample_freq=12000):
    abs_mean = np.mean(np.abs(vibration))
    rms = np.sqrt(np.mean(vibration ** 2))
    peak = np.max(np.abs(vibration))
    kurtosis = np.mean((vibration - np.mean(vibration)) ** 4) / (np.std(vibration) ** 4)
    crest = peak / rms
    fft_vib = np.abs(fft(vibration))
    freq_centroid = np.sum(fft_vib * np.arange(len(fft_vib))) / np.sum(fft_vib)

    return {
        "abs_mean": abs_mean,
        "rms": rms,
        "peak": peak,
        "kurtosis": kurtosis,
        "crest_factor": crest,
        "freq_centroid": freq_centroid
    }


# ====================== 批量处理 ======================
if not os.path.exists("./output"):
    os.mkdir("./output")

all_structured = []

for filename, label in FILE_LABEL_MAP.items():
    print(f"正在处理：{filename} -> {label}")
    file_path = os.path.join(DATA_PATH, filename)

    df = load_cwru_mat(file_path, label)
    df_clean, _ = clean_data(df)
    feats = extract_features(df_clean["vibration_norm"].values)

    struct = {
        "file": filename,
        "bearing_model": "SKF 6205",
        "rpm": 1797,
        "fault_type": label,
        **feats
    }
    all_structured.append(struct)

# 保存结构化数据为JSON格式（替换原CSV保存逻辑）
with open("./output/cwru_structured_metadata.json", "w", encoding="utf-8") as f:
    # 确保浮点数正常序列化，中文正常显示
    json.dump(all_structured, f, ensure_ascii=False, indent=4)

print("\n✅ 数据处理完成！无警告无错误！")
# 仍打印DataFrame便于查看结果
df_final = pd.DataFrame(all_structured)
print(df_final)