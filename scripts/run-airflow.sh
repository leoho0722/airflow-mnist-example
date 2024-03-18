#!/bin/bash

# 設定 AIRFLOW_HOME 環境變數
export AIRFLOW_HOME=$(pwd)

clear

# 啟動 Airflow Standalone
airflow standalone