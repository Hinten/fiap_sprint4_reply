variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "us-east-1"
}

variable "instance_name" {
  description = "Value of the Name tag for the EC2 instance"
  type        = string
  default     = "app-server"
}

variable "instance_type" {
  description = "The EC2 instance type"
  type        = string
  default     = "t3.micro"
}

variable "dashboard_port" {
  description = "Porta do dashboard (Streamlit)"
  type        = number
  default     = 8501
}

variable "api_port" {
  description = "Porta da API (FastAPI)"
  type        = number
  default     = 8180
}

variable "rds_db_name" {
  description = "Nome do banco RDS"
  type        = string
  default     = "fiap_reply_db"
}

variable "rds_username" {
  description = "Usuário master da database RDS"
  type        = string
  default     = "FIAPREPLYUSER"
}

variable "rds_password" {
  description = "Senha master da database RDS"
  type        = string
  sensitive   = true
}

variable "rds_instance_class" {
  description = "Classe da instância RDS"
  type        = string
  default     = "db.t3.micro"
}

variable "rds_allocated_storage" {
  description = "Armazenamento (GB) do RDS"
  type        = number
  default     = 20
}

variable "sns_topic_name" {
  description = "Nome do tópico SNS para notificações por e-mail"
  type        = string
  default     = "email-notifications-topic"
}

variable "aws_access_key_id" {
  description = "AWS Access Key ID - Necessário para enviar notificações SNS, utilize aws configure get aws_access_key_id"
  type        = string
  sensitive   = true
}

variable "aws_secret_access_key" {
  description = "AWS Secret Access Key - Necessário para enviar notificações SNS, utilize aws configure get aws_secret_access_key"
  type        = string
  sensitive   = true
}

variable "aws_session_token" {
  description = "AWS Session Token - Necessário para enviar notificações SNS, utilize aws configure get aws_session_token"
  type        = string
  sensitive   = true
}