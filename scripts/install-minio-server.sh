#!/bin/bash

# ===== Download MinIO Server Binary File from Official =====

# 切回根目錄
cd ~

# 判斷是否有舊的 minio 目錄，有的話就刪除
if [ -d "minio" ]; then
    echo "found old minio directory..."
    echo "removing..."
    
    rm -rf minio
fi

# 判斷是否有舊的 minio 二進制執行檔，有的話就刪除
if [ -f "minio" ]; then
    echo "found old minio binary executable file..."
    echo "removing..."
    
    rm minio
fi

# 開始從官方下載 MinIO Server 二進制執行檔
echo "Downloading MinIO Server Binary executable file..."

wget https://dl.min.io/server/minio/release/linux-amd64/minio

echo "Downloaded MinIO Server Binary executable file success..."

# 更新 MinIO Server 二進制執行檔的權限
echo "Update Permissions of MinIO Server Binary executable file..."
chmod +x minio
