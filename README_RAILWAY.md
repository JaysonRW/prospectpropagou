# 🚀 Deploy no Railway

Este projeto está configurado para rodar na plataforma Railway.

## 📋 Pré-requisitos

- Conta no [Railway](https://railway.app)
- Repositório GitHub conectado
- Projeto criado no Railway

## 🔧 Configuração

### 1. Variáveis de Ambiente

Configure as seguintes variáveis no Railway:

```bash
# Obrigatórias
SECRET_KEY=sua_chave_secreta_aqui
FLASK_ENV=production
FLASK_DEBUG=false

# Opcionais (valores padrão configurados)
SELENIUM_ENABLED=false
MAX_MESSAGES_PER_HOUR=5
MAX_SCRAPING_RESULTS=50
LOG_LEVEL=INFO
```

### 2. Banco de Dados

O Railway criará automaticamente um banco PostgreSQL. A variável `DATABASE_URL` será fornecida automaticamente.

## 🚀 Deploy

1. **Conecte o repositório** no Railway
2. **Configure as variáveis** de ambiente
3. **Deploy automático** acontecerá a cada push na main

## ⚠️ Limitações no Railway

### Funcionalidades Desabilitadas:
- **Selenium/Web Scraping** - Não suportado em ambiente serverless
- **WhatsApp Automation** - Requer navegador real
- **Arquivos locais** - Use `/tmp` para arquivos temporários

### Alternativas Recomendadas:
- **Scraping**: APIs externas (Google Places, Yelp)
- **WhatsApp**: Twilio, MessageBird
- **Arquivos**: Cloud storage (AWS S3, Google Cloud)

## 🔍 Monitoramento

- **Logs**: Acesse via dashboard do Railway
- **Health Check**: `/` endpoint para verificar status
- **Métricas**: CPU, memória e rede no dashboard

## 🛠️ Desenvolvimento Local

Para testar localmente com configurações do Railway:

```bash
# Copie as variáveis de ambiente
cp railway.env.example .env

# Instale dependências
pip install -r requirements.txt

# Execute
python app.py
```

## 📞 Suporte

- **Railway Docs**: https://docs.railway.app
- **Issues**: Abra no repositório GitHub
- **Discord**: Comunidade Railway 