from constants import env
from utils.utils import convert_pkl_to_data
from utils.minio import client as mc
from utils.minio import buckets as mc_buckets

from keras.layers import Conv2D, Dense, Dropout, Flatten, MaxPool2D
from keras.models import Sequential


def model_training():
    # 連接 MinIO Server 並建立 Bucket
    minioClient = mc.connect_minio()
    bucket_names = [
        env.MNIST_NORMALIZE_BUCKET_NAME,
        env.MNIST_ONEHOT_ENCODING_BUCKET_NAME,
        env.MNIST_TRAINING_MODEL_BUCKET_NAME
    ]
    mc_buckets.create_buckets(minioClient, bucket_names)

    # 從 MinIO 取得預處理的資料
    mc_buckets.get_file_from_bucket(
        client=minioClient,
        bucket_name=env.MNIST_NORMALIZE_BUCKET_NAME,
        object_name=env.X_TRAIN4D_NORMALIZE_PKL_FILENAME,
        file_path=env.X_TRAIN4D_NORMALIZE_FILE_PATH
    )
    X_Train4D_normalize = convert_pkl_to_data(
        env.X_TRAIN4D_NORMALIZE_FILE_PATH
    )
    mc_buckets.get_file_from_bucket(
        client=minioClient,
        bucket_name=env.MNIST_ONEHOT_ENCODING_BUCKET_NAME,
        object_name=env.Y_TRAIN_ONE_HOT_ENCODING_PKL_FILENAME,
        file_path=env.Y_TRAIN_ONE_HOT_ENCODING_FILE_PATH
    )
    y_TrainOneHot = convert_pkl_to_data(env.Y_TRAIN_ONE_HOT_ENCODING_FILE_PATH)

    # 建立模型
    model = model_build()

    # 訓練模型
    trained_model, _ = training_model(model=model,
                                      normalize_data=X_Train4D_normalize,
                                      onehot_data=y_TrainOneHot)

    # 將訓練後的模型資料儲存到 MinIO Bucket
    save_trained_model(trained_model, env.TRAINED_MODEL_KERAS_FILE_PATH)
    mc_buckets.upload_file_to_bucket(
        client=minioClient,
        bucket_name=env.MNIST_TRAINING_MODEL_BUCKET_NAME,
        object_name=env.TRAINED_MODEL_KERAS_FILENAME,
        file_path=env.TRAINED_MODEL_KERAS_FILE_PATH
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
    train_result = model.fit(x=normalize_data,
                             y=onehot_data,
                             validation_split=0.2,
                             epochs=10,
                             batch_size=300,
                             verbose=1)

    return model, train_result


def save_trained_model(model, filename: str):
    """儲存訓練好的模型

    Args:
        model (keras.models.Sequential): keras.models.Sequential
        filename (str): 訓練好的模型檔名
    """

    model.save(filename)
