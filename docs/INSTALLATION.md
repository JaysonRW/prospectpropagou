# 📋 Guia de Instalação Detalhado

Este guia fornece instruções passo-a-passo para instalar e configurar a Automação de Prospecção em diferentes ambientes.

## 🖥️ Requisitos do Sistema

### Requisitos Mínimos
- **Sistema Operacional**: Linux (Ubuntu 18.04+), macOS (10.14+), Windows 10+
- **Python**: 3.8 ou superior
- **RAM**: 2GB mínimo, 4GB recomendado
- **Armazenamento**: 1GB de espaço livre
- **Internet**: Conexão estável

### Requisitos Recomendados para Produção
- **Sistema Operacional**: Ubuntu 20.04+ LTS
- **Python**: 3.11+
- **RAM**: 8GB ou mais
- **CPU**: 2+ cores
- **Armazenamento**: SSD com 10GB+ livres
- **Internet**: Conexão dedicada

## 🐧 Instalação no Linux (Ubuntu/Debian)

### 1. Atualizar Sistema
```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Instalar Python e Dependências
```bash
# Instalar Python 3.11
sudo apt install python3.11 python3.11-venv python3.11-dev -y

# Instalar pip
sudo apt install python3-pip -y

# Instalar Git
sudo apt install git -y
```

### 3. Instalar Google Chrome
```bash
# Baixar e instalar Chrome
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt update
sudo apt install google-chrome-stable -y

# Ou instalar Chromium (alternativa)
sudo apt install chromium-browser -y
```

### 4. Clonar e Configurar Projeto
```bash
# Clonar repositório
git clone https://github.com/seu-usuario/automacao-prospeccao.git
cd automacao-prospeccao

# Executar script de instalação
chmod +x start.sh
./start.sh
```

## 🍎 Instalação no macOS

### 1. Instalar Homebrew (se não tiver)
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 2. Instalar Python e Dependências
```bash
# Instalar Python 3.11
brew install python@3.11

# Instalar Git
brew install git

# Instalar Google Chrome
brew install --cask google-chrome
```

### 3. Configurar Projeto
```bash
# Clonar repositório
git clone https://github.com/seu-usuario/automacao-prospeccao.git
cd automacao-prospeccao

# Executar script de instalação
chmod +x start.sh
./start.sh
```

## 🪟 Instalação no Windows

### 1. Instalar Python
1. Baixe Python 3.11+ de [python.org](https://python.org)
2. Execute o instalador
3. ✅ Marque "Add Python to PATH"
4. ✅ Marque "Install pip"

### 2. Instalar Git
1. Baixe Git de [git-scm.com](https://git-scm.com)
2. Execute o instalador com configurações padrão

### 3. Instalar Google Chrome
1. Baixe Chrome de [google.com/chrome](https://google.com/chrome)
2. Execute o instalador

### 4. Configurar Projeto
```cmd
# Abrir PowerShell como Administrador

# Clonar repositório
git clone https://github.com/seu-usuario/automacao-prospeccao.git
cd automacao-prospeccao

# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt

# Configurar ambiente
copy .env.example .env
# Edite o arquivo .env no Notepad

# Criar diretórios
mkdir data logs export

# Executar aplicação
python app.py
```

## 🐳 Instalação com Docker

### 1. Instalar Docker
```bash
# Ubuntu
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# macOS
brew install --cask docker

# Windows: Baixar Docker Desktop
```

### 2. Criar Dockerfile
```dockerfile
FROM python:3.11-slim

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    && wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

# Criar diretórios
RUN mkdir -p data logs export

# Configurar usuário não-root
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expor porta
EXPOSE 5000

# Comando de inicialização
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "app:app"]
```

### 3. Build e Run
```bash
# Build da imagem
docker build -t automacao-prospeccao .

# Executar container
docker run -d \
  --name automacao-prospeccao \
  -p 5000:5000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/export:/app/export \
  automacao-prospeccao
```

## ☁️ Instalação em VPS/Servidor

### 1. Configurar Servidor (Ubuntu 20.04+)
```bash
# Conectar via SSH
ssh root@seu-servidor-ip

# Atualizar sistema
apt update && apt upgrade -y

# Instalar dependências básicas
apt install -y python3.11 python3.11-venv python3-pip git nginx supervisor

# Instalar Chrome
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list
apt update
apt install -y google-chrome-stable

# Criar usuário para aplicação
useradd -m -s /bin/bash prospeccao
su - prospeccao
```

### 2. Instalar Aplicação
```bash
# Como usuário prospeccao
cd /home/prospeccao

# Clonar projeto
git clone https://github.com/seu-usuario/automacao-prospeccao.git
cd automacao-prospeccao

# Configurar ambiente
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp .env.example .env
nano .env  # Editar configurações
```

### 3. Configurar como Serviço
```bash
# Como root
sudo cp /home/prospeccao/automacao-prospeccao/automacao-prospeccao.service /etc/systemd/system/

# Editar arquivo de serviço se necessário
sudo nano /etc/systemd/system/automacao-prospeccao.service

# Habilitar e iniciar serviço
sudo systemctl daemon-reload
sudo systemctl enable automacao-prospeccao
sudo systemctl start automacao-prospeccao

# Verificar status
sudo systemctl status automacao-prospeccao
```

### 4. Configurar Nginx (Opcional)
```bash
# Criar configuração do Nginx
sudo nano /etc/nginx/sites-available/automacao-prospeccao
```

```nginx
server {
    listen 80;
    server_name seu-dominio.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Habilitar site
sudo ln -s /etc/nginx/sites-available/automacao-prospeccao /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 🔧 Configuração Pós-Instalação

### 1. Configurar Variáveis de Ambiente
```bash
# Editar arquivo .env
nano .env
```

```env
# Configurações essenciais
FLASK_ENV=production
SECRET_KEY=sua_chave_super_secreta_aqui_com_32_caracteres
DATABASE_URL=sqlite:///data/prospeccao.db

# Configurações de segurança
SELENIUM_HEADLESS=true
MAX_MESSAGES_PER_HOUR=5
MAX_SCRAPING_RESULTS=50

# Configurações de logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
```

### 2. Testar Instalação
```bash
# Ativar ambiente virtual
source venv/bin/activate

# Testar aplicação
python app.py

# Em outro terminal, testar API
curl http://localhost:5000/api/status
```

### 3. Configurar Backup Automático
```bash
# Criar script de backup
nano backup.sh
```

```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/prospeccao/backups"
mkdir -p $BACKUP_DIR

# Backup do banco de dados
cp data/prospeccao.db $BACKUP_DIR/prospeccao_$DATE.db

# Backup dos logs (últimos 7 dias)
find logs/ -name "*.log" -mtime -7 -exec cp {} $BACKUP_DIR/ \;

# Limpar backups antigos (manter últimos 30 dias)
find $BACKUP_DIR -name "*.db" -mtime +30 -delete

echo "Backup concluído: $DATE"
```

```bash
# Tornar executável
chmod +x backup.sh

# Adicionar ao crontab (backup diário às 2h)
crontab -e
# Adicionar linha:
# 0 2 * * * /home/prospeccao/automacao-prospeccao/backup.sh
```

## 🔍 Verificação da Instalação

### 1. Checklist de Verificação
- [ ] Python 3.8+ instalado
- [ ] Chrome/Chromium instalado
- [ ] Dependências Python instaladas
- [ ] Arquivo .env configurado
- [ ] Diretórios criados (data, logs, export)
- [ ] Aplicação inicia sem erros
- [ ] Interface web acessível
- [ ] API responde corretamente

### 2. Comandos de Teste
```bash
# Verificar versão do Python
python3 --version

# Verificar Chrome
google-chrome --version

# Testar aplicação
curl -I http://localhost:5000

# Verificar logs
tail -f logs/app.log
```

### 3. Solução de Problemas Comuns

#### Erro: "Chrome binary not found"
```bash
# Instalar Chrome
sudo apt install google-chrome-stable

# Ou definir caminho manualmente
export CHROME_BIN=/usr/bin/google-chrome
```

#### Erro: "Permission denied"
```bash
# Corrigir permissões
sudo chown -R $USER:$USER .
chmod +x start.sh
```

#### Erro: "Port already in use"
```bash
# Verificar processo usando porta 5000
sudo lsof -i :5000

# Matar processo se necessário
sudo kill -9 PID
```

## 📞 Suporte

Se encontrar problemas durante a instalação:

1. **Verifique os logs**: `tail -f logs/app.log`
2. **Consulte o troubleshooting**: [README.md](../README.md#troubleshooting)
3. **Abra uma issue**: [GitHub Issues](https://github.com/seu-usuario/automacao-prospeccao/issues)

---

**Instalação concluída com sucesso! 🎉**

Próximos passos: [Configuração para Servidor](SERVER.md) | [Guia de Uso](USAGE.md)
