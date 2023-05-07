provider "aws" {
  region = "sa-east-1"
}

terraform {
  backend "s3" {
    bucket = "terraform-cka"
    key    = "cka-master/terraform.tfstate"
    region = "us-east-1"
  }
}

resource "aws_security_group" "kubernetes" {
  name_prefix = "kubernetes-"

  ingress {
    from_port   = 0
    to_port     = 65535
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 0
    to_port     = 65535
    protocol    = "udp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 6443
    to_port     = 6443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 2379
    to_port     = 2380
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 10250
    to_port     = 10255
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 30000
    to_port     = 32767
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "kubernetes"
  }
}


resource "aws_instance" "cka-master" {
  ami           = "ami-0b7af114fb404cd23"
  instance_type = "t3.small"
  key_name      = "ubuntu-xiaomi"

  tags = {
    Name = "cka-master"
  }
}

output "public_ip" {
  value = aws_instance.cka-master.public_ip
}

resource "local_file" "output" {
  content  = "[${aws_instance.cka-master.tags.Name}] \n${aws_instance.cka-master.public_ip} ansible_user=ubuntu"
  filename = "../ansible/hosts"
}

