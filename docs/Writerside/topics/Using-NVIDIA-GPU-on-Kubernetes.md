# Using NVIDIA GPU on Kubernetes

## Remove default driver

### Check the default driver is existing or not

```Shell
sudo lshw -C display
```

![截圖 2024-04-12 15.59.08.png](截圖_2024-04-12_15.59.08.png)

### List the default driver

```Shell
lsmod | grep nouveau
```

有出現「nouveau」就代表有預設驅動

![截圖 2024-04-12 15.59.51.png](截圖_2024-04-12_15.59.51.png)

### Delete the default driver and reboot

```Shell
cat <<EOF | sudo tee /etc/modprobe.d/blacklist-nouveau.conf
blacklist nouveau
options nouveau modeset=0
EOF
sudo update-initramfs -u
sudo reboot
```

![截圖 2024-04-12 16.02.24.png](截圖_2024-04-12_16.02.24.png)

## Install Nvidia CUDA

```Shell
sudo apt-get update -y
sudo apt install -y build-essential linux-headers-$(uname -r) wget
```

從 NVIDIA 官網下載所需的 CUDA Toolkit 版本

[NVIDIA CUDA Toolkit Official Download Website](https://developer.nvidia.com/cuda-toolkit-archive)

![截圖 2024-04-12 16.12.08.png](截圖_2024-04-12_16.12.08.png)

這邊示範的環境為

* CUDA Toolkit 12.4.1
* Ubuntu 22.04 x86_64
* runfile (local) Installer Type

![截圖 2024-04-12 16.13.46.png](截圖_2024-04-12_16.13.46.png)

```Shell
wget https://developer.download.nvidia.com/compute/cuda/12.4.1/local_installers/cuda_12.4.1_550.54.15_linux.run
sudo sh cuda_12.4.1_550.54.15_linux.run
```
執行後，會看到類 UI 的安裝選單
輸入 accept 來接受使用者條款

![截圖 2024-04-12 16.49.14.png](截圖_2024-04-12_16.49.14.png)

用空白鍵勾選「Driver」、「CUDA Toolkit」

![截圖 2024-04-12 16.54.35.png](截圖_2024-04-12_16.54.35.png)

安裝完成後，將下面兩行新增到 ```~/.bashrc``` 的最後

```Shell
nano ~/.bashrc
```

```Shell
export PATH=/usr/local/cuda/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH
```

```Shell
source ~/.bashrc
```

![截圖 2024-04-12 17.01.39.png](截圖_2024-04-12_17.01.39.png)

![截圖 2024-04-12 17.00.37.png](截圖_2024-04-12_17.00.37.png)

### Check NVIDIA CUDA

```Shell
nvidia-smi
nvcc --version
```

![截圖 2024-04-12 17.13.18.png](截圖_2024-04-12_17.13.18.png)

![截圖 2024-04-12 17.32.46.png](截圖_2024-04-12_17.32.46.png)

## Install NVIDIA cuDNN

從 NVIDIA 官網下載所需的 cuDNN 版本

[NVIDIA cuDNN Official Download Website](https://developer.download.nvidia.com/compute/cudnn/redist/cudnn/)

![截圖 2024-04-12 17.19.22.png](截圖_2024-04-12_17.19.22.png)

這邊系統環境是 Ubuntu 22.04 x86_64，所以選 ```linux-x86_64/```

![截圖 2024-04-12 17.21.06.png](截圖_2024-04-12_17.21.06.png)

這邊以 ```cudnn-linux-x86_64-8.9.7.29_cuda12-archive.tar.xz``` 為例

```Shell
wget https://developer.download.nvidia.com/compute/cudnn/redist/cudnn/linux-x86_64/cudnn-linux-x86_64-8.9.7.29_cuda12-archive.tar.xz
tar -xvf cudnn-linux-x86_64-8.9.7.29_cuda12-archive.tar.xz
sudo cp cudnn-linux-x86_64-8.9.7.29_cuda12-archive/include/cudnn*.h /usr/local/cuda/include/
sudo cp -P cudnn-linux-x86_64-8.9.7.29_cuda12-archive/lib/libcudnn* /usr/local/cuda/lib64
sudo chmod a+r /usr/local/cuda/include/ /usr/local/cuda/lib64
cat /usr/local/cuda/include/cudnn_version.h | grep CUDNN_MAJOR -A 2
```

![截圖 2024-04-12 17.24.56.png](截圖_2024-04-12_17.24.56.png)

![截圖 2024-04-12 17.25.41.png](截圖_2024-04-12_17.25.41.png)

![截圖 2024-04-12 17.30.50.png](截圖_2024-04-12_17.30.50.png)

## Install DKMS

```Shell
sudo apt-get update -y
sudo apt install -y dkms

# NVIDIA Driver Version 可以透過 nvidia-smi 取得，例如：550.54.15
sudo dkms install -m nvidia -v <NVIDIA Driver Version>
```

## Install NVIDIA Container Toolkit

[NVIDIA Container Toolkit Official Installation Guide](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)

### Installing with Apt

1. Configure the production repository

```Shell
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \
  && curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
    sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
    sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
```

2. Update the packages list from the repository

```Shell
sudo apt-get update
```

3. Install the NVIDIA Container Toolkit packages

```Shell
sudo apt-get install -y nvidia-container-toolkit
```

![截圖 2024-04-12 17.47.34.png](截圖_2024-04-12_17.47.34.png)

### Configuration

#### Configuring Docker

```Shell
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

確認 ```/etc/docker/daemon.json``` 是否有正確設定 NVIDIA GPU runtime，類似下面的資訊

```Shell
cat /etc/docker/daemon.json
```

```json
{
    "exec-opts": [
      "native.cgroupdriver=systemd"
    ],
    "log-driver": "json-file",
    "log-opts": {
      "max-size": "100m"
    },
    "default-runtime": "nvidia",
    "runtimes": {
      "nvidia": {
        "args": [],
        "path": "nvidia-container-runtime"
      }
    },
    "storage-driver": "overlay2"
}
```

如果依照官方步驟，卻沒有自動將 ```default-runtime``` 設定為 ```nvidia``` 的話，需手動加入

```Shell
sudo nano /etc/docker/daemon.json
sudo systemctl daemon-reload
sudo systemctl restart docker
```

#### Configuring containerd (for Kubernetes)

```Shell
sudo nvidia-ctk runtime configure --runtime=containerd
sudo systemctl restart containerd
```

## Install Kubernetes NVIDIA Device Plugin

[Kubernetes NVIDIA Device Plugin Official GitHub Repo](https://github.com/NVIDIA/k8s-device-plugin)

部署 ```nvidia-device-plugin``` DaemonSet 到 Kubernetes Cluster 中

```Shell
kubectl create -f https://raw.githubusercontent.com/NVIDIA/k8s-device-plugin/v0.14.5/nvidia-device-plugin.yml
```

### Check Pod can run GPU Jobs or not

```Shell
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: gpu-pod
spec:
  restartPolicy: Never
  containers:
    - name: cuda-container
      image: nvcr.io/nvidia/k8s/cuda-sample:vectoradd-cuda10.2
      resources:
        limits:
          nvidia.com/gpu: 1 # requesting 1 GPU
  tolerations:
  - key: nvidia.com/gpu
    operator: Exists
    effect: NoSchedule
EOF
```

```Shell
kubectl logs pod/gpu-pod
```

輸出 ```Test PASSED``` 就代表有成功在 Pod 中使用 GPU 資源

![截圖 2024-04-12 18.30.15.png](截圖_2024-04-12_18.30.15.png)

### Check node can use GPU resource or not

確認 ```Capacity``` 跟 ```Allocatable``` 是否有顯示 ```nvidia.com/gpu```

```Shell
kubectl describe node <Worker Node name>

# Example
kubectl describe node ubuntu3070ti
```

![截圖 2024-04-12 18.46.28.png](截圖_2024-04-12_18.46.28.png)