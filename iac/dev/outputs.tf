output "instance_hostname" {
  description = "Private DNS of the EC2 instance"
  value       = aws_instance.app_server.private_dns
}

output "instance_public_ip" {
  description = "Public IP of the EC2 instance"
  value       = aws_instance.app_server.public_ip
}

output "app_server_private_key" {
  description = "Private key for SSH access to app server"
  value       = tls_private_key.app_server.private_key_pem
  sensitive   = true
}

output "dashboard_url" {
  description = "URL to access the Streamlit dashboard"
  value       = "${aws_instance.app_server.public_ip}:${var.dashboard_port}"
}

output "api_url" {
  description = "URL to access the FastAPI service"
  value       = "${aws_instance.app_server.public_ip}:${var.api_port}"
}

output "rds_username" {
  description = "Usuário master da database RDS"
  value       = var.rds_username
}

output "rds_password" {
  description = "Senha master da database RDS"
  value       = var.rds_password
  sensitive   = true
}
