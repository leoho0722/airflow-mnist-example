FROM --platform=$TARGETPLATFORM python:3.10.13-slim

WORKDIR /src

COPY dags/buckets_create/buckets_create.py /src/buckets_create/buckets_create.py
COPY k8s/requirements.txt /src/requirements.txt

RUN pip install -r /src/requirements.txt

CMD ["python", "/src/buckets_create/buckets_create.py"]
