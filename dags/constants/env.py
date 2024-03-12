# ===== MinIO Server 設定 =====
MINIO_API_ENDPOINT = "10.0.0.196:9000"
MINIO_ACCESS_KEY = "minioadmin"
MINIO_SECRET_KEY = "minioadmin"

# ===== MinIO Buckets 名稱 =====
MNIST_DATASETS_BUCKET_NAME = "mnist-datasets"
MNIST_NORMALIZE_BUCKET_NAME = "mnist-normalize"
MNIST_ONEHOT_ENCODING_BUCKET_NAME = "mnist-onehot-encoding"
MNIST_TRAINING_MODEL_BUCKET_NAME = "mnist-training-model"

# ===== MNIST 資料集檔案名稱 =====
MNIST_DATASETS_FILENAME = "mnist.npz"

# ===== Pkl 檔案名稱 =====
X_TRAIN4D_NORMALIZE_PKL_FILENAME = "X_Train4D_normalize.pkl"
X_TEST4D_NORMALIZE_PKL_FILENAME = "X_Test4D_normalize.pkl"
Y_TRAIN_ONE_HOT_ENCODING_PKL_FILENAME = "y_Train_One_Hot_Encoding.pkl"
Y_TEST_ONE_HOT_ENCODING_PKL_FILENAME = "y_TestOneHot.pkl"

# ===== 訓練後的模型檔案名稱 =====
TRAINED_MODEL_KERAS_FILENAME = "trained_model.keras"

# ===== Directory Path =====
MNIST_PARENT_DIR = "./"
MNIST_ROOT_DIR = "./mnist"
MNIST_DATASETS_DIR = f"{MNIST_ROOT_DIR}/datasets"
MNIST_NORMALIZE_DIR = f"{MNIST_ROOT_DIR}/normalize"
MNIST_ONEHOT_ENCODING_DIR = f"{MNIST_ROOT_DIR}/onehot-encoding"
MNIST_TRAINING_MODEL_DIR = f"{MNIST_ROOT_DIR}/training-model"

# ===== File Path =====
MNIST_DATASETS_FILE_PATH = f"{MNIST_DATASETS_DIR}/{MNIST_DATASETS_FILENAME}"
X_TRAIN4D_NORMALIZE_FILE_PATH = f"{MNIST_NORMALIZE_DIR}/{X_TRAIN4D_NORMALIZE_PKL_FILENAME}"
X_TEST4D_NORMALIZE_FILE_PATH = f"{MNIST_NORMALIZE_DIR}/{X_TEST4D_NORMALIZE_PKL_FILENAME}"
Y_TRAIN_ONE_HOT_ENCODING_FILE_PATH = f"{MNIST_ONEHOT_ENCODING_DIR}/{Y_TRAIN_ONE_HOT_ENCODING_PKL_FILENAME}"
Y_TEST_ONE_HOT_ENCODING_FILE_PATH = f"{MNIST_ONEHOT_ENCODING_DIR}/{Y_TEST_ONE_HOT_ENCODING_PKL_FILENAME}"
TRAINED_MODEL_KERAS_FILE_PATH = f"{MNIST_TRAINING_MODEL_DIR}/{TRAINED_MODEL_KERAS_FILENAME}"
