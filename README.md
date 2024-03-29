# airflow-mnist-example

## Environment

### Developement

* macOS Sonoma 14.4.1
* Python 3.10.13 (via Homebrew)
* minikube 1.32.0 (Installed Kubernetes 1.28.3)

### Deployment

#### Local

* Airflow 2.8.3
* PostgreSQL 16.2
* MinIO 7.2.5

#### Kubernetes Cluster

##### Master Node (Control Plane)

* Kubernetes 1.23.17

##### Worker Node

* Kubernetes 1.23.17
* NVIDIA CUDA 12.1
* GPU: NVIDIA GeForce RTX 3070 Ti

#### DAGs

```text
airflow-buckets-create >> airflow-preprocess >> airflow-training >> airflow-evaluate
```

* airflow-buckets-create
  * Docker Base Image: `python:3.10.13-slim`
  * PyPl
    * Tensorflow 2.16.1
    * MinIO 7.2.5
* airflow-preprocess
  * Docker Base Image: `python:3.10.13-slim`
  * PyPl
    * Tensorflow 2.16.1
    * MinIO 7.2.5
* airflow-training
  * Docker Base Image: `tensorflow/tensorflow:2.14.0-gpu`
  * PyPl
    * MinIO 7.2.5
* airflow-evaluate
  * Docker Base Image: `tensorflow/tensorflow:2.14.0`
  * PyPl
    * MinIO 7.2.5

## Documentation

Go to the [Documentation](https://leoho0722.github.io/airflow-mnist-example/home.html)
