#!/bin/bash

# Script de inicialização para Automação de Prospecção
# Uso: ./start.sh [development|production]

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Iniciando Automação de Prospecção - Curitiba${NC}"

# Verificar se o ambiente foi especificado
ENV=${1:-development}
echo -e "${YELLOW}📋 Ambiente: $ENV${NC}"

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 não encontrado. Por favor, instale Python 3.8+${NC}"
    exit 1
fi

# Verificar se o ambiente virtual existe
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}📦 Criando ambiente virtual...${NC}"
    python3 -m venv venv
fi

# Ativar ambiente virtual
echo -e "${YELLOW}🔧 Ativando ambiente virtual...${NC}"
source venv/bin/activate

# Instalar dependências
echo -e "${YELLOW}📚 Instalando dependências...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

# Verificar se arquivo .env existe
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚙️  Arquivo .env não encontrado. Copiando .env.example...${NC}"
    cp .env.example .env
    echo -e "${YELLOW}📝 Por favor, edite o arquivo .env com suas configurações${NC}"
fi

# Criar diretórios necessários
mkdir -p data logs export

# Configurar variável de ambiente
export FLASK_ENV=$ENV

# Verificar se Chrome/Chromium está instalado (necessário para Selenium)
if ! command -v google-chrome &> /dev/null && ! command -v chromium-browser &> /dev/null; then
    echo -e "${YELLOW}⚠️  Chrome/Chromium não encontrado. Instalando...${NC}"
    
    # Detectar sistema operacional
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Ubuntu/Debian
        if command -v apt-get &> /dev/null; then
            sudo apt-get update
            sudo apt-get install -y chromium-browser
        # CentOS/RHEL
        elif command -v yum &> /dev/null; then
            sudo yum install -y chromium
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            brew install --cask google-chrome
        fi
    fi
fi

echo -e "${GREEN}✅ Configuração concluída!${NC}"
echo -e "${GREEN}🌐 Iniciando servidor...${NC}"

# Iniciar aplicação
if [ "$ENV" = "production" ]; then
    echo -e "${YELLOW}🏭 Modo produção - usando Gunicorn${NC}"
    
    # Instalar Gunicorn se não estiver instalado
    pip install gunicorn
    
    # Iniciar com Gunicorn
    gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 app:app
else
    echo -e "${YELLOW}🔧 Modo desenvolvimento - usando Flask dev server${NC}"
    python app.py
fi
