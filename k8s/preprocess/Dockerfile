FROM --platform=$TARGETPLATFORM python:3.10.13-slim

WORKDIR /src

COPY dags/preprocess/preprocess.py /src/preprocess/preprocess.py
COPY k8s/requirements.txt /src/requirements.txt

RUN pip install -r /src/requirements.txt

CMD ["python", "/src/preprocess/preprocess.py"]
