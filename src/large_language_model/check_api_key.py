import os

def check_api_key():
    """
    Verifica se a variável de ambiente GEMINI_API está definida.
    :raises SystemExit: Se a variável de ambiente não estiver definida.
    """
    api_key = os.getenv("GEMINI_API")
    if not api_key:
        raise SystemExit("GEMINI_API não definida")
    print("GEMINI_API disponível")


if __name__ == "__main__":
    check_api_key()