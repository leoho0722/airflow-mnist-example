#!/bin/bash

KUBE_VERSION=1.23
# containerd=v1.6.0+,1,5.8+
CNI_VERSION="v0.8.2"
CRICTL_VERSION="v1.23.0"
KUBELET_SERVICE_RELEASE_VERSION="v0.4.0"

KUBERNETES_RELEASE="$(curl -sSL https://dl.k8s.io/release/stable-${KUBE_VERSION}.txt)"
ARCH=$(dpkg --print-architecture)

# =====   Prepare    =====
# ----- disable swap -----
sudo sed -i '/swap/s/^/#/' /etc/fstab
sudo swapoff -a
sudo cat /etc/fstab
# ----- set iptables -----
cat <<EOF | sudo tee /etc/modules-load.d/k8s.conf
br_netfilter
EOF

cat <<EOF | sudo tee /etc/sysctl.d/k8s.conf
net.bridge.bridge-nf-call-ip6tables = 1
net.bridge.bridge-nf-call-iptables  = 1
EOF
sudo sysctl --system

# -----  Package   -----
sudo apt update
sudo apt install -y curl tar ca-certificates socat conntrack


# =====  Install   =====
# ----- CNI plugins -----
sudo mkdir -p /opt/cni/bin
curl -L "https://github.com/containernetworking/plugins/releases/download/${CNI_VERSION}/cni-plugins-linux-${ARCH}-${CNI_VERSION}.tgz" | sudo tar -C /opt/cni/bin -xz

# ----- Install crictl -----
DOWNLOAD_DIR=/usr/local/bin
sudo mkdir -p $DOWNLOAD_DIR
curl -L "https://github.com/kubernetes-sigs/cri-tools/releases/download/${CRICTL_VERSION}/crictl-${CRICTL_VERSION}-linux-${ARCH}.tar.gz" | sudo tar -C $DOWNLOAD_DIR -xz

# ----- Install kubeadm, kubelet, kubectl -----
cd $DOWNLOAD_DIR
sudo curl -L --remote-name-all https://dl.k8s.io/release/${KUBERNETES_RELEASE}/bin/linux/${ARCH}/{kubeadm,kubelet,kubectl}
sudo curl -L --remote-name-all https://dl.k8s.io/release/${KUBERNETES_RELEASE}/bin/linux/${ARCH}/{kubeadm,kubelet,kubectl}.sha256
echo "$(cat kubeadm.sha256)  kubeadm" | sha256sum --check
echo "$(cat kubelet.sha256)  kubelet" | sha256sum --check
echo "$(cat kubectl.sha256)  kubectl" | sha256sum --check
sudo chmod +x {kubeadm,kubelet,kubectl}

kubeadm version
kubelet --version
kubectl version --client

# ----- kubelet service -----
curl -sSL "https://raw.githubusercontent.com/kubernetes/release/${KUBELET_SERVICE_RELEASE_VERSION}/cmd/kubepkg/templates/latest/deb/kubelet/lib/systemd/system/kubelet.service" | sed "s:/usr/bin:${DOWNLOAD_DIR}:g" | sudo tee /etc/systemd/system/kubelet.service
sudo mkdir -p /etc/systemd/system/kubelet.service.d
curl -sSL "https://raw.githubusercontent.com/kubernetes/release/${KUBELET_SERVICE_RELEASE_VERSION}/cmd/kubepkg/templates/latest/deb/kubeadm/10-kubeadm.conf" | sed "s:/usr/bin:${DOWNLOAD_DIR}:g" | sudo tee /etc/systemd/system/kubelet.service.d/10-kubeadm.conf
sudo systemctl enable --now kubelet
systemctl status --no-pager kubelet

if [ $# -le 2 ]
then
  sudo kubeadm init --v=5 --pod-network-cidr=10.244.0.0/16
  mkdir -p $HOME/.kube
  sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
  sudo chown $(id -u):$(id -g) $HOME/.kube/config
  kubectl apply -f https://github.com/flannel-io/flannel/releases/latest/download/kube-flannel.yml
  kubectl cluster-info
else
  sudo kubeadm join $*
fi