import boto3
import os

SNS_TOPIC_ARN = os.environ.get('SNS_TOPIC_ARN')
SNS_REGION = os.environ.get('SNS_REGION')


def enviar_email(assunto, mensagem):
    sns = boto3.client("sns", region_name=SNS_REGION)
    response = sns.publish(
        TopicArn=SNS_TOPIC_ARN,
        Subject=assunto,
        Message=mensagem
    )
    return response

def subscribe_email(email):
    sns = boto3.client("sns", region_name=SNS_REGION)
    response = sns.subscribe(
        TopicArn=SNS_TOPIC_ARN,
        Protocol='email',
        Endpoint=email
    )
    return response

if __name__ == "__main__":
    assunto = "Notificação de Teste"
    mensagem = "Olá! Esse é um e-mail enviado via Amazon SNS com boto3."
    resp = enviar_email(assunto, mensagem)
    print("Mensagem enviada! ID:", resp["MessageId"])
