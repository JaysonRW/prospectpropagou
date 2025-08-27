
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import pandas as pd
from models import Business, ScrapingSession, SessionLocal, init_db
from datetime import datetime
import logging
import os

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GoogleMapsScraper:
    def __init__(self, headless=True):
        self.headless = headless
        self.driver = None
        self.setup_driver()
        
    def setup_driver(self):
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
    def search_businesses(self, keyword, max_results=50):
        """Busca negócios no Google Maps"""
        search_query = f"{keyword} Curitiba"
        url = f"https://www.google.com/maps/search/{search_query.replace(' ', '+')}"
        
        logger.info(f"Buscando: {search_query}")
        self.driver.get(url)
        
        # Aguardar carregamento
        time.sleep(5)
        
        businesses = []
        processed_names = set()
        
        try:
            # Scroll para carregar mais resultados
            self.scroll_results(max_results)
            
            # Encontrar todos os resultados
            results = self.driver.find_elements(By.CSS_SELECTOR, '[data-result-index]')
            logger.info(f"Encontrados {len(results)} resultados iniciais")
            
            for i, result in enumerate(results[:max_results]):
                try:
                    # Clicar no resultado para abrir detalhes
                    self.driver.execute_script("arguments[0].click();", result)
                    time.sleep(random.uniform(2, 4))
                    
                    business_data = self.extract_business_data()
                    
                    if business_data and business_data['name'] not in processed_names:
                        business_data['scraped_keyword'] = keyword
                        businesses.append(business_data)
                        processed_names.add(business_data['name'])
                        logger.info(f"Extraído: {business_data['name']}")
                    
                    # Pequena pausa entre extrações
                    time.sleep(random.uniform(1, 2))
                    
                except Exception as e:
                    logger.error(f"Erro ao processar resultado {i}: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.error(f"Erro durante scraping: {str(e)}")
            
        return businesses
    
    def scroll_results(self, max_results):
        """Scroll na lista de resultados para carregar mais"""
        try:
            results_panel = self.driver.find_element(By.CSS_SELECTOR, '[role="main"]')
            
            last_height = self.driver.execute_script("return arguments[0].scrollHeight", results_panel)
            scroll_attempts = 0
            max_scrolls = max_results // 10  # Aproximadamente 10 resultados por scroll
            
            while scroll_attempts < max_scrolls:
                # Scroll down
                self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", results_panel)
                time.sleep(3)
                
                # Verificar se carregou mais conteúdo
                new_height = self.driver.execute_script("return arguments[0].scrollHeight", results_panel)
                if new_height == last_height:
                    break
                    
                last_height = new_height
                scroll_attempts += 1
                
        except Exception as e:
            logger.error(f"Erro durante scroll: {str(e)}")
    
    def extract_business_data(self):
        """Extrai dados do negócio da página de detalhes"""
        try:
            business_data = {
                'name': '',
                'phone': '',
                'address': '',
                'category': '',
                'rating': 0.0,
                'reviews_count': 0,
                'website': ''
            }
            
            # Nome do negócio
            try:
                name_element = self.driver.find_element(By.CSS_SELECTOR, 'h1[data-attrid="title"]')
                business_data['name'] = name_element.text.strip()
            except:
                try:
                    name_element = self.driver.find_element(By.CSS_SELECTOR, '[data-section-id="oh"] h1')
                    business_data['name'] = name_element.text.strip()
                except:
                    pass
            
            # Telefone
            try:
                phone_elements = self.driver.find_elements(By.CSS_SELECTOR, '[data-item-id*="phone"]')
                for element in phone_elements:
                    phone_text = element.get_attribute('data-item-id')
                    if 'phone:tel:' in phone_text:
                        business_data['phone'] = phone_text.replace('phone:tel:', '')
                        break
            except:
                pass
            
            # Endereço
            try:
                address_element = self.driver.find_element(By.CSS_SELECTOR, '[data-item-id="address"]')
                business_data['address'] = address_element.text.strip()
            except:
                pass
            
            # Categoria
            try:
                category_element = self.driver.find_element(By.CSS_SELECTOR, '[jsaction*="category"]')
                business_data['category'] = category_element.text.strip()
            except:
                pass
            
            # Rating e reviews
            try:
                rating_element = self.driver.find_element(By.CSS_SELECTOR, '[jsaction*="pane.rating"]')
                rating_text = rating_element.text
                if rating_text:
                    parts = rating_text.split()
                    if len(parts) >= 1:
                        business_data['rating'] = float(parts[0].replace(',', '.'))
                    if len(parts) >= 2:
                        reviews_text = parts[1].replace('(', '').replace(')', '').replace('.', '')
                        business_data['reviews_count'] = int(reviews_text) if reviews_text.isdigit() else 0
            except:
                pass
            
            # Website
            try:
                website_element = self.driver.find_element(By.CSS_SELECTOR, '[data-item-id*="authority"]')
                business_data['website'] = website_element.get_attribute('href')
            except:
                pass
            
            return business_data if business_data['name'] else None
            
        except Exception as e:
            logger.error(f"Erro ao extrair dados: {str(e)}")
            return None
    
    def save_to_database(self, businesses, keyword):
        """Salva os dados no banco"""
        db = SessionLocal()
        try:
            session = ScrapingSession(
                keyword=keyword,
                total_found=len(businesses),
                successful_scrapes=0,
                started_at=datetime.now()
            )
            db.add(session)
            db.commit()
            
            successful = 0
            for business_data in businesses:
                try:
                    # Verificar se já existe
                    existing = db.query(Business).filter_by(
                        name=business_data['name'],
                        phone=business_data['phone']
                    ).first()
                    
                    if not existing:
                        business = Business(**business_data)
                        db.add(business)
                        successful += 1
                    
                except Exception as e:
                    logger.error(f"Erro ao salvar negócio: {str(e)}")
                    continue
            
            session.successful_scrapes = successful
            session.completed_at = datetime.now()
            session.status = 'completed'
            db.commit()
            
            logger.info(f"Salvos {successful} novos negócios no banco")
            return successful
            
        except Exception as e:
            logger.error(f"Erro ao salvar no banco: {str(e)}")
            return 0
        finally:
            db.close()
    
    def export_to_excel(self, filename=None):
        """Exporta dados para Excel"""
        if not filename:
            filename = f"export/negocios_curitiba_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        os.makedirs('export', exist_ok=True)
        
        db = SessionLocal()
        try:
            businesses = db.query(Business).all()
            
            data = []
            for business in businesses:
                data.append({
                    'Nome': business.name,
                    'Telefone': business.phone,
                    'Endereço': business.address,
                    'Categoria': business.category,
                    'Avaliação': business.rating,
                    'Número de Avaliações': business.reviews_count,
                    'Website': business.website,
                    'Palavra-chave': business.scraped_keyword,
                    'Data Captura': business.created_at.strftime('%d/%m/%Y %H:%M')
                })
            
            df = pd.DataFrame(data)
            df.to_excel(filename, index=False)
            logger.info(f"Dados exportados para {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Erro ao exportar: {str(e)}")
            return None
        finally:
            db.close()
    
    def close(self):
        if self.driver:
            self.driver.quit()

def run_scraping(keywords, max_results_per_keyword=50):
    """Função principal para executar o scraping"""
    init_db()
    scraper = GoogleMapsScraper(headless=True)
    
    all_businesses = []
    
    try:
        for keyword in keywords:
            logger.info(f"Iniciando scraping para: {keyword}")
            businesses = scraper.search_businesses(keyword, max_results_per_keyword)
            
            if businesses:
                saved_count = scraper.save_to_database(businesses, keyword)
                all_businesses.extend(businesses)
                logger.info(f"Concluído {keyword}: {len(businesses)} encontrados, {saved_count} salvos")
            
            # Pausa entre keywords
            time.sleep(random.uniform(5, 10))
        
        # Exportar para Excel
        excel_file = scraper.export_to_excel()
        
        return {
            'total_businesses': len(all_businesses),
            'excel_file': excel_file,
            'success': True
        }
        
    except Exception as e:
        logger.error(f"Erro durante scraping: {str(e)}")
        return {
            'total_businesses': 0,
            'excel_file': None,
            'success': False,
            'error': str(e)
        }
    finally:
        scraper.close()

if __name__ == "__main__":
    # Teste com algumas categorias
    test_keywords = [
        "restaurantes",
        "salão de beleza",
        "loja de roupas",
        "oficina mecânica",
        "padaria"
    ]
    
    result = run_scraping(test_keywords, max_results_per_keyword=20)
    print(f"Resultado: {result}")
