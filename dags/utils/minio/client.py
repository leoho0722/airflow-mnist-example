from env import env

from minio import Minio


def connect_minio():
    """連接 MinIO Server"""

    return Minio(
        endpoint=env.MINIO_API_ENDPOINT,
        access_key=env.MINIO_ACCESS_KEY,
        secret_key=env.MINIO_SECRET_KEY,
        secure=False
    )
