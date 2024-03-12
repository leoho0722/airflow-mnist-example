from constants import env
from utils.utils import mkdir
from preprocess import data_preprocess
from training import model_training
from evaluate import model_evaluate

from airflow import DAG
from airflow.operators.python import PythonOperator
import pendulum

default_args = {
    'owner': 'Leo Ho',
    'start_date': pendulum.datetime(2024, 3, 11, tz="UTC"),
    'retries': 1,
}

# ===== Airflow MNIST Pipeline Python Callable Functions =====


def create_folder():
    mkdir(env.MNIST_ROOT_DIR)
    mkdir(env.MNIST_DATASETS_DIR)
    mkdir(env.MNIST_NORMALIZE_DIR)
    mkdir(env.MNIST_ONEHOT_ENCODING_DIR)
    mkdir(env.MNIST_TRAINING_MODEL_DIR)


with DAG(dag_id='mnist-pipeline', default_args=default_args) as dag:
    mnist_create_folder = PythonOperator(
        task_id='mnist-create-folder',
        python_callable=create_folder
    )
    mnist_data_preprocess = PythonOperator(
        task_id='mnist-data-preprocess',
        python_callable=data_preprocess.model_data_preprocess
    )
    mnist_model_training = PythonOperator(
        task_id='mnist-model-training',
        python_callable=model_training.model_training
    )
    mnist_model_evaluate = PythonOperator(
        task_id='mnist-model-evaluate',
        python_callable=model_evaluate.model_evaluate
    )

    mnist_create_folder >> mnist_data_preprocess >> mnist_model_training >> mnist_model_evaluate
