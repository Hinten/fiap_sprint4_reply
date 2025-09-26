@echo off
REM Script para deploy do app server via SSH
REM Pré-requisitos: terraform, aws cli, scp, ssh instalados
REM aws cli já deve estar com as credenciais configuradas

REM 1. Ir para o diretório do Terraform e salvar outputs corretamente
pushd iac\dev
terraform output -raw instance_public_ip > ..\..\instance_public_ip.txt
terraform output -raw app_server_private_key > ..\..\app_server_key.pem
popd

REM 2. Ler IP e definir arquivo de chave
set /p EC2_IP=<instance_public_ip.txt
set KEY_FILE=app_server_key.pem

REM 3. Copiar o dockerfile e o app para o servidor
REM PQ fazer isso? A imagem do docker buildada tem 1.6GB por conta do pycaret. Esta forma não é a mais correta, porém é muito rápido, bom para testar

scp -i %KEY_FILE% -o StrictHostKeyChecking=no Dockerfile ubuntu@%EC2_IP%:~/app/Dockerfile

REM 4. Conectar via SSH e instalar Docker, buildar e rodar app
ssh -i %KEY_FILE% -o StrictHostKeyChecking=no ubuntu@%EC2_IP% "sudo apt-get update && sudo apt-get install -y docker.io && sudo usermod -aG docker ubuntu && cd ~/app && sudo docker build -t streamlit-app . && sudo docker run -d -p 8501:8501 streamlit-app streamlit run main_dash.py --server.address=0.0.0.0 --server.port=8501"

echo Deploy finalizado. Acesse: http://%EC2_IP%:8501
pause
