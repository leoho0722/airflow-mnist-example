#!/bin/bash

# ===== Download MinIO Client Binary executable file from Official =====

# 切回根目錄
cd ~

# 判斷是否有舊的 mc 二進制執行檔，有的話就刪除
if [ -f "mc" ]; then
    echo "found old mc binary executable file..."
    echo "removing..."
    
    rm mc
fi

# 開始從官方下載 MinIO Client 二進制執行檔
echo "Downloading MinIO Client Binary executable file..."

wget https://dl.min.io/client/mc/release/linux-amd64/mc

echo "Downloaded MinIO Client Binary executable file success..."

# 更新 MinIO Client 二進制執行檔的權限
echo "Update Permissions of MinIO Client Binary executable file..."
chmod +x mc