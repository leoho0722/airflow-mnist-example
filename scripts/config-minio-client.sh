#!/bin/bash

# ===== Setup MinIO Client Config =====

# 切回根目錄
cd ~

# 設定 MinIO Client 的配置檔
echo "Setup client config..."
~/mc alias set local "http://127.0.0.1:9000" minioadmin minioadmin
~/mc admin info local