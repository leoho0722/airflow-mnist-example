# airflow-mnist-example

**Below is deprecated.** Please refer to the [Documentation](./docs/Writerside/topics/Home.md) for the latest installation instructions.

## Environment Install

### MNIST CNN Model Datasets

#### Download

```shell
https://storage.googleapis.com/tensorflow/tf-keras-datasets/mnist.npz
```

### Python

Python Version: 3.10.13

<details>

<summary>Install Essential Libraries</summary>

```shell
# OpenSSL (use general user)
# Solved Error: Python require OpenSSL 1.1.1 or newer
wget https://www.openssl.org/source/openssl-1.1.1w.tar.gz
tar -xvf openssl-1.1.1w.tar.gz
cd openssl-1.1.1w
./config
sudo make
sudo make install
```

```shell
# Solved ImportError: No module named '_ctypes' 
sudo apt-get install libffi-dev
```

```shell
# Solved ImportError: No module named '_sqlite3'
sudo apt-get install sqlite3
```

```shell
# Solved AttributeError: module 'lib' has no attribute 'X509_V_FLAG_CB_ISSUER_CHECK'
# Reference: https://0xzx.com/zh-tw/2023020303323135609.html
sudo apt remove python3-pip 
wget https://bootstrap.pypa.io/get-pip.py
sudo python3 get-pip.py
# Kill Terminal or Reboot
pip install pyopenssl --upgrade
```

</details>

<details>

<summary>Build from Source Code</summary>

```shell
sudo apt-get update
wget https://www.python.org/ftp/python/3.10.13/Python-3.10.13.tgz
tar -xvf Python-3.10.13.tgz
cd Python-3.10.13
sudo apt-get install sqlite3 libffi-dev
./configure --enable-optimizations --enable-loadable-sqlite-extensions
sudo make
sudo make install
python3.10 --version
```

#### Test sqlite3

see "import sqlite3 success" message if sqlite3 is installed successfully.

```shell
python3.10
>> import sqlite3
>> print("import sqlite3 success")
```

#### Test openssl

see "import ssl success" message if ssl is installed successfully.

```shell
python3.10
>> import ssl
>> print("import ssl success")
```

#### Test ctypes

see "import ctypes success" message if ctypes is installed successfully.

```shell
python3.10
>> import ctypes
>> print("import ctypes success")
```

</details>

#### Update PIP

```shell
# Use root user
sudo python3.10 -m pip install --upgrade pip
```

#### Install Dependencies

```shell
# Use root user
sudo python3.10 -m pip install -r requirements.txt
```

### Airflow

#### Install from PyPI

Already installed through requirements.txt

#### Settings Environment Path for Airflow

```shell
export AIRFLOW_HOME=$(pwd)
```

#### Start Airflow Instance using standalone mode

```shell
airflow standalone
```

### MinIO Server

#### Install

* Ubuntu

```shell
wget https://dl.min.io/server/minio/release/linux-amd64/archive/minio_20240305044844.0.0_amd64.deb -O minio.deb
sudo dpkg -i minio.deb
```

* macOS

```shell
brew install minio/stable/minio
```

#### Launch

* Ubuntu

```shell
mkdir ~/minio
minio server ~/minio --console-address :9001
```

* macOS

```shell
export MINIO_CONFIG_ENV_FILE=/etc/default/minio
minio server --console-address :9001
```

### MinIO Client

#### Install

* Ubuntu

```shell
wget https://dl.min.io/client/mc/release/linux-amd64/mc
chmod +x mc
sudo mv mc /usr/local/bin/mc
```

* macOS

```shell
brew install minio/stable/mc
```

#### Config

```shell
mc alias set <ALIAS_NAME> http://<HOST_IP>:9000 <ACCESS_KEY> <SECRET_KEY> 
mc admin info <ALIAS_NAME>

# Example
# mc alias set local http://10.0.0.196:9000 minioadmin minioadmin
# mc admin info local
```

## Run

1. Start MinIO Server
   * `make run-minio-server`
2. Start Airflow standalone Instance
    * `make run-airflow-standalone`
3. Run Airflow DAG on Web UI
   * `http://<HOST_IP>:8080`
      * Username: `admin`
      * Password: can be see in `standalone_admin_password.txt` file
