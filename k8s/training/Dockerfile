# Use the GPU version image of TensorFlow, supports CUDA >= 11.8
FROM tensorflow/tensorflow:2.14.0-gpu

WORKDIR /src

COPY dags/training/model_training.py /src/training/model_training.py

RUN pip install minio

CMD ["python", "/src/training/model_training.py"]
