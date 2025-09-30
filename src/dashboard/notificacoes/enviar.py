import streamlit as st
from src.notificacoes.email import enviar_email
import os

SNS_TOPIC_ARN = os.environ.get('SNS_TOPIC_ARN')
SNS_REGION = os.environ.get('SNS_REGION')
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')


def enviar_email_teste():

    st.write(SNS_TOPIC_ARN)
    st.write(SNS_REGION)
    st.write(AWS_ACCESS_KEY_ID)
    st.write(AWS_SECRET_ACCESS_KEY)

    assunto = st.text_input(label="Assunto", value="Manutenção Programada")
    mensagem = st.text_area(label="Mensagem", value="Prezado usuário, informamos que nossa Inteligência Artificial detectou que é necessário realizar uma manutenção programada no equipamento X. A manutenção ocorrerá no dia DD/MM/YYYY, das HH:MM as HH:MM (horário de Brasília). Pedimos desculpas por qualquer inconveniente e agradecemos pela compreensão.")

    if st.button("Enviar E-mail de Teste"):
        resposta = enviar_email(assunto, mensagem)
        st.success(f"E-mail enviado com sucesso! ID da Mensagem: {resposta['MessageId']}")
