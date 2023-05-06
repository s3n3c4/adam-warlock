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
