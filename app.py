
from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, flash
import os
import json
import logging
from datetime import datetime
from config import get_config
from models import Business, MessageLog, ScrapingSession, SessionLocal, init_db
from scraper import run_scraping
from sender import run_message_campaign
import threading
import pandas as pd

# Configurar aplicação
config_class = get_config()
app = Flask(__name__)
app.config.from_object(config_class)

# Configurar logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=getattr(logging, app.config['LOG_LEVEL']),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(app.config['LOG_FILE']),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Inicializar banco de dados
init_db()

# Status global das operações
operation_status = {
    'scraping': {'running': False, 'progress': ''},
    'messaging': {'running': False, 'progress': ''}
}

@app.route('/')
def index():
    """Página principal"""
    db = SessionLocal()
    try:
        # Estatísticas gerais
        total_businesses = db.query(Business).count()
        total_with_phone = db.query(Business).filter(Business.phone.isnot(None), Business.phone != '').count()
        messages_sent = db.query(MessageLog).filter(MessageLog.message_sent == True).count()
        
        # Últimas sessões de scraping
        recent_sessions = db.query(ScrapingSession).order_by(ScrapingSession.started_at.desc()).limit(5).all()
        
        stats = {
            'total_businesses': total_businesses,
            'total_with_phone': total_with_phone,
            'messages_sent': messages_sent,
            'recent_sessions': recent_sessions
        }
        
        return render_template('index.html', stats=stats, status=operation_status)
        
    finally:
        db.close()

@app.route('/scraping')
def scraping_page():
    """Página de configuração do scraping"""
    return render_template('scraping.html', status=operation_status)

@app.route('/messaging')
def messaging_page():
    """Página de configuração de mensagens"""
    db = SessionLocal()
    try:
        # Buscar categorias disponíveis
        categories = db.query(Business.category).distinct().filter(Business.category.isnot(None)).all()
        categories = [cat[0] for cat in categories if cat[0]]
        
        # Negócios disponíveis para mensagem
        available_businesses = db.query(Business).filter(
            Business.phone.isnot(None), 
            Business.phone != ''
        ).count()
        
        # Negócios que já receberam mensagem
        sent_messages = db.query(MessageLog).filter(MessageLog.message_sent == True).count()
        
        return render_template('messaging.html', 
                             categories=categories,
                             available_businesses=available_businesses,
                             sent_messages=sent_messages,
                             status=operation_status)
    finally:
        db.close()

@app.route('/reports')
def reports_page():
    """Página de relatórios"""
    db = SessionLocal()
    try:
        # Dados para relatórios
        businesses_by_category = db.query(Business.category, db.func.count(Business.id)).group_by(Business.category).all()
        
        # Mensagens por dia
        messages_by_date = db.query(
            db.func.date(MessageLog.sent_at),
            db.func.count(MessageLog.id)
        ).filter(MessageLog.message_sent == True).group_by(db.func.date(MessageLog.sent_at)).all()
        
        return render_template('reports.html',
                             businesses_by_category=businesses_by_category,
                             messages_by_date=messages_by_date)
    finally:
        db.close()

@app.route('/api/start_scraping', methods=['POST'])
def start_scraping():
    """Inicia processo de scraping"""
    if operation_status['scraping']['running']:
        return jsonify({'success': False, 'error': 'Scraping já está em execução'})
    
    data = request.json
    keywords = data.get('keywords', [])
    max_results = int(data.get('max_results', 50))
    
    if not keywords:
        return jsonify({'success': False, 'error': 'Nenhuma palavra-chave fornecida'})
    
    def run_scraping_thread():
        operation_status['scraping']['running'] = True
        operation_status['scraping']['progress'] = 'Iniciando scraping...'
        
        try:
            result = run_scraping(keywords, max_results)
            operation_status['scraping']['progress'] = f"Concluído: {result.get('total_businesses', 0)} negócios encontrados"
        except Exception as e:
            operation_status['scraping']['progress'] = f"Erro: {str(e)}"
        finally:
            operation_status['scraping']['running'] = False
    
    thread = threading.Thread(target=run_scraping_thread)
    thread.start()
    
    return jsonify({'success': True, 'message': 'Scraping iniciado'})

@app.route('/api/start_messaging', methods=['POST'])
def start_messaging():
    """Inicia campanha de mensagens"""
    if operation_status['messaging']['running']:
        return jsonify({'success': False, 'error': 'Campanha já está em execução'})
    
    data = request.json
    max_messages = int(data.get('max_messages', 50))
    messages_per_hour = int(data.get('messages_per_hour', 10))
    category_filter = data.get('category_filter')
    test_mode = data.get('test_mode', False)
    
    def run_messaging_thread():
        operation_status['messaging']['running'] = True
        operation_status['messaging']['progress'] = 'Iniciando campanha...'
        
        try:
            result = run_message_campaign(
                max_messages=max_messages,
                messages_per_hour=messages_per_hour,
                category_filter=category_filter,
                test_mode=test_mode
            )
            
            if result['success']:
                operation_status['messaging']['progress'] = f"Concluído: {result['successful_sends']} mensagens enviadas"
            else:
                operation_status['messaging']['progress'] = f"Erro: {result.get('error', 'Erro desconhecido')}"
                
        except Exception as e:
            operation_status['messaging']['progress'] = f"Erro: {str(e)}"
        finally:
            operation_status['messaging']['running'] = False
    
    thread = threading.Thread(target=run_messaging_thread)
    thread.start()
    
    return jsonify({'success': True, 'message': 'Campanha iniciada'})

@app.route('/api/status')
def get_status():
    """Retorna status das operações"""
    return jsonify(operation_status)

@app.route('/api/export_excel')
def export_excel():
    """Exporta dados para Excel"""
    try:
        db = SessionLocal()
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
        filename = f"export/negocios_curitiba_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        os.makedirs('export', exist_ok=True)
        df.to_excel(filename, index=False)
        
        return send_file(filename, as_attachment=True)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    finally:
        db.close()

@app.route('/api/businesses')
def get_businesses():
    """API para listar negócios"""
    db = SessionLocal()
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        category = request.args.get('category')
        
        query = db.query(Business)
        
        if category:
            query = query.filter(Business.category.contains(category))
        
        total = query.count()
        businesses = query.offset((page - 1) * per_page).limit(per_page).all()
        
        data = []
        for business in businesses:
            data.append({
                'id': business.id,
                'name': business.name,
                'phone': business.phone,
                'address': business.address,
                'category': business.category,
                'rating': business.rating,
                'reviews_count': business.reviews_count,
                'created_at': business.created_at.strftime('%d/%m/%Y %H:%M')
            })
        
        return jsonify({
            'businesses': data,
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': (total + per_page - 1) // per_page
        })
        
    finally:
        db.close()

if __name__ == '__main__':
    logger.info(f"Iniciando aplicação em modo {app.config.get('FLASK_ENV', 'development')}")
    app.run(
        host=app.config['HOST'], 
        port=app.config['PORT'], 
        debug=app.config['DEBUG']
    )
