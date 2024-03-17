# Install on Ubuntu 20.04

## Build Essentials

### Install build essentials

```Shell
sudo apt-get update && sudo apt-get upgrade -y
sudo apt-get install -y build-essential curl
```

## Python

Ubuntu 20.04 default Python version is `Python 3.8.10`.

### PyPI

#### Install PyPI

```Shell
sudo apt-get update
sudo apt-get install -y python3-pip
```

### Virtual Environment

#### Install Virtual Environment

```Shell
sudo apt-get update
sudo apt-get install -y python3.8-venv
```

#### Activate Virtual Environment

```Shell
cd ~
python3.8 -m venv <venv name>
source ~/<venv name>/bin/activate
```

#### Deactivate Virtual Environment

```Shell
deactivate
```

### Install Project needed Dependencies

#### Automatic

```Shell
# In venv
pip install -r requirements-py38.txt
```

#### Manual

```Shell
# In venv
pip install tensorflow==2.13.1 apache-airflow==2.8.3 apache-airflow-providers-postgres==5.10.2 minio==7.2.5
pip install werkzeug==2.2.3 # Optional, reinstall if the above software packages cause incompatibility
pip install packaging==23.2 # Optional, reinstall if the above software packages cause incompatibility
pip install importlib-metadata==6.5.0 # Optional, reinstall if the above software packages cause incompatibility
```

## PostgreSQL

The version installed here is `PostgreSQL 16.2`.

### Install PostgreSQL (Automatic)

Already included in the command `make install`, just execute it.

### Install PostgreSQL (Manual)

```Shell
make install-postgresql
```

### Configure PostgreSQL

Connect to PostgreSQL Database using default user `postgres`.

```Shell
sudo -u postgres psql
```

```Shell
# In PostgreSQL shell
postgres=# \conninfo
```

Change password of default user `postgres` to `postgres`.

```Shell
# In PostgreSQL shell
postgres=# \password postgres
```

Create Database named `airflow_db`.

```Shell
# In PostgreSQL shell
postgres=# CREATE DATABASE airflow_db;
```

List all databases.

```Shell
# In PostgreSQL shell
postgres=# \l
```

### Configure pgAdmin4

* The email for pgAdmin4 is `admin@admin.com`.
* The password for pgAdmin4 is `postgres`.

Open browser, go to `http://127.0.0.1/pgadmin4`.
Click `Add New Server`.

Filled below parameters.

| Category   | Form                 | Value      |
|------------|----------------------|------------|
| General    | Name                 | Airflow    |
| Connection | Host name/address    | localhost  |
|            | Port                 | 5432       |
|            | Maintenance database | airflow_db |
|            | Username             | postgres   |
|            | Password             | postgres   |

## MinIO Object Storage for Linux

### MinIO Server

The version installed here is `latest`.

#### Install MinIO Server (Automatic)

Already included in the command `make install`, just execute it.

#### Install MinIO Server (Manual)

```Shell
make install-minio-server
```

#### Running MinIO Server

* The username for WebUI default is `minioadmin`.
* The password for WebUI default is `minioadmin`.

```Shell
make run-minio-server
```

### MinIO Client

The version installed here is `latest`.

#### Install MinIO Client (Automatic)

Already included in the command `make install`, just execute it.

#### Install MinIO Client (Manual)

```Shell
make install-minio-client
```

#### Configure MinIO Client

Notices: **Please configure MinIO Client after executing MinIO Server.**

* The MinIO Server host default is `http://127.0.0.1:9000`.
* The access_key for MinIO Client API default is `minioadmin`.
* The secret_key for MinIO Client API default is `minioadmin`.

```Shell
make config-minio-client
```

## Airflow

The version installed here is `Airflow 2.8.3`.

### Install Airflow

Already installed via `requirements.txt`.

### Running Airflow

* The username for WebUI default is `admin`.
* The password for WebUI can be seen in `standalone_password.txt` or in the terminal output log.

```Shell
# In venv
export AIRFLOW_HOME=$(pwd)
airflow standalone
```

### (Optional) Configure Airflow

Notices: **Please configure Airflow after executing Airflow instance once.**

Modify two parameters in the `airflow.cfg` file.

1. load_templates

Set False if you don't load airflow default templates. Default is True.

```text
load_templates = False
```

### Configure Airflow Database Connection

Notices: **Please configure Airflow Database Connection after executing Airflow instance once.**

Modify two parameters in the `airflow.cfg` file.

1. sql_alchemy_conn
2. executor

```text
sql_alchemy_conn = postgresql+psycopg2://postgres:postgres@localhost:5432/airflow_db
```

```text
executor = LocalExecutor
```

After the modification is completed, save the file and restart the airflow instance.