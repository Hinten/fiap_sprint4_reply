
output "instance_hostname" {
  description = "Private DNS of the EC2 instance"
  value       = aws_instance.app_server.private_dns

}

output "instance_public_ip" {
  description = "Public IP of the EC2 instance"
  value       = aws_instance.app_server.public_ip

}