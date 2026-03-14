"""
这个 py 文件用于从 url 上下载数据
"""

import requests

def download_data(url, save_path):
    # 下载并保存
    response = requests.get(url, timeout=30)
    with open(save_path, "wb") as f:
        f.write(response.content)
    print(f"✅ 已保存为：{save_path}")

if __name__ == "__main__":
    data_source = [
        {'url': 'https://engineering.case.edu/sites/default/files/97.mat', 'name': './CWRU/97.mat'},
        {'url': 'https://engineering.case.edu/sites/default/files/105.mat', 'name': './CWRU/105.mat'},
        {'url': 'https://engineering.case.edu/sites/default/files/118.mat', 'name': './CWRU/118.mat'},
        {'url': 'https://engineering.case.edu/sites/default/files/130.mat', 'name': './CWRU/130.mat'},
    ]

    for index, value in enumerate(data_source):
        url = value['url']
        save_path = value['name']
        download_data(url, save_path)