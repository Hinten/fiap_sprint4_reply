"""
Tool for sending email notifications to users.
Uses AWS SNS to send email alerts about equipment status, maintenance, or critical readings.
"""
from src.large_language_model.tipos_base.base_tools import BaseTool
from src.notificacoes.email import enviar_email
import os


def enviar_notificacao(assunto: str, mensagem: str) -> str:
    """
    Envia uma notificação por e-mail usando AWS SNS.
    
    Envia e-mails para os endereços cadastrados no tópico SNS do sistema.
    Útil para alertar sobre leituras críticas, necessidade de manutenção,
    ou qualquer evento importante relacionado aos equipamentos.
    
    :param assunto: Assunto do e-mail (limite de 100 caracteres)
    :param mensagem: Corpo da mensagem do e-mail
    :return: String confirmando o envio ou mensagem de erro
    """
    try:
        # Verificar se as configurações SNS estão presentes
        sns_topic_arn = os.environ.get('SNS_TOPIC_ARN')
        sns_region = os.environ.get('SNS_REGION')
        
        if not sns_topic_arn or not sns_region:
            return ("⚠️ Notificações por e-mail não estão configuradas.\n"
                   "Configure as variáveis SNS_TOPIC_ARN e SNS_REGION no arquivo .env para habilitar notificações.")
        
        # Validar tamanho do assunto
        if len(assunto) > 100:
            assunto = assunto[:97] + "..."
        
        # Enviar e-mail via SNS
        response = enviar_email(assunto=assunto, mensagem=mensagem)
        
        if response and 'MessageId' in response:
            resultado = f"✅ Notificação enviada com sucesso!\n\n"
            resultado += f"📧 Assunto: {assunto}\n"
            resultado += f"📨 ID da Mensagem: {response['MessageId']}\n"
            resultado += f"📬 Destinatários: Inscritos no tópico SNS\n"
            return resultado
        else:
            return "⚠️ Notificação enviada, mas não foi possível confirmar o recebimento."
        
    except Exception as e:
        error_msg = str(e)
        
        # Provide helpful error messages for common issues
        if "credentials" in error_msg.lower():
            return ("❌ Erro de autenticação AWS.\n"
                   "Verifique as credenciais AWS (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN) no arquivo .env.")
        elif "not found" in error_msg.lower() or "does not exist" in error_msg.lower():
            return ("❌ Tópico SNS não encontrado.\n"
                   "Verifique se o SNS_TOPIC_ARN está correto no arquivo .env.")
        elif "region" in error_msg.lower():
            return ("❌ Erro de região AWS.\n"
                   "Verifique se SNS_REGION está configurado corretamente no arquivo .env.")
        else:
            return f"❌ Erro ao enviar notificação: {error_msg}"


class EnviarNotificacaoTool(BaseTool):
    """
    Ferramenta para enviar notificações por e-mail usando AWS SNS.
    Permite alertar usuários sobre eventos importantes do sistema.
    """
    
    @property
    def function_declaration(self):
        return enviar_notificacao
    
    def call_chat_display(self) -> str:
        return "📧 Enviando notificação por e-mail..."
    
    def call_result_display(self, result: str) -> str:
        return result
