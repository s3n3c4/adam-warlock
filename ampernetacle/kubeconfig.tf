### Commented because it didn't work properly 

# locals {
#   is_windows = substr(pathexpand("~"), 0, 1) == "/" ? false : true
# }

# data "external" "kubeconfig" {
#   depends_on = [oci_core_instance._[1]]
#   program = local.is_windows ? [
#     "powershell",
#     <<EOT
#     write-host "{`"base64`": `"$(ssh -o StrictHostKeyChecking=no -l k8s -i ${local_file.ssh_private_key.filename} ${oci_core_instance._[1].public_ip} sudo base64 -w0 /etc/kubernetes/admin.conf)`"}"
#     EOT
#     ] : [
#     "sh",
#     "-c",
#     <<-EOT
#       set -e
#       cat >/dev/null
#       echo '{"base64": "'$(
#         ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
#               -l k8s -i ${local_file.ssh_private_key.filename} \
#               ${oci_core_instance._[1].public_ip} \
#               sudo cat ~/.kube/config | base64 -w0
#             )'"}'
#     EOT
#   ]
# }

# resource "local_file" "kubeconfig" {
#   content         = base64decode(data.external.kubeconfig.result.base64)
#   filename        = "kubeconfig"
#   file_permission = "0600"
#   provisioner "local-exec" {
#     command = "kubectl --kubeconfig=kubeconfig config set-cluster kubernetes --server=https://${oci_core_instance._[1].public_ip}:6443"
#   }
# }
