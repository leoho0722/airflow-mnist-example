import os
import pickle

from keras.models import load_model
from minio import Minio
import numpy as np

# ===== Constants =====

MINIO_API_ENDPOINT = os.environ["MINIO_API_ENDPOINT"]  # 10.20.1.229:9000
MINIO_ACCESS_KEY = os.environ["MINIO_ACCESS_KEY"]  # minioadmin
MINIO_SECRET_KEY = os.environ["MINIO_SECRET_KEY"]  # minioadmin

MNIST_NORMALIZE_BUCKET_NAME = "mnist-normalize"
MNIST_ONEHOT_ENCODING_BUCKET_NAME = "mnist-onehot-encoding"
MNIST_TRAINING_MODEL_BUCKET_NAME = "mnist-training-model"

X_TEST4D_NORMALIZE_PKL_FILENAME = "X_Test4D_normalize.pkl"
Y_TEST_ONE_HOT_ENCODING_PKL_FILENAME = "y_TestOneHot.pkl"

TRAINED_MODEL_KERAS_FILENAME = "trained_model.keras"

X_TEST4D_NORMALIZE_FILE_PATH = f"/src/{X_TEST4D_NORMALIZE_PKL_FILENAME}"
Y_TEST_ONE_HOT_ENCODING_FILE_PATH = f"/src/{Y_TEST_ONE_HOT_ENCODING_PKL_FILENAME}"
TRAINED_MODEL_KERAS_FILE_PATH = f"/src/{TRAINED_MODEL_KERAS_FILENAME}"


def model_evaluate():
    # 連接 MinIO Server 並建立 Bucket
    minio_client = connect_minio()

    # 從 MinIO 取得訓練後的模型資料，並轉換回 keras 模型
    get_file_from_bucket(
        client=minio_client,
        bucket_name=MNIST_TRAINING_MODEL_BUCKET_NAME,
        object_name=TRAINED_MODEL_KERAS_FILENAME,
        file_path=TRAINED_MODEL_KERAS_FILE_PATH
    )
    os.system("ls -al")
    model = load_model(TRAINED_MODEL_KERAS_FILE_PATH)

    # 從 MinIO 取得測試資料集
    get_file_from_bucket(
        client=minio_client,
        bucket_name=MNIST_NORMALIZE_BUCKET_NAME,
        object_name=X_TEST4D_NORMALIZE_PKL_FILENAME,
        file_path=X_TEST4D_NORMALIZE_FILE_PATH
    )
    X_Test4D_normalize = convert_pkl_to_data(
        filename=X_TEST4D_NORMALIZE_FILE_PATH
    )
    get_file_from_bucket(
        client=minio_client,
        bucket_name=MNIST_ONEHOT_ENCODING_BUCKET_NAME,
        object_name=Y_TEST_ONE_HOT_ENCODING_PKL_FILENAME,
        file_path=Y_TEST_ONE_HOT_ENCODING_FILE_PATH
    )
    y_TestOneHot = convert_pkl_to_data(
        filename=Y_TEST_ONE_HOT_ENCODING_FILE_PATH
    )

    # 評估模型
    evaluate_model(
        model=model,
        test_data=X_Test4D_normalize,
        test_label=y_TestOneHot
    )

    # 預測模型
    prediction_model(model=model, test_data=X_Test4D_normalize)


def evaluate_model(model, test_data, test_label):
    """評估模型

    Args:
        model (keras.models.Sequential): 訓練後的模型
        test_data: 標準化後的測試資料
        test_label: 標準化後的 onehot encoding 測試資料
    """

    scores = model.evaluate(test_data, test_label)
    print()
    print("\t[Info] Accuracy of testing data = {:2.1f}%".format(
        scores[1]*100.0))


def prediction_model(model, test_data):
    """預測模型

    Args:
        model (keras.models.Sequential): 訓練後的模型
        test_data: 標準化後的測試資料
    """

    print("\t[Info] Making prediction of X_Test4D_norm")
    # Making prediction and save result to prediction
    predict_x = model.predict(test_data)
    classes_x = np.argmax(predict_x, axis=1)
    print()
    print("\t[Info] Show 10 prediction result (From 240):")
    print("%s\n" % (classes_x[240:250]))


# ===== Utils =====


def convert_pkl_to_data(filename: str):
    """將 pkl 檔案轉換回原始資料

    Args:
        filename (str): pkl 檔案名稱
    """

    with open(filename, 'rb') as f:
        data = pickle.load(f)
    return data


def connect_minio():
    """連接 MinIO Server"""

    return Minio(
        endpoint=MINIO_API_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=False
    )


def get_all_files_from_bucket(
    client: Minio,
    bucket_name: str,
    dir_path: str
):
    """取得 MinIO Bucket 內的所有資料

    Args:
        client (Minio): MinIO Client instance
        bucket_name (str): MinIO Bucket 名稱
        dir_path (str): 下載後的資料夾路徑
    """

    objects = client.list_objects(bucket_name, recursive=True)
    for obj in objects:
        file_path = f"{dir_path}/{obj.object_name}"
        get_file_from_bucket(
            client=client,
            bucket_name=bucket_name,
            object_name=obj.object_name,  # type: ignore
            file_path=file_path
        )


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


# ===== Main =====


if __name__ == "__main__":
    model_evaluate()
