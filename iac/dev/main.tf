# Configure the AWS Provider
provider "aws" {
  region = "us-east-1"
}

data "aws_ami" "ubuntu" {
  most_recent = true

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*"]
  }

  owners = ["099720109477"] # Canonical
}

resource "tls_private_key" "app_server" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

resource "aws_key_pair" "app_server" {
  key_name   = "app_server_key"
  public_key = tls_private_key.app_server.public_key_openssh
}

resource "aws_vpc" "app_server_vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true
  tags = {
    Name = "app-server-vpc"
  }
}

resource "aws_internet_gateway" "app_server_igw" {
  vpc_id = aws_vpc.app_server_vpc.id
  tags = {
    Name = "app-server-igw"
  }
}

resource "aws_subnet" "app_server_subnet" {
  vpc_id                  = aws_vpc.app_server_vpc.id
  cidr_block              = "10.0.1.0/24"
  map_public_ip_on_launch = true
  availability_zone       = "us-east-1a"
  tags = {
    Name = "app-server-subnet"
  }
}

resource "aws_route_table" "app_server_rt" {
  vpc_id = aws_vpc.app_server_vpc.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.app_server_igw.id
  }
  tags = {
    Name = "app-server-rt"
  }
}

resource "aws_route_table_association" "app_server_rta" {
  subnet_id      = aws_subnet.app_server_subnet.id
  route_table_id = aws_route_table.app_server_rt.id
}

resource "aws_security_group" "app_server_sg" {
  name        = "app_server_sg"
  description = "Permite acesso SSH e HTTP ao app server"
  vpc_id      = aws_vpc.app_server_vpc.id

  ingress {
    description = "SSH from anywhere (ajuste para seu IP se desejar)"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTP para Streamlit"
    from_port   = var.dashboard_port
    to_port     = var.dashboard_port
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "Porta api REST FastAPI"
    from_port   = var.api_port
    to_port     = var.api_port
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_instance" "app_server" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = var.instance_type
  key_name               = aws_key_pair.app_server.key_name
  vpc_security_group_ids = [aws_security_group.app_server_sg.id]
  subnet_id              = aws_subnet.app_server_subnet.id

  tags = {
    Name = var.instance_name
  }

}

resource "local_file" "env_file" {
  filename = "${path.module}/../../.env-docker"
  content  = <<EOF
DASHBOARD_PORT=${var.dashboard_port}
API_PORT=${var.api_port}
EOF
}
