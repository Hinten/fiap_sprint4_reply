import streamlit as st
from src.notificacoes.email import enviar_email

def enviar_email_teste():

    assunto = st.text_input(label="Assunto", value="Manutenção Programada")
    mensagem = st.text_area(label="Mensagem", value="Prezado usuário, informamos que nossa Inteligência Artificial detectou que é necessário realizar uma manutenção programada no equipamento X. A manutenção ocorrerá no dia DD/MM/YYYY, das HH:MM as HH:MM (horário de Brasília). Pedimos desculpas por qualquer inconveniente e agradecemos pela compreensão.")

    if st.button("Enviar E-mail de Teste"):
        resposta = enviar_email(assunto, mensagem)
        st.success(f"E-mail enviado com sucesso! ID da Mensagem: {resposta['MessageId']}")
