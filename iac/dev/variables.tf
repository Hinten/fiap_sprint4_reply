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
