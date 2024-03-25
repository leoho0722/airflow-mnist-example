FROM --platform=$TARGETPLATFORM python:3.10.13-alpine

WORKDIR /src

COPY dags/check_gpu/check_gpu.py /src/check_gpu.py

CMD [ "python", "/src/check_gpu.py" ]