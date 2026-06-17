import os
import logging
import requests
from dotenv import load_dotenv
from supabase import create_client, Client

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
ZAPI_INSTANCE_ID = os.getenv("ZAPI_INSTANCE_ID")
ZAPI_TOKEN = os.getenv("ZAPI_TOKEN")

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    logging.error(f"Erro ao inicializar o Supabase: {e}")
    exit(1)

def get_contacts():

    logging.info("Buscando contatos no Supabase...")
    try:
        response = supabase.table("contatos").select("*").execute()
        
        contatos = response.data
        logging.info(f"{len(contatos)} contato(s) encontrado(s).")
        return contatos
    except Exception as e:
        logging.error(f"Erro ao buscar contatos no banco: {e}")
        return []

def send_whatsapp_message(nome, telefone):
    
    url = f"https://api.z-api.io/instances/{ZAPI_INSTANCE_ID}/token/{ZAPI_TOKEN}/send-text"
    
    mensagem = f"Olá, {nome} tudo bem com você?"
    
    payload = {
        "phone": telefone,
        "message": mensagem
    }
    
    logging.info(f"Enviando mensagem para {nome} ({telefone})...")
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status() 
        
        logging.info(f"Mensagem enviada com sucesso para {nome}!")
    except requests.exceptions.RequestException as e:
        logging.error(f"Falha ao enviar mensagem para {nome}: {e}")

def main():

    logging.info("Iniciando rotina de mensagens b2bflow...")
    
    contatos = get_contacts()
    
    if not contatos:
        logging.warning("Nenhum contato para enviar mensagens. Encerrando rotina.")
        return

    for contato in contatos:
        nome = contato.get("nome_contato")
        telefone = contato.get("telefone")
        
        if nome and telefone:
            send_whatsapp_message(nome, telefone)
        else:
            logging.warning(f"Contato inválido ou com dados faltando ignorado: {contato}")
            
    logging.info("Rotina de mensagens finalizada.")

main()