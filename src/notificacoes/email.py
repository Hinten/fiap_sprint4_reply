import boto3
import os

SNS_TOPIC_ARN = os.environ['SNS_TOPIC_ARN']
SNS_REGION = os.environ['SNS_REGION']
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')

# Cria cliente do SNS, usando credenciais se fornecidas
if AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY:
    sns = boto3.client(
        "sns",
        region_name=SNS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )
else:
    sns = boto3.client("sns", region_name=SNS_REGION)

def enviar_email(assunto, mensagem):
    response = sns.publish(
        TopicArn=SNS_TOPIC_ARN,
        Subject=assunto,
        Message=mensagem
    )
    return response

if __name__ == "__main__":
    assunto = "Notificação de Teste"
    mensagem = "Olá! Esse é um e-mail enviado via Amazon SNS com boto3."
    resp = enviar_email(assunto, mensagem)
    print("Mensagem enviada! ID:", resp["MessageId"])
