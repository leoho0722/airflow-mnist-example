FROM --platform=$TARGETPLATFORM python:3.10.13-slim

WORKDIR /src

COPY dags/evaluate/model_evaluate.py /src/evaluate/model_evaluate.py
COPY k8s/requirements.txt /src/requirements.txt

RUN pip install -r /src/requirements.txt

CMD ["python", "/src/evaluate/model_evaluate.py"]
