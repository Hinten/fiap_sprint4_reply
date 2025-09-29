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

resource "aws_subnet" "app_server_subnet_2" {
  vpc_id                  = aws_vpc.app_server_vpc.id
  cidr_block              = "10.0.2.0/24"
  map_public_ip_on_launch = true
  availability_zone       = "us-east-1b"
  tags = {
    Name = "app-server-subnet-2"
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
ORACLE_DSN=${aws_db_instance.oracle_rds.endpoint}:1521/${var.rds_db_name}
ORACLE_USER=${var.rds_username}
ORACLE_PASSWORD=${var.rds_password}
EOF
}

resource "aws_db_subnet_group" "oracle_rds_subnet_group" {
  name       = "oracle-rds-subnet-group"
  subnet_ids = [aws_subnet.app_server_subnet.id, aws_subnet.app_server_subnet_2.id]
  tags = {
    Name = "oracle-rds-subnet-group"
  }
}

resource "aws_security_group" "oracle_rds_sg" {
  name        = "oracle_rds_sg"
  description = "Permite acesso ao Oracle RDS apenas do EC2 na VPC"
  vpc_id      = aws_vpc.app_server_vpc.id

  ingress {
    description     = "Permite acesso Oracle do EC2"
    from_port       = 1521
    to_port         = 1521
    protocol        = "tcp"
    security_groups = [aws_security_group.app_server_sg.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_db_instance" "oracle_rds" {
  identifier             = "oracle-rds-instance"
  engine                 = "oracle-se2"
  engine_version         = "19.0.0.0.ru-2024-04.rur-2024-04.r1"
  instance_class         = var.rds_instance_class
  allocated_storage      = var.rds_allocated_storage
  db_name                = var.rds_db_name
  username               = var.rds_username
  password               = var.rds_password
  db_subnet_group_name   = aws_db_subnet_group.oracle_rds_subnet_group.name
  vpc_security_group_ids = [aws_security_group.oracle_rds_sg.id]
  skip_final_snapshot    = true
  publicly_accessible    = false
  tags = {
    Name = "oracle-rds-instance"
  }
}
