@echo off
REM Script para buildar e subir imagem Docker para AWS ECR

REM Obtém o AWS Account ID automaticamente
for /f "delims=" %%i in ('aws sts get-caller-identity --query Account --output text') do set AWS_ACCOUNT_ID=%%i
set AWS_REGION=us-east-1
set REPO_NAME=streamlit-app
set IMAGE_TAG=latest

REM Login no ECR
aws ecr get-login-password --region %AWS_REGION% | docker login --username AWS --password-stdin %AWS_ACCOUNT_ID%.dkr.ecr.%AWS_REGION%.amazonaws.com

REM Build da imagem Docker
if exist Dockerfile (
    docker build -t %REPO_NAME%:latest .
) else (
    echo Dockerfile não encontrado!
    exit /b 1
)

REM Tag da imagem para o ECR
set ECR_IMAGE=%AWS_ACCOUNT_ID%.dkr.ecr.%AWS_REGION%.amazonaws.com/%REPO_NAME%:%IMAGE_TAG%
docker tag %REPO_NAME%:latest %ECR_IMAGE%

REM Push da imagem para o ECR
docker push %ECR_IMAGE%

echo Imagem enviada para o ECR: %ECR_IMAGE%
pause
