from config import env
from utils.utils import write_file
from utils.minio import client as mc
from utils.minio import buckets as mc_buckets

import numpy as np
from keras.utils import to_categorical, get_file


def model_data_preprocess():
    # 連接 MinIO Server 並建立 Bucket
    minioClient = mc.connect_minio()
    bucket_names = [
        env.MNIST_DATASETS_BUCKET_NAME,
        env.MNIST_NORMALIZE_BUCKET_NAME,
        env.MNIST_ONEHOT_ENCODING_BUCKET_NAME
    ]
    mc_buckets.create_buckets(minioClient, bucket_names)

    is_datasets_exists = mc_buckets.object_exists(
        client=minioClient,
        bucket_name=env.MNIST_DATASETS_BUCKET_NAME,
        object_name=env.MNIST_DATASETS_FILENAME
    )

    if is_datasets_exists:
        print("MNIST datasets exists.")
        mc_buckets.get_file_from_bucket(
            client=minioClient,
            bucket_name=env.MNIST_DATASETS_BUCKET_NAME,
            object_name=env.MNIST_DATASETS_FILENAME,
            file_path=env.MNIST_DATASETS_FILE_PATH
        )
    else:
        print("MNIST datasets doesn't exist. download...")
        # 從 MinIO 下載 MNIST 資料集
        # https://storage.googleapis.com/tensorflow/tf-keras-datasets/mnist.npz
        path = get_file(
            fname=env.MNIST_DATASETS_FILENAME,
            origin='https://storage.googleapis.com/tensorflow/tf-keras-datasets/mnist.npz',
            file_hash="731c5ac602752760c8e48fbffcf8c3b850d9dc2a2aedcf2cc48468fc17b673d1",
            cache_dir=env.MNIST_PARENT_DIR,
            cache_subdir=env.MNIST_DATASETS_DIR
        )
        mc_buckets.upload_file_to_bucket(
            client=minioClient,
            bucket_name=env.MNIST_DATASETS_BUCKET_NAME,
            object_name=env.MNIST_DATASETS_FILENAME,
            file_path=path
        )

    # 進行資料預處理
    X_Train4D_normalize, X_Test4D_normalize, y_TrainOneHot, y_TestOneHot = data_preprocess()

    # 將資料儲存成 pkl 檔案
    write_file(env.X_TRAIN4D_NORMALIZE_FILE_PATH, X_Train4D_normalize)
    write_file(env.X_TEST4D_NORMALIZE_FILE_PATH, X_Test4D_normalize)
    write_file(env.Y_TRAIN_ONE_HOT_ENCODING_FILE_PATH, y_TrainOneHot)
    write_file(env.Y_TEST_ONE_HOT_ENCODING_FILE_PATH, y_TestOneHot)

    # 將檔案儲存 MinIO Bucket
    # normalize
    mc_buckets.upload_file_to_bucket(
        client=minioClient,
        bucket_name=env.MNIST_NORMALIZE_BUCKET_NAME,
        object_name=env.X_TRAIN4D_NORMALIZE_PKL_FILENAME,
        file_path=env.X_TRAIN4D_NORMALIZE_FILE_PATH
    )
    mc_buckets.upload_file_to_bucket(
        client=minioClient,
        bucket_name=env.MNIST_NORMALIZE_BUCKET_NAME,
        object_name=env.X_TEST4D_NORMALIZE_PKL_FILENAME,
        file_path=env.X_TEST4D_NORMALIZE_FILE_PATH
    )
    # onehot encoding
    mc_buckets.upload_file_to_bucket(
        client=minioClient,
        bucket_name=env.MNIST_ONEHOT_ENCODING_BUCKET_NAME,
        object_name=env.Y_TRAIN_ONE_HOT_ENCODING_PKL_FILENAME,
        file_path=env.Y_TRAIN_ONE_HOT_ENCODING_FILE_PATH
    )
    mc_buckets.upload_file_to_bucket(
        client=minioClient,
        bucket_name=env.MNIST_ONEHOT_ENCODING_BUCKET_NAME,
        object_name=env.Y_TEST_ONE_HOT_ENCODING_PKL_FILENAME,
        file_path=env.Y_TEST_ONE_HOT_ENCODING_FILE_PATH
    )


def data_preprocess():
    """資料預處理"""

    np.random.seed(10)

    # 讀取 MNIST 資料集
    with np.load(env.MNIST_DATASETS_FILE_PATH) as f:
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


if __name__ == "__main__":
    model_data_preprocess()
