#!/bin/bash

# 1. Install Istio
~/kustomize-v3.2.0 build common/istio-1-14/istio-crds/base | kubectl apply -f -
~/kustomize-v3.2.0 build common/istio-1-14/istio-namespace/base | kubectl apply -f -
~/kustomize-v3.2.0 build common/istio-1-14/istio-install/base | kubectl apply -f -

# 2. Install Knative Serving
~/kustomize-v3.2.0 build common/knative/knative-serving/overlays/gateways | kubectl apply -f -
~/kustomize-v3.2.0 build common/istio-1-14/cluster-local-gateway/base | kubectl apply -f -

# 3. Install Cert Manager
~/kustomize-v3.2.0 build common/cert-manager/cert-manager/base | kubectl apply -f -
~/kustomize-v3.2.0 build common/cert-manager/kubeflow-issuer/base | kubectl apply -f -

# 4. Install KServe
kubectl apply -f https://github.com/kserve/kserve/releases/download/v0.8.0/kserve.yaml

# 5. Install KServe Built-in ClusterServingRuntimes
kubectl apply -f https://github.com/kserve/kserve/releases/download/v0.8.0/kserve-runtimes.yaml

# 6. Install Other
# * Dex
~/kustomize-v3.2.0 build common/dex/overlays/istio | kubectl apply -f -

# * OIDC AuthService
~/kustomize-v3.2.0 build common/oidc-authservice/base | kubectl apply -f -
kubectl apply -f kubeflow-pv.yaml -l name=authservice

# * Kubeflow Namespace
~/kustomize-v3.2.0 build common/kubeflow-namespace/base | kubectl apply -f -

# * Kubeflow Roles
~/kustomize-v3.2.0 build common/kubeflow-roles/base | kubectl apply -f -

# * Kubeflow Istio Resources
~/kustomize-v3.2.0 build common/istio-1-14/kubeflow-istio-resources/base | kubectl apply -f -

# * Kubeflow Pipelines
~/kustomize-v3.2.0 build apps/pipeline/upstream/env/cert-manager/platform-agnostic-multi-user | kubectl apply -f -
kubectl apply -f kubeflow-pv.yaml -l name=kubeflow

# * katib
~/kustomize-v3.2.0 build apps/katib/upstream/installs/katib-with-kubeflow | kubectl apply -f -
kubectl apply -f kubeflow-pv.yaml -l name=katib-mysql

# * Central Dashboard
~/kustomize-v3.2.0 build apps/centraldashboard/upstream/overlays/kserve | kubectl apply -f -

# * Admission Webhook
~/kustomize-v3.2.0 build apps/admission-webhook/upstream/overlays/cert-manager | kubectl apply -f -

# * Notebooks
~/kustomize-v3.2.0 build apps/jupyter/notebook-controller/upstream/overlays/kubeflow | kubectl apply -f -

# * Profiles + KFAM
~/kustomize-v3.2.0 build apps/profiles/upstream/overlays/kubeflow | kubectl apply -f -

# * Volumes Web App
~/kustomize-v3.2.0 build apps/volumes-web-app/upstream/overlays/istio | kubectl apply -f -

# * Tensorboard
~/kustomize-v3.2.0 build apps/tensorboard/tensorboards-web-app/upstream/overlays/istio | kubectl apply -f -

# * Training Operator
~/kustomize-v3.2.0 build apps/training-operator/upstream/overlays/kubeflow | kubectl apply -f -

# * User Namespace
~/kustomize-v3.2.0 build common/user-namespace/base | kubectl apply -f -