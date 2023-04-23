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

resource "aws_security_group_rule" "ssh_from_my_ip" {
  type        = "ingress"
  from_port   = 22
  to_port     = 22
  protocol    = "tcp"
  cidr_blocks = ["0.0.0.0/0"]

  security_group_id = "sg-0e6413d8d8d6736c7"
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
