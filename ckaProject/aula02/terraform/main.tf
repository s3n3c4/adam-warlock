provider "aws" {
  region = "sa-east-1"
}

terraform {
  backend "s3" {
    bucket = "terraform-cka"
    key    = "cka-node-1/terraform.tfstate"
    region = "us-east-1"
  }
}

data "aws_security_group" "kubernetes" {
  name = "kubernetes"
}

resource "aws_security_group_rule" "ssh_from_my_ip" {
  type        = "ingress"
  from_port   = 22
  to_port     = 22
  protocol    = "tcp"
  cidr_blocks = ["0.0.0.0/0"]

  security_group_id = data.aws_security_group.kubernetes.id
}
resource "aws_instance" "cka-node-1" {
  ami           = "ami-0b7af114fb404cd23"
  instance_type = "t3.small"
  key_name      = "ubuntu-xiaomi"

  tags = {
    Name = "cka-node-1"
  }
}

resource "local_file" "output" {
  content  = "[${aws_instance.cka-node-1.tags.Name}] \n${aws_instance.cka-node-1.public_ip} ansible_user=ubuntu"
  filename = "../ansible/hosts"
}
