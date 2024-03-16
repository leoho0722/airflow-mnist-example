#!/bin/bash

# ===== Run MinIO Server =====

# 切回根目錄
cd ~

# 判斷是否有 minio-data 目錄，沒有的話就建立
if [ ! -d "minio-data" ]; then
    echo "~/minio-data directory does not exist..."
    echo "create ~/minio-data directory..."
    
    mkdir ~/minio-data
fi

# 判斷是否有 minio-data 目錄，有的話就執行 minio server
if [ -d "minio-data" ]; then
    echo "~/minio-data directory does exist..."
    echo "starting run minio server..."
    
    ~/minio server ~/minio-data --console-address :9001
fi