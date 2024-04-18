FROM tensorflow/tensorflow:2.14.0

WORKDIR /src

COPY dags/evaluate/evaluate.py /src/evaluate/evaluate.py

RUN pip install minio

CMD ["python", "/src/evaluate/evaluate.py"]
