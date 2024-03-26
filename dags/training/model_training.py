import os
import pickle
from keras.layers import Conv2D, Dense, Dropout, Flatten, MaxPool2D
from keras.models import Sequential
from minio import Minio, S3Error
import tensorflow as tf

# ===== Constants =====

MINIO_API_ENDPOINT = os.environ["MINIO_API_ENDPOINT"]  # 10.20.1.229:9000
MINIO_ACCESS_KEY = os.environ["MINIO_ACCESS_KEY"]  # minioadmin
MINIO_SECRET_KEY = os.environ["MINIO_SECRET_KEY"]  # minioadmin

MNIST_NORMALIZE_BUCKET_NAME = "mnist-normalize"
MNIST_ONEHOT_ENCODING_BUCKET_NAME = "mnist-onehot-encoding"
MNIST_TRAINING_MODEL_BUCKET_NAME = "mnist-training-model"

X_TRAIN4D_NORMALIZE_PKL_FILENAME = "X_Train4D_normalize.pkl"
Y_TRAIN_ONE_HOT_ENCODING_PKL_FILENAME = "y_Train_One_Hot_Encoding.pkl"
Y_TEST_ONE_HOT_ENCODING_PKL_FILENAME = "y_TestOneHot.pkl"

TRAINED_MODEL_KERAS_FILENAME = "trained_model.keras"

X_TRAIN4D_NORMALIZE_FILE_PATH = f"/src/{X_TRAIN4D_NORMALIZE_PKL_FILENAME}"
Y_TRAIN_ONE_HOT_ENCODING_FILE_PATH = f"/src/{Y_TRAIN_ONE_HOT_ENCODING_PKL_FILENAME}"
Y_TEST_ONE_HOT_ENCODING_FILE_PATH = f"/src/{Y_TEST_ONE_HOT_ENCODING_PKL_FILENAME}"
TRAINED_MODEL_KERAS_FILE_PATH = f"/src/{TRAINED_MODEL_KERAS_FILENAME}"


def check_gpu():
    """檢查是否有 GPU 可用"""

    physical_devices = tf.config.experimental.list_physical_devices('GPU')
    if len(physical_devices) == 0:
        print("Not enough GPU hardware devices available")

    print(f"Found {len(physical_devices)} GPU hardware devices available")
    print(f"GPU model: {tf.test.gpu_device_name()}")


def model_training():
    # 連接 MinIO Server 並建立 Bucket
    minio_client = connect_minio()

    # 從 MinIO 取得預處理的資料
    get_file_from_bucket(
        client=minio_client,
        bucket_name=MNIST_NORMALIZE_BUCKET_NAME,
        object_name=X_TRAIN4D_NORMALIZE_PKL_FILENAME,
        file_path=X_TRAIN4D_NORMALIZE_FILE_PATH
    )
    X_Train4D_normalize = convert_pkl_to_data(
        X_TRAIN4D_NORMALIZE_FILE_PATH
    )
    get_file_from_bucket(
        client=minio_client,
        bucket_name=MNIST_ONEHOT_ENCODING_BUCKET_NAME,
        object_name=Y_TRAIN_ONE_HOT_ENCODING_PKL_FILENAME,
        file_path=Y_TRAIN_ONE_HOT_ENCODING_FILE_PATH
    )
    y_TrainOneHot = convert_pkl_to_data(
        filename=Y_TRAIN_ONE_HOT_ENCODING_FILE_PATH
    )

    # 建立模型
    model = model_build()

    # 訓練模型
    trained_model, _ = training_model(
        model=model,
        normalize_data=X_Train4D_normalize,
        onehot_data=y_TrainOneHot
    )

    # 將訓練後的模型資料儲存到 MinIO Bucket
    save_trained_model(
        model=trained_model,
        filename=TRAINED_MODEL_KERAS_FILE_PATH
    )
    upload_file_to_bucket(
        client=minio_client,
        bucket_name=MNIST_TRAINING_MODEL_BUCKET_NAME,
        object_name=TRAINED_MODEL_KERAS_FILENAME,
        file_path=TRAINED_MODEL_KERAS_FILE_PATH
    )


def model_build():
    """建立模型"""

    model = Sequential()
    create_cn_layer_and_pool_layer(model)
    create_flatten_layer_and_hidden_layer(model)
    model_summary(model)

    return model


def create_cn_layer_and_pool_layer(model):
    """建立卷積層與池化層

    Args:
        model (keras.models.Sequential): keras.models.Sequential
    """

    # Create CN layer 1
    model.add(Conv2D(filters=16,
                     kernel_size=(5, 5),
                     padding='same',
                     input_shape=(28, 28, 1),
                     activation='relu',
                     name='conv2d_1'))
    # Create Max-Pool 1
    model.add(MaxPool2D(pool_size=(2, 2), name='max_pooling2d_1'))

    # Create CN layer 2
    model.add(Conv2D(filters=36,
                     kernel_size=(5, 5),
                     padding='same',
                     input_shape=(28, 28, 1),
                     activation='relu',
                     name='conv2d_2'))

    # Create Max-Pool 2
    model.add(MaxPool2D(pool_size=(2, 2), name='max_pooling2d_2'))

    # Add Dropout layer
    model.add(Dropout(0.25, name='dropout_1'))


def create_flatten_layer_and_hidden_layer(model):
    """建立平坦層與隱藏層

    Args:
        model (keras.models.Sequential): keras.models.Sequential
    """

    # Create Flatten layer
    model.add(Flatten(name='flatten_1'))

    # Create Hidden layer
    model.add(Dense(128, activation='relu', name='dense_1'))
    model.add(Dropout(0.5, name='dropout_2'))

    # Create Output layer
    model.add(Dense(10, activation='softmax', name='dense_2'))


def model_summary(model):
    """顯示模型摘要

    Args:
        model (keras.models.Sequential): keras.models.Sequential
    """

    model.summary()
    print("Model is built successfully!")


def training_model(model, normalize_data, onehot_data):
    """訓練模型

    Args:
        model (keras.models.Sequential): keras.models.Sequential
        normalize_data (numpy.ndarray): 標準化後的訓練資料
        onehot_data (numpy.ndarray): onehot encoding 後的訓練資料
    """

    # 定義訓練方式
    model.compile(loss='categorical_crossentropy',
                  optimizer='adam',
                  metrics=['accuracy'])

    # 開始訓練
    training_epochs = os.environ["TRAINING_EPOCHS"]  # 10
    train_result = model.fit(
        x=normalize_data,
        y=onehot_data,
        validation_split=0.2,
        epochs=int(training_epochs),
        batch_size=300,
        verbose=1
    )

    return model, train_result


def save_trained_model(model, filename: str):
    """儲存訓練好的模型

    Args:
        model (keras.models.Sequential): keras.models.Sequential
        filename (str): 訓練好的模型檔名
    """

    model.save(filename)


# ===== Utils =====


def convert_pkl_to_data(filename: str):
    """將 pkl 檔案轉換回原始資料

    Args:
        filename (str): pkl 檔案名稱
    """

    with open(filename, 'rb') as f:
        data = pickle.load(f)
    return data


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

    client.fget_object(
        bucket_name=bucket_name,
        object_name=object_name,
        file_path=file_path
    )


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
    check_gpu()
    model_training()
