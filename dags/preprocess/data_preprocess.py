import os
import pickle
from keras.utils import to_categorical
from minio import Minio, S3Error
import numpy as np

# ===== Constants =====

MINIO_API_ENDPOINT = os.environ["MINIO_API_ENDPOINT"]  # 10.20.1.229:9000
MINIO_ACCESS_KEY = os.environ["MINIO_ACCESS_KEY"]  # minioadmin
MINIO_SECRET_KEY = os.environ["MINIO_SECRET_KEY"]  # minioadmin

MNIST_DATASETS_BUCKET_NAME = "mnist-datasets"
MNIST_NORMALIZE_BUCKET_NAME = "mnist-normalize"
MNIST_ONEHOT_ENCODING_BUCKET_NAME = "mnist-onehot-encoding"

MNIST_DATASETS_FILENAME = "mnist.npz"

X_TRAIN4D_NORMALIZE_PKL_FILENAME = "X_Train4D_normalize.pkl"
X_TEST4D_NORMALIZE_PKL_FILENAME = "X_Test4D_normalize.pkl"
Y_TRAIN_ONE_HOT_ENCODING_PKL_FILENAME = "y_Train_One_Hot_Encoding.pkl"
Y_TEST_ONE_HOT_ENCODING_PKL_FILENAME = "y_TestOneHot.pkl"

MNIST_PARENT_DIR = "/src"
MNIST_DATASETS_DIR = f"/src/datasets"

MNIST_DATASETS_FILE_PATH = f"/src/{MNIST_DATASETS_FILENAME}"
X_TRAIN4D_NORMALIZE_FILE_PATH = f"/src/{X_TRAIN4D_NORMALIZE_PKL_FILENAME}"
X_TEST4D_NORMALIZE_FILE_PATH = f"/src/{X_TEST4D_NORMALIZE_PKL_FILENAME}"
Y_TRAIN_ONE_HOT_ENCODING_FILE_PATH = f"/src/{Y_TRAIN_ONE_HOT_ENCODING_PKL_FILENAME}"
Y_TEST_ONE_HOT_ENCODING_FILE_PATH = f"/src/{Y_TEST_ONE_HOT_ENCODING_PKL_FILENAME}"


def model_data_preprocess():
    # 連接 MinIO Server 並建立 Bucket
    minio_client = connect_minio()

    is_datasets_exists = object_exists(
        client=minio_client,
        bucket_name=MNIST_DATASETS_BUCKET_NAME,
        object_name=MNIST_DATASETS_FILENAME
    )

    if is_datasets_exists:
        print("MNIST datasets exists.")
        get_file_from_bucket(
            client=minio_client,
            bucket_name=MNIST_DATASETS_BUCKET_NAME,
            object_name=MNIST_DATASETS_FILENAME,
            file_path=MNIST_DATASETS_FILE_PATH
        )

    # 進行資料預處理
    X_Train4D_normalize, X_Test4D_normalize, y_TrainOneHot, y_TestOneHot = data_preprocess()

    # 將資料儲存成 pkl 檔案
    write_file(X_TRAIN4D_NORMALIZE_FILE_PATH, X_Train4D_normalize)
    write_file(X_TEST4D_NORMALIZE_FILE_PATH, X_Test4D_normalize)
    write_file(Y_TRAIN_ONE_HOT_ENCODING_FILE_PATH, y_TrainOneHot)
    write_file(Y_TEST_ONE_HOT_ENCODING_FILE_PATH, y_TestOneHot)

    # 將檔案儲存 MinIO Bucket
    # normalize
    upload_file_to_bucket(
        client=minio_client,
        bucket_name=MNIST_NORMALIZE_BUCKET_NAME,
        object_name=X_TRAIN4D_NORMALIZE_PKL_FILENAME,
        file_path=X_TRAIN4D_NORMALIZE_FILE_PATH
    )
    upload_file_to_bucket(
        client=minio_client,
        bucket_name=MNIST_NORMALIZE_BUCKET_NAME,
        object_name=X_TEST4D_NORMALIZE_PKL_FILENAME,
        file_path=X_TEST4D_NORMALIZE_FILE_PATH
    )
    # onehot encoding
    upload_file_to_bucket(
        client=minio_client,
        bucket_name=MNIST_ONEHOT_ENCODING_BUCKET_NAME,
        object_name=Y_TRAIN_ONE_HOT_ENCODING_PKL_FILENAME,
        file_path=Y_TRAIN_ONE_HOT_ENCODING_FILE_PATH
    )
    upload_file_to_bucket(
        client=minio_client,
        bucket_name=MNIST_ONEHOT_ENCODING_BUCKET_NAME,
        object_name=Y_TEST_ONE_HOT_ENCODING_PKL_FILENAME,
        file_path=Y_TEST_ONE_HOT_ENCODING_FILE_PATH
    )


def data_preprocess():
    """資料預處理"""

    np.random.seed(10)

    # 讀取 MNIST 資料集
    with np.load(MNIST_DATASETS_FILE_PATH) as f:
        X_train, y_train = f['x_train'], f['y_train']
        X_test, y_test = f['x_test'], f['y_test']

    # 資料轉換
    X_Train4D = X_train.reshape(X_train.shape[0], 28, 28, 1).astype('float32')
    X_Test4D = X_test.reshape(X_test.shape[0], 28, 28, 1).astype('float32')

    # 資料標準化
    X_Train4D_normalize, X_Test4D_normalize = data_normalize(
        X_Train4D, X_Test4D)

    # Label OneHot Encoding
    y_TrainOneHot, y_TestOneHot = data_one_hot_encoding(y_train, y_test)

    return X_Train4D_normalize, X_Test4D_normalize, y_TrainOneHot, y_TestOneHot


def data_normalize(X_Train4D, X_Test4D):
    """資料標準化

    Args:
        X_Train4D (numpy.ndarray): 訓練資料
        X_Test4D (numpy.ndarray): 測試資料
    """

    X_Train4D_normalize = X_Train4D / 255
    X_Test4D_normalize = X_Test4D / 255

    return X_Train4D_normalize, X_Test4D_normalize


def data_one_hot_encoding(y_train, y_test):
    """Label OneHot Encoding

    Args:
        y_train (numpy.ndarray): 訓練資料標籤
        y_test (numpy.ndarray): 測試資料標籤
    """

    y_TrainOneHot = to_categorical(y_train)
    y_TestOneHot = to_categorical(y_test)

    return y_TrainOneHot, y_TestOneHot


# ===== Utils =====


def write_file(filename: str, data):
    """將模型資料寫入檔案

    Args:
        filename (str): 檔案名稱
        data: 要寫入的資料
    """

    with open(filename, 'wb') as f:
        pickle.dump(data, f)


def connect_minio():
    """連接 MinIO Server"""

    return Minio(
        endpoint=MINIO_API_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=False
    )


def create_buckets(client: Minio, bucket_names: list):
    """建立 MinIO Bucket

    Args:
        client (Minio): Minio Client instance
        bucket_names (list): 要建立的 MinIO Bucket 名稱
    """

    print(f"bucket_names: {bucket_names}")
    for name in bucket_names:
        if client.bucket_exists(name):
            print(f"Bucket {name} already exists")
        else:
            client.make_bucket(name)
            print(f"Bucket {name} created")


def get_file_from_bucket(
    client: Minio,
    bucket_name: str,
    object_name: str,
    file_path: str
):
    """取得 MinIO Bucket 內的資料

    Args:
        client (Minio): MinIO Client instance
        bucket_name (str): MinIO Bucket 名稱
        object_name (str): 要取得的 object 名稱
        file_path (str): 下載後的檔案路徑
    """

    client.fget_object(bucket_name, object_name, file_path)


def upload_file_to_bucket(
    client: Minio,
    bucket_name: str,
    object_name: str,
    file_path: str
):
    """上傳資料到 MinIO Bucket 內

    Args:
        client (Minio): MinIO Client instance
        bucket_name (str): MinIO Bucket 名稱
        object_name (str): 要上傳到 MinIO Bucket 的 object 名稱
        filename (object): 要上傳到 MinIO Bucket 的檔案名稱
    """

    try:
        client.fput_object(
            bucket_name=bucket_name,
            object_name=object_name,
            file_path=file_path
        )
    except S3Error as err:
        print(
            f"upload file {file_path} to minio bucket {bucket_name} occurs error. Error: {err}"
        )


def object_exists(
    client: Minio,
    bucket_name: str,
    object_name: str
):
    """確認 MinIO Bucket 內是否存在指定的 object

    Args:
        client (Minio): MinIO Client instance
        bucket_name (str): MinIO Bucket 名稱
        object_name (str): 要確認是否存在於 MinIO Bucket 的 object 名稱
    """

    try:
        client.stat_object(bucket_name=bucket_name, object_name=object_name)
        return True
    except:
        return False


# ===== Main =====


if __name__ == "__main__":
    model_data_preprocess()
