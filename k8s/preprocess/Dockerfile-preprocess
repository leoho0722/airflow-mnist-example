FROM --platform=$TARGETPLATFORM python:3.10.13-slim

WORKDIR /src

COPY dags/preprocess/data_preprocess.py /src/preprocess/data_preprocess.py
COPY k8s/requirements.txt /src/requirements.txt

RUN pip install -r /src/requirements.txt

CMD ["python", "/src/preprocess/data_preprocess.py"]
