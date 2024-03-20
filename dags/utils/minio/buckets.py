from minio import Minio, S3Error


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
        client.fput_object(bucket_name=bucket_name,
                           object_name=object_name,
                           file_path=file_path)
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
