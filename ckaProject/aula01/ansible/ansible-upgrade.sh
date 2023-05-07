#!/bin/bash

sudo apt-get update && apt-get install -y kubeadm=1.27.1-00
sudo kubeadm upgrade plan
sudo kubeadm upgrade apply v1.27.1-00
kubectl drain cka-master --ignore-daemonsets
sudo apt-get update && sudo apt-get install -y kubelet=1.27.1-00 kubectl=1.27.1-00
sudo systemctl daemon-reload
sudo systemctl restart kubelet
kubectl uncordon cka-master
kubectl get nodes