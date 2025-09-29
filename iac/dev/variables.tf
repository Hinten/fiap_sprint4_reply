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
