import streamlit as st
from src.notificacoes.email import enviar_email, subscribe_email
import os

@st.fragment
def subscrever_email_fragment():

    email = st.text_input(label="E-mail para subscrição")

    if st.button("Subscrever E-mail"):

        if not email:
            st.error("Por favor, insira um e-mail válido.")
            return

        resposta = subscribe_email(email)
        st.warning(f"Um e-mail de confirmação foi enviado para {email}. Por favor, verifique sua caixa de entrada e confirme a subscrição.")

@st.fragment
def enviar_email_teste():

    st.title("📧 Enviar E-mail de Teste")
    st.write("Envie um e-mail de teste para verificar se o sistema de notificações está funcionando corretamente.")

    assunto = st.text_input(label="Assunto", value="Manutenção Programada - TESTE")
    mensagem = st.text_area(label="Mensagem", value="Prezado usuário, informamos que nossa Inteligência Artificial detectou que é necessário realizar uma manutenção programada no equipamento X. A manutenção ocorrerá no dia DD/MM/YYYY, das HH:MM as HH:MM (horário de Brasília). Pedimos desculpas por qualquer inconveniente e agradecemos pela compreensão.")

    if st.button("Enviar E-mail de Teste"):
        resposta = enviar_email(assunto, mensagem)
        st.success(f"E-mail enviado com sucesso! ID da Mensagem: {resposta['MessageId']}")

def subscrever_email_view():
    st.title("📧 Subscrever E-mail")
    st.write("Insira seu e-mail abaixo para receber notificações e alertas automáticos do sistema.")
    subscrever_email_fragment()

    st.divider()

    enviar_email_teste()

subscrever_email_page = st.Page(
    subscrever_email_view,
    title="Subscrever E-mail",
    icon="📧",
)