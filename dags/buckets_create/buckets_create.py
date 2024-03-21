from keras.utils import get_file
from minio import Minio


# ===== Constants =====

MINIO_API_ENDPOINT = "10.20.1.229:9000"
MINIO_ACCESS_KEY = "minioadmin"
MINIO_SECRET_KEY = "minioadmin"

MNIST_DATASETS_BUCKET_NAME = "mnist-datasets"
MNIST_NORMALIZE_BUCKET_NAME = "mnist-normalize"
MNIST_ONEHOT_ENCODING_BUCKET_NAME = "mnist-onehot-encoding"
MNIST_TRAINING_MODEL_BUCKET_NAME = "mnist-training-model"

MNIST_DATASETS_FILENAME = "mnist.npz"

MNIST_PARENT_DIR = "/src"
MNIST_DATASETS_DIR = f"/src/datasets"

MNIST_DATASETS_FILE_PATH = f"/src/{MNIST_DATASETS_FILENAME}"


def download_mnist_datasets(client: Minio):
    """下載 MNIST 資料集

    Args:
        client (Minio): MinIO Client instance
    """

    is_datasets_exists = object_exists(
        client=client,
        bucket_name=MNIST_DATASETS_BUCKET_NAME,
        object_name=MNIST_DATASETS_FILENAME
    )

    if not is_datasets_exists:
        print("MNIST datasets doesn't exist. download...")
        # 從 MinIO 下載 MNIST 資料集
        # https://storage.googleapis.com/tensorflow/tf-keras-datasets/mnist.npz
        path = get_file(
            fname=MNIST_DATASETS_FILENAME,
            origin='https://storage.googleapis.com/tensorflow/tf-keras-datasets/mnist.npz',
            file_hash="731c5ac602752760c8e48fbffcf8c3b850d9dc2a2aedcf2cc48468fc17b673d1",
            cache_dir=MNIST_PARENT_DIR,
            cache_subdir=MNIST_DATASETS_DIR
        )
        upload_file_to_bucket(
            client=client,
            bucket_name=MNIST_DATASETS_BUCKET_NAME,
            object_name=MNIST_DATASETS_FILENAME,
            file_path=path
        )
    else:
        print("MNIST datasets exists. Skip download.")


def connect_minio():
    """連接 MinIO Server"""

    return Minio(
        endpoint=MINIO_API_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=False
    )


def create_buckets(client: Minio, buckets: list):
    """建立 MinIO Bucket

    Args:
        client (Minio): Minio Client instance
        buckets (list): 要建立的 MinIO Bucket 名稱
    """

    print(f"bucket_names: {buckets}")
    for name in buckets:
        if client.bucket_exists(name):
            print(f"Bucket {name} already exists")
        else:
            client.make_bucket(name)
            print(f"Bucket {name} created")


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
        file_path (str): 要上傳的檔案路徑
    """

    client.fput_object(bucket_name, object_name, file_path)


# ===== Main =====

if __name__ == "__main__":
    # 連接 MinIO Server
    client = connect_minio()

    # 建立 MinIO Buckets
    bucket_names = [
        MNIST_DATASETS_BUCKET_NAME,
        MNIST_NORMALIZE_BUCKET_NAME,
        MNIST_ONEHOT_ENCODING_BUCKET_NAME,
        MNIST_TRAINING_MODEL_BUCKET_NAME
    ]
    create_buckets(client, bucket_names)

    # 下載 MNIST 資料集
    download_mnist_datasets(client)
