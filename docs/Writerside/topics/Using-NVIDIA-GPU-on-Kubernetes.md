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

If "nouveau" appears, it means there is a default driver.

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

Download the required CUDA Toolkit version from the NVIDIA official website

[NVIDIA CUDA Toolkit Official Download Website](https://developer.nvidia.com/cuda-toolkit-archive)

![截圖 2024-04-12 16.12.08.png](截圖_2024-04-12_16.12.08.png)

The environment demonstrated here is

* CUDA Toolkit 12.4.1
* Ubuntu 22.04 x86_64
* runfile (local) Installer Type

![截圖 2024-04-12 16.13.46.png](截圖_2024-04-12_16.13.46.png)

```Shell
wget https://developer.download.nvidia.com/compute/cuda/12.4.1/local_installers/cuda_12.4.1_550.54.15_linux.run
sudo sh cuda_12.4.1_550.54.15_linux.run
```

After execution, you will see a UI-like installation menu.
Enter accept to accept the terms of use

![截圖 2024-04-12 16.49.14.png](截圖_2024-04-12_16.49.14.png)

Use the space bar to select "Driver" and "CUDA Toolkit"

![截圖 2024-04-12 16.54.35.png](截圖_2024-04-12_16.54.35.png)

After the installation is complete, add the following two lines to the end of ```~/.bashrc```

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

Download the required cuDNN version from the NVIDIA official website

[NVIDIA cuDNN Official Download Website](https://developer.download.nvidia.com/compute/cudnn/redist/cudnn/)

![截圖 2024-04-12 17.19.22.png](截圖_2024-04-12_17.19.22.png)

The system environment here is Ubuntu 22.04 x86_64, so choose ```linux-x86_64/```

![截圖 2024-04-12 17.21.06.png](截圖_2024-04-12_17.21.06.png)

Here we take ```cudnn-linux-x86_64-8.9.7.29_cuda12-archive.tar.xz``` as an example

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

Confirm whether ```/etc/docker/daemon.json``` has correctly configured NVIDIA GPU runtime, similar to the following information

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

If you follow the official steps but do not automatically set ```default-runtime``` to ```nvidia```, you need to manually add it.

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

Deploy ```nvidia-device-plugin``` DaemonSet to Kubernetes Cluster

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

Outputting ```Test PASSED``` means that GPU resources are successfully used in the Pod.

![截圖 2024-04-12 18.30.15.png](截圖_2024-04-12_18.30.15.png)

### Check node can use GPU resource or not

Check whether ```Capacity``` and ```Allocatable``` are displayed ```nvidia.com/gpu```

```Shell
kubectl describe node <Worker Node name>

# Example
kubectl describe node ubuntu3070ti
```

![截圖 2024-04-12 18.46.28.png](截圖_2024-04-12_18.46.28.png)