from constants import env
from utils.utils import convert_pkl_to_data
from utils.minio import client as mc
from utils.minio import buckets as mc_buckets

import keras
import numpy as np


def model_evaluate():
    # 連接 MinIO Server 並建立 Bucket
    minioClient = mc.connect_minio()

    # 從 MinIO 取得訓練後的模型資料，並轉換回 keras 模型
    mc_buckets.get_file_from_bucket(
        client=minioClient,
        bucket_name=env.MNIST_TRAINING_MODEL_BUCKET_NAME,
        object_name=env.TRAINED_MODEL_KERAS_FILENAME,
        file_path=env.TRAINED_MODEL_KERAS_FILE_PATH
    )
    model = keras.models.load_model(env.TRAINED_MODEL_KERAS_FILE_PATH)

    # 從 MinIO 取得測試資料集
    mc_buckets.get_file_from_bucket(
        client=minioClient,
        bucket_name=env.MNIST_NORMALIZE_BUCKET_NAME,
        object_name=env.X_TEST4D_NORMALIZE_PKL_FILENAME,
        file_path=env.X_TEST4D_NORMALIZE_FILE_PATH
    )
    X_Test4D_normalize = convert_pkl_to_data(env.X_TEST4D_NORMALIZE_FILE_PATH)
    mc_buckets.get_file_from_bucket(
        client=minioClient,
        bucket_name=env.MNIST_ONEHOT_ENCODING_BUCKET_NAME,
        object_name=env.Y_TEST_ONE_HOT_ENCODING_PKL_FILENAME,
        file_path=env.Y_TEST_ONE_HOT_ENCODING_FILE_PATH
    )
    y_TestOneHot = convert_pkl_to_data(env.Y_TEST_ONE_HOT_ENCODING_FILE_PATH)

    # 評估模型
    evaluate_model(model, X_Test4D_normalize, y_TestOneHot)

    # 預測模型
    prediction_model(model, X_Test4D_normalize)


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
