
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from models import Business, MessageLog, SessionLocal, init_db
from datetime import datetime
import logging
import os
import urllib.parse

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WhatsAppSender:
    def __init__(self, headless=False):
        self.headless = headless
        self.driver = None
        self.setup_driver()
        self.message_template = """Olá {nome},

Seu negócio em Curitiba merece mais do que apenas ser encontrado. Ele merece ser descoberto por clientes prontos para comprar, que buscam ativamente o que você oferece, bem aqui na sua região.

Você já usa o Google Meu Negócio? Ótimo! Ele ajuda a ser visto. Mas e se eu te disser que existe uma forma de ir além, de alcançar um público que já está buscando soluções locais e específicas, com um suporte personalizado que o Google não oferece?

No Propagou Negócios, nós não apenas listamos sua empresa; nós a promovemos ativamente para um público engajado em Curitiba e região. Nos últimos 90 dias, tivemos mais de 3.900 visitantes únicos e 4.100 pageviews, com um crescimento de mais de 23%!

Isso significa que seu anúncio estará em um ambiente onde as pessoas já estão com a intenção de compra, buscando guias de empregos, informações sobre bairros e listas de serviços – ou seja, clientes qualificados esperando para te encontrar.

Quer saber como podemos levar seu negócio para o próximo nível e transformar essa visibilidade em vendas reais? É rápido e sem compromisso.

Responda a esta mensagem ou clique no link para conversarmos:
https://wa.me/5541995343245

Atenciosamente,
Equipe Propagou Negócios"""
        
    def setup_driver(self):
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        # Usar perfil persistente para manter login do WhatsApp
        profile_path = os.path.abspath("data/chrome_profile")
        os.makedirs(profile_path, exist_ok=True)
        chrome_options.add_argument(f"--user-data-dir={profile_path}")
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
    def login_whatsapp(self):
        """Abre WhatsApp Web e aguarda login"""
        logger.info("Abrindo WhatsApp Web...")
        self.driver.get("https://web.whatsapp.com")
        
        try:
            # Aguardar até que o QR code apareça ou já esteja logado
            WebDriverWait(self.driver, 30).until(
                lambda driver: driver.find_elements(By.CSS_SELECTOR, '[data-testid="qr-code"]') or 
                              driver.find_elements(By.CSS_SELECTOR, '[data-testid="chat-list"]')
            )
            
            # Verificar se precisa escanear QR code
            if self.driver.find_elements(By.CSS_SELECTOR, '[data-testid="qr-code"]'):
                logger.info("QR Code detectado. Por favor, escaneie com seu celular.")
                logger.info("Aguardando login...")
                
                # Aguardar até estar logado (chat list aparecer)
                WebDriverWait(self.driver, 120).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="chat-list"]'))
                )
                
            logger.info("Login realizado com sucesso!")
            time.sleep(3)
            return True
            
        except TimeoutException:
            logger.error("Timeout ao fazer login no WhatsApp")
            return False
        except Exception as e:
            logger.error(f"Erro ao fazer login: {str(e)}")
            return False
    
    def send_message_to_number(self, phone, message):
        """Envia mensagem para um número específico"""
        try:
            # Limpar número (remover caracteres especiais)
            clean_phone = ''.join(filter(str.isdigit, phone))
            
            # Adicionar código do país se não tiver
            if not clean_phone.startswith('55'):
                clean_phone = '55' + clean_phone
            
            # URL do WhatsApp com número
            url = f"https://web.whatsapp.com/send?phone={clean_phone}"
            logger.info(f"Enviando mensagem para: {clean_phone}")
            
            self.driver.get(url)
            
            # Aguardar carregar a conversa
            try:
                WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="compose-box-input"]'))
                )
            except TimeoutException:
                # Tentar seletor alternativo
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '[contenteditable="true"]'))
                )
            
            # Encontrar caixa de texto
            try:
                text_box = self.driver.find_element(By.CSS_SELECTOR, '[data-testid="compose-box-input"]')
            except:
                text_box = self.driver.find_element(By.CSS_SELECTOR, '[contenteditable="true"]')
            
            # Limpar e digitar mensagem
            text_box.clear()
            text_box.send_keys(message)
            
            # Aguardar um pouco antes de enviar
            time.sleep(2)
            
            # Enviar mensagem
            text_box.send_keys(Keys.ENTER)
            
            # Aguardar confirmação de envio
            time.sleep(3)
            
            logger.info(f"Mensagem enviada para {clean_phone}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem para {phone}: {str(e)}")
            return False
    
    def send_bulk_messages(self, businesses, messages_per_hour=10, test_mode=False):
        """Envia mensagens em lote com controle de velocidade"""
        if not self.login_whatsapp():
            return {'success': False, 'error': 'Falha no login do WhatsApp'}
        
        db = SessionLocal()
        results = {
            'total_attempted': 0,
            'successful_sends': 0,
            'failed_sends': 0,
            'errors': []
        }
        
        # Calcular intervalo entre mensagens (em segundos)
        interval = 3600 / messages_per_hour  # 3600 segundos = 1 hora
        
        try:
            for business in businesses:
                if not business.phone:
                    continue
                
                results['total_attempted'] += 1
                
                # Verificar se já foi enviada mensagem
                existing_log = db.query(MessageLog).filter_by(
                    business_id=business.id,
                    message_sent=True
                ).first()
                
                if existing_log:
                    logger.info(f"Mensagem já enviada para {business.name}")
                    continue
                
                # Personalizar mensagem
                personalized_message = self.message_template.format(
                    nome=business.name.split()[0] if business.name else "Empresário"
                )
                
                # Criar log da tentativa
                message_log = MessageLog(
                    business_id=business.id,
                    business_name=business.name,
                    phone=business.phone,
                    message_sent=False
                )
                
                if test_mode:
                    logger.info(f"MODO TESTE - Mensagem para {business.name} ({business.phone})")
                    message_log.message_sent = True
                    message_log.sent_at = datetime.now()
                    results['successful_sends'] += 1
                else:
                    # Enviar mensagem real
                    success = self.send_message_to_number(business.phone, personalized_message)
                    
                    if success:
                        message_log.message_sent = True
                        message_log.sent_at = datetime.now()
                        results['successful_sends'] += 1
                        logger.info(f"✓ Mensagem enviada para {business.name}")
                    else:
                        message_log.error_message = "Falha no envio"
                        results['failed_sends'] += 1
                        results['errors'].append(f"Falha ao enviar para {business.name}")
                
                db.add(message_log)
                db.commit()
                
                # Aguardar intervalo entre mensagens (exceto no modo teste)
                if not test_mode and results['total_attempted'] < len(businesses):
                    logger.info(f"Aguardando {interval:.1f} segundos...")
                    time.sleep(interval)
            
            results['success'] = True
            return results
            
        except Exception as e:
            logger.error(f"Erro durante envio em lote: {str(e)}")
            results['success'] = False
            results['error'] = str(e)
            return results
        finally:
            db.close()
    
    def get_businesses_for_messaging(self, limit=None, category_filter=None):
        """Busca negócios para envio de mensagens"""
        db = SessionLocal()
        try:
            query = db.query(Business).filter(Business.phone.isnot(None), Business.phone != '')
            
            if category_filter:
                query = query.filter(Business.category.contains(category_filter))
            
            # Excluir negócios que já receberam mensagem
            sent_business_ids = db.query(MessageLog.business_id).filter(MessageLog.message_sent == True).subquery()
            query = query.filter(~Business.id.in_(sent_business_ids))
            
            if limit:
                query = query.limit(limit)
            
            return query.all()
            
        finally:
            db.close()
    
    def close(self):
        if self.driver:
            self.driver.quit()

def run_message_campaign(max_messages=50, messages_per_hour=10, category_filter=None, test_mode=False):
    """Executa campanha de mensagens"""
    init_db()
    sender = WhatsAppSender(headless=False)  # Não usar headless para WhatsApp
    
    try:
        # Buscar negócios para envio
        businesses = sender.get_businesses_for_messaging(
            limit=max_messages,
            category_filter=category_filter
        )
        
        if not businesses:
            return {
                'success': False,
                'error': 'Nenhum negócio encontrado para envio de mensagens'
            }
        
        logger.info(f"Iniciando campanha para {len(businesses)} negócios")
        
        # Executar envio
        results = sender.send_bulk_messages(
            businesses=businesses,
            messages_per_hour=messages_per_hour,
            test_mode=test_mode
        )
        
        return results
        
    except Exception as e:
        logger.error(f"Erro na campanha: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }
    finally:
        sender.close()

if __name__ == "__main__":
    # Teste da campanha
    result = run_message_campaign(
        max_messages=5,
        messages_per_hour=12,
        test_mode=True
    )
    print(f"Resultado da campanha: {result}")
