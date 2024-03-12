import os
import pickle


def mkdir(dir: str):
    """建立資料夾

    Args:
        dir (str): 資料夾路徑
    """

    if not os.path.exists(dir):
        os.mkdir(dir)
        print(f"Directory {dir} created success")


def write_file(filename: str, data):
    """將模型資料寫入檔案

    Args:
        filename (str): 檔案名稱
        data: 要寫入的資料
    """

    with open(filename, 'wb') as f:
        pickle.dump(data, f)


def convert_pkl_to_data(filename: str):
    """將 pkl 檔案轉換回原始資料

    Args:
        filename (str): pkl 檔案名稱
    """

    with open(filename, 'rb') as f:
        data = pickle.load(f)
    return data
