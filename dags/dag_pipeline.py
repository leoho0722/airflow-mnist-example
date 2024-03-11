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


# def hello1():
#     print('Hello 1')


# def hello2():
#     print('Hello 2')


# def hello3():
#     print('Hello 3')


# def hello4():
#     print('Hello 4')


with DAG(dag_id='mnist-pipeline', default_args=default_args) as dag:
    preprocess = PythonOperator(
        task_id='mnist-preprocess',
        python_callable=data_preprocess.data_preprocess
    )
    training = PythonOperator(
        task_id='mnist-model-training',
        python_callable=model_training.training_model
    )
    evaluate = PythonOperator(
        task_id='mnist-model-evaluate',
        python_callable=model_evaluate.model_evaluate
    )

    preprocess >> training >> evaluate


# with DAG(dag_id='hello-pipeline', default_args=default_args) as dag:
#     hello1 = PythonOperator(
#         task_id='hello1',
#         python_callable=hello1
#     )
#     hello2 = PythonOperator(
#         task_id='hello2',
#         python_callable=hello2
#     )
#     hello3 = PythonOperator(
#         task_id='hello3',
#         python_callable=hello3
#     )
#     hello4 = PythonOperator(
#         task_id='hello4',
#         python_callable=hello4
#     )

#     hello1 >> hello2 >> hello3 >> hello4
