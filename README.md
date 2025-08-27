# 🚀 Automação de Prospecção - Curitiba

Sistema completo de automação para prospecção de negócios em Curitiba usando Google Maps e WhatsApp Web.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)
![Selenium](https://img.shields.io/badge/Selenium-4.25+-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ Funcionalidades

### 🔍 **Scraping Inteligente**
- ✅ Busca automatizada no Google Maps
- ✅ Extração de dados completos (nome, telefone, endereço, categoria, avaliações)
- ✅ Filtros avançados por categoria e localização
- ✅ Sistema de sessões para controle de progresso
- ✅ Rate limiting para evitar bloqueios

### 📱 **Campanhas de Mensagens**
- ✅ Integração com WhatsApp Web
- ✅ Campanhas automatizadas com controle de velocidade
- ✅ Personalização de mensagens por categoria
- ✅ Modo de teste para validação
- ✅ Logs detalhados de envios

### 📊 **Dashboard Profissional**
- ✅ Interface web moderna e intuitiva
- ✅ Estatísticas em tempo real
- ✅ Relatórios de performance detalhados
- ✅ Exportação para Excel
- ✅ Monitoramento de operações

### 🛡️ **Recursos de Segurança**
- ✅ Configurações flexíveis por ambiente
- ✅ Logs detalhados de todas as operações
- ✅ Modo headless para servidores
- ✅ Proteção contra rate limiting

## 🚀 Instalação Rápida

### Método 1: Script Automático (Recomendado)

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/automacao-prospeccao.git
cd automacao-prospeccao

# Execute o script de instalação
chmod +x start.sh
./start.sh
```

### Método 2: Instalação Manual

```bash
# 1. Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou venv\Scripts\activate  # Windows

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Configurar ambiente
cp .env.example .env
# Edite o arquivo .env conforme necessário

# 4. Criar diretórios necessários
mkdir -p data logs export

# 5. Executar aplicação
python app.py
```

## ⚙️ Configuração

### Configuração Básica

1. **Copie o arquivo de configuração:**
```bash
cp .env.example .env
```

2. **Edite as configurações principais:**
```env
# Configurações do Flask
FLASK_ENV=development
FLASK_DEBUG=true
SECRET_KEY=sua_chave_secreta_super_segura_aqui

# Banco de dados
DATABASE_URL=sqlite:///data/prospeccao.db

# Selenium (para scraping)
SELENIUM_HEADLESS=true

# Rate limiting (importante!)
MAX_MESSAGES_PER_HOUR=10
MAX_SCRAPING_RESULTS=100
```

### Configuração para Servidor/VPS

Para usar em servidor próprio:

```bash
# 1. Configurar para produção
export FLASK_ENV=production

# 2. Usar Gunicorn (mais estável)
./start.sh production

# 3. Ou instalar como serviço
sudo cp automacao-prospeccao.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable automacao-prospeccao
sudo systemctl start automacao-prospeccao
```

## 💻 Como Usar

### Interface Web

1. **Acesse:** `http://localhost:5000`
2. **Dashboard:** Visualize estatísticas gerais
3. **Captura de Dados:** Configure palavras-chave e execute scraping
4. **Envio de Mensagens:** Configure campanhas de WhatsApp
5. **Relatórios:** Analise resultados e exporte dados

### Fluxo de Trabalho Típico

1. **Configurar Palavras-chave** → Defina termos de busca
2. **Executar Scraping** → Colete dados do Google Maps
3. **Revisar Dados** → Verifique qualidade dos dados
4. **Configurar Campanha** → Defina mensagens e filtros
5. **Enviar Mensagens** → Execute campanha no WhatsApp
6. **Analisar Resultados** → Monitore performance

## 🤖 Integração com Code LLM

### 1. **Análise Inteligente de Dados**

```python
# Exemplo de integração com LLM para análise
def analyze_business_data_with_llm(businesses):
    prompt = f"""
    Analise os seguintes dados de {len(businesses)} negócios coletados:
    
    Dados: {businesses}
    
    Forneça insights sobre:
    1. Melhores horários para contato por categoria
    2. Padrões geográficos interessantes
    3. Oportunidades de mercado identificadas
    4. Sugestões de segmentação
    """
    return llm_client.generate(prompt)
```

### 2. **Geração de Mensagens Personalizadas**

```python
def generate_personalized_message(business_data):
    prompt = f"""
    Crie uma mensagem de prospecção profissional para:
    
    Nome: {business_data['name']}
    Categoria: {business_data['category']}
    Localização: {business_data['address']}
    Avaliação: {business_data['rating']} estrelas
    
    A mensagem deve:
    - Ser personalizada e relevante
    - Mencionar algo específico sobre o negócio
    - Ter tom profissional mas amigável
    - Incluir uma proposta de valor clara
    - Ter no máximo 160 caracteres
    """
    return llm_client.generate(prompt)
```

### 3. **Otimização de Campanhas**

```python
def optimize_campaign_with_llm(campaign_results):
    prompt = f"""
    Analise os resultados da campanha:
    
    {campaign_results}
    
    Sugira otimizações para:
    1. Timing de envios
    2. Segmentação de público
    3. Personalização de mensagens
    4. Taxa de conversão
    """
    return llm_client.generate(prompt)
```

## 🔧 API Endpoints

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/api/businesses` | GET | Listar negócios com paginação |
| `/api/start_scraping` | POST | Iniciar processo de scraping |
| `/api/start_messaging` | POST | Iniciar campanha de mensagens |
| `/api/status` | GET | Status das operações em tempo real |
| `/api/export_excel` | GET | Exportar dados para Excel |

### Exemplo de Uso da API

```python
import requests

# Iniciar scraping
response = requests.post('http://localhost:5000/api/start_scraping', json={
    'keywords': ['restaurante', 'pizzaria', 'lanchonete'],
    'max_results': 50
})

# Verificar status
status = requests.get('http://localhost:5000/api/status').json()
print(f"Scraping: {status['scraping']['progress']}")
```

## 🐳 Deploy com Docker

```dockerfile
FROM python:3.11-slim

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

# Criar diretórios
RUN mkdir -p data logs export

# Expor porta
EXPOSE 5000

# Comando de inicialização
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "app:app"]
```

```bash
# Build e run
docker build -t automacao-prospeccao .
docker run -p 5000:5000 -v $(pwd)/data:/app/data automacao-prospeccao
```

## 🛠️ Troubleshooting

### Problemas Comuns e Soluções

#### ❌ Chrome/Chromium não encontrado
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install chromium-browser

# CentOS/RHEL
sudo yum install chromium

# macOS
brew install --cask google-chrome
```

#### ❌ Erro de permissões
```bash
chmod +x start.sh
sudo chown -R $USER:$USER .
```

#### ❌ WhatsApp não conecta
1. Verifique se WhatsApp Web funciona no navegador
2. Limpe cache e cookies
3. Reinicie a aplicação
4. Verifique logs em `logs/app.log`

#### ❌ Banco de dados corrompido
```bash
# Backup dos dados (se necessário)
cp data/prospeccao.db data/prospeccao.db.backup

# Recriar banco
rm data/prospeccao.db
python app.py
```

#### ❌ Selenium WebDriver issues
```bash
# Atualizar WebDriver
pip install --upgrade webdriver-manager

# Verificar versão do Chrome
google-chrome --version
```

## 📁 Estrutura do Projeto

```
automacao_prospeccao/
├── 📄 app.py                    # Aplicação principal Flask
├── ⚙️ config.py                 # Configurações por ambiente
├── 🗄️ models.py                 # Modelos do banco de dados
├── 🕷️ scraper.py                # Lógica de scraping Google Maps
├── 📱 sender.py                 # Lógica de envio WhatsApp
├── 📋 requirements.txt          # Dependências Python
├── 🚀 start.sh                  # Script de inicialização
├── 🔧 automacao-prospeccao.service # Serviço systemd
├── 📝 .env.example              # Exemplo de configuração
├── 🚫 .gitignore                # Arquivos ignorados pelo Git
├── 📁 templates/                # Templates HTML
│   ├── base.html
│   ├── index.html
│   ├── scraping.html
│   ├── messaging.html
│   └── reports.html
├── 📁 static/                   # CSS, JS, imagens
├── 📁 data/                     # Banco de dados SQLite
├── 📁 logs/                     # Arquivos de log
└── 📁 export/                   # Arquivos Excel exportados
```

## 🤝 Contribuição

Contribuições são bem-vindas! Para contribuir:

1. **Fork** o projeto
2. **Crie** uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. **Commit** suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. **Push** para a branch (`git push origin feature/AmazingFeature`)
5. **Abra** um Pull Request

### Diretrizes de Contribuição

- Siga o padrão de código existente
- Adicione testes para novas funcionalidades
- Atualize a documentação quando necessário
- Use commits descritivos

## 📊 Roadmap

- [ ] **v2.0**: Integração com Telegram
- [ ] **v2.1**: Dashboard com gráficos avançados
- [ ] **v2.2**: API REST completa
- [ ] **v2.3**: Integração com CRM
- [ ] **v2.4**: Machine Learning para otimização
- [ ] **v2.5**: App mobile

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🆘 Suporte

### Canais de Suporte

- 🐛 **Issues**: [GitHub Issues](https://github.com/seu-usuario/automacao-prospeccao/issues)
- 📖 **Documentação**: Este README
- 📋 **Logs**: Verifique `logs/app.log`

### FAQ

**P: Posso usar em outros estados além de Curitiba?**
R: Sim! Basta alterar a cidade no código do scraper.

**P: É seguro usar com WhatsApp?**
R: Sim, desde que respeite os limites de rate limiting configurados.

**P: Funciona em Windows?**
R: Sim, mas recomendamos Linux para produção.

## ⚖️ Aviso Legal

⚠️ **IMPORTANTE**: Este software é fornecido apenas para fins educacionais e de automação legítima de negócios.

### Responsabilidades do Usuário

- ✅ Respeitar os termos de uso do Google Maps e WhatsApp
- ✅ Cumprir as leis de proteção de dados (LGPD/GDPR)
- ✅ Usar de forma ética e responsável
- ✅ Obter consentimento adequado antes de enviar mensagens
- ✅ Não fazer spam ou uso abusivo

### Limitações

- 🚫 Não nos responsabilizamos por bloqueios de conta
- 🚫 Não garantimos 100% de sucesso nas operações
- 🚫 Use por sua própria conta e risco

---

<div align="center">

**Desenvolvido com ❤️ para automatizar prospecção de negócios**

[⭐ Star no GitHub](https://github.com/seu-usuario/automacao-prospeccao) | [🐛 Reportar Bug](https://github.com/seu-usuario/automacao-prospeccao/issues) | [💡 Sugerir Feature](https://github.com/seu-usuario/automacao-prospeccao/issues)

</div>
