FROM --platform=$TARGETPLATFORM python:3.10.13-slim

WORKDIR /src

COPY dags/training/model_training.py /src/training/model_training.py
COPY k8s/requirements.txt /src/requirements.txt

RUN pip install -r /src/requirements.txt

CMD ["python", "/src/training/model_training.py"]
