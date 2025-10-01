@echo off
REM Script para verificar os logs gerados pelo docker no app server via SSH

pushd iac\dev
terraform output -raw app_server_private_key > ..\..\app_server_key.pem
for /f "delims=" %%i in ('terraform output -raw instance_public_ip') do set EC2_IP=%%i
for /f "delims=" %%i in ('terraform output -raw dashboard_url') do set dashboard_url=%%i
for /f "delims=" %%i in ('terraform output -raw api_url') do set api_url=%%i
popd

REM 2. Definir arquivo de chave
set KEY_FILE=app_server_key.pem

ssh -i %KEY_FILE% -o StrictHostKeyChecking=no ubuntu@%EC2_IP% "cd ~/app && sudo docker-compose logs api"

pause
