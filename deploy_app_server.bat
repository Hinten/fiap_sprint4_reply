
@echo off
REM Script para deploy do app server via SSH
REM Pré-requisitos: terraform, aws cli, scp, ssh instalados
REM aws cli já deve estar com as credenciais configuradas

REM 1. Ir para o diretório do Terraform e salvar outputs corretamente
pushd iac\dev
terraform output -raw app_server_private_key > ..\..\app_server_key.pem
for /f "delims=" %%i in ('terraform output -raw instance_public_ip') do set EC2_IP=%%i
for /f "delims=" %%i in ('terraform output -raw dashboard_url') do set dashboard_url=%%i
for /f "delims=" %%i in ('terraform output -raw api_url') do set api_url=%%i
popd

REM 2. Definir arquivo de chave
set KEY_FILE=app_server_key.pem

REM 3. Copiar o dockerfile e o app para o servidor
REM PQ fazer isso? A imagem do docker buildada tem 1.6GB por conta do pycaret. Esta forma não é a mais correta, porém é muito rápido, bom para testar

ssh -i %KEY_FILE% -o StrictHostKeyChecking=no ubuntu@%EC2_IP% "sudo apt-get update"
ssh -i %KEY_FILE% -o StrictHostKeyChecking=no ubuntu@%EC2_IP% "sudo apt-get install -y docker.io"
ssh -i %KEY_FILE% -o StrictHostKeyChecking=no ubuntu@%EC2_IP% "sudo apt-get install -y git"

ssh -i %KEY_FILE% -o StrictHostKeyChecking=no ubuntu@%EC2_IP% "sudo rm -rf ~/app"
ssh -i %KEY_FILE% -o StrictHostKeyChecking=no ubuntu@%EC2_IP% "sudo git clone https://github.com/Hinten/fiap_sprint4_reply.git ~/app"
ssh -i %KEY_FILE% -o StrictHostKeyChecking=no ubuntu@%EC2_IP% "sudo chmod +x ~/app"
REM tive que adicionar as 2 linhas abaixo pq o docker-compose não estava no package manager do ubuntu da máquina
ssh -i %KEY_FILE% -o StrictHostKeyChecking=no ubuntu@%EC2_IP% "sudo curl -L \"https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)\" -o /usr/local/bin/docker-compose"
ssh -i %KEY_FILE% -o StrictHostKeyChecking=no ubuntu@%EC2_IP% "sudo chmod +x /usr/local/bin/docker-compose"
ssh -i %KEY_FILE% -o StrictHostKeyChecking=no ubuntu@%EC2_IP% "sudo usermod -aG docker ubuntu"

REM Corrigir permissões para permitir scp
ssh -i %KEY_FILE% -o StrictHostKeyChecking=no ubuntu@%EC2_IP% "sudo chown -R ubuntu:ubuntu ~/app"

ssh -i %KEY_FILE% -o StrictHostKeyChecking=no ubuntu@%EC2_IP% "mkdir -p ~/app/"
scp -i %KEY_FILE% -o StrictHostKeyChecking=no Dockerfile ubuntu@%EC2_IP%:~/app/Dockerfile
ssh -i %KEY_FILE% -o StrictHostKeyChecking=no ubuntu@%EC2_IP% "mkdir -p ~/app/src/dashboard"
scp -i %KEY_FILE% -o StrictHostKeyChecking=no src/dashboard/Dockerfile ubuntu@%EC2_IP%:~/app/src/dashboard/Dockerfile
ssh -i %KEY_FILE% -o StrictHostKeyChecking=no ubuntu@%EC2_IP% "mkdir -p ~/app/src/api"
scp -i %KEY_FILE% -o StrictHostKeyChecking=no src/api/Dockerfile ubuntu@%EC2_IP%:~/app/src/api/Dockerfile
REM importante para pegar as variáveis de ambiente corretas
scp -i %KEY_FILE% -o StrictHostKeyChecking=no .env-docker ubuntu@%EC2_IP%:~/app/.env
scp -i %KEY_FILE% -o StrictHostKeyChecking=no docker-compose.yaml ubuntu@%EC2_IP%:~/app/docker-compose.yaml

REM 4. Buildar e rodar app
ssh -i %KEY_FILE% -o StrictHostKeyChecking=no ubuntu@%EC2_IP% "mkdir -p ~/app"
ssh -i %KEY_FILE% -o StrictHostKeyChecking=no ubuntu@%EC2_IP% "cd ~/app"
ssh -i %KEY_FILE% -o StrictHostKeyChecking=no ubuntu@%EC2_IP% "sudo docker-compose version"
REM caso seja necessário, descomentar as linhas abaixo para limpar imagens antigas para evitar problemas de espaço
REM ssh -i %KEY_FILE% -o StrictHostKeyChecking=no ubuntu@%EC2_IP% "docker container prune -f"
REM ssh -i %KEY_FILE% -o StrictHostKeyChecking=no ubuntu@%EC2_IP% "docker image prune -a -f"
REM ssh -i %KEY_FILE% -o StrictHostKeyChecking=no ubuntu@%EC2_IP% "docker volume prune -f"
REM ssh -i %KEY_FILE% -o StrictHostKeyChecking=no ubuntu@%EC2_IP% "docker network prune -f"
ssh -i %KEY_FILE% -o StrictHostKeyChecking=no ubuntu@%EC2_IP% "cd ~/app && docker build -t requirements-cache:latest ."
ssh -i %KEY_FILE% -o StrictHostKeyChecking=no ubuntu@%EC2_IP% "sudo docker-compose -f ~/app/docker-compose.yaml build"
ssh -i %KEY_FILE% -o StrictHostKeyChecking=no ubuntu@%EC2_IP% "sudo docker-compose -f ~/app/docker-compose.yaml up -d --remove-orphans"

REM 5. Remover arquivos temporários se existirem
if exist instance_public_ip.txt del instance_public_ip.txt
if exist app_server_key.pem del app_server_key.pem

echo Deploy finalizado.
echo Acesse dashboard: http://%dashboard_url%
echo Acesse api: http://%api_url%
pause
