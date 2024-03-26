FROM tensorflow/tensorflow:2.16.1

WORKDIR /src

COPY dags/evaluate/model_evaluate.py /src/evaluate/model_evaluate.py

RUN pip install minio

CMD ["python", "/src/evaluate/model_evaluate.py"]
