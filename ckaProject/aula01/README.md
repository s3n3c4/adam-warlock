## Bizus

- sudo apt list -a kube-adm

(instalar versão especifica)

- `sudo apt list -a kubeadm`

- `sudo apt install kubeadm=1.27.0-00 kubelet=1.27.0-00 kubectl=1.27.0-00 -y`

- `sudo kubeadm init --kubernetes-version=1.27.0`

- `mkdir -p $HOME/.kube`
- `sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config`
- `sudo chown $(id -u):$(id -g) $HOME/.kube/config`

> Depois do último nó entrar no cluster

- `kubectl apply -f https://github.com/weaveworks/weave/releases/download/v2.8.1/weave-daemonset-k8s.yaml`
