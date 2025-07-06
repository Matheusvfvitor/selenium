📄 README.md
markdown
Copiar
Editar
# 🚀 Cloud Function Selenium (Python 3.9 + Headless Chrome)

Este repositório contém uma função HTTP para o **Google Cloud Functions Gen 2**, escrita em **Python 3.9**, que utiliza o **Selenium WebDriver** com **Chrome Headless** para realizar automações web em ambientes serverless, como scraping, testes ou captura de dados.

---

## 📦 Estrutura

cloud-function-selenium/
├── main.py # Código principal da função

├── requirements.txt # Dependências Python (Selenium)

├── chrome_setup.sh # Script opcional para baixar os binários

└── files/

├── chromedriver # Driver do Chrome (copiado para /tmp)

└── headless-chromium # Binário do Chrome Headless (copiado para /tmp)

yaml
Copiar
Editar

---

## ⚙️ Pré-requisitos

- Conta na [Google Cloud Platform](https://console.cloud.google.com/)
- Projeto ativo e com billing
- Python 3.9 habilitado no ambiente
- Google Cloud CLI configurado (`gcloud auth login`)

---

## 🚀 Deploy

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/cloud-function-selenium.git
cd cloud-function-selenium
2. Baixe os binários
bash
Copiar
Editar
bash chrome_setup.sh
Isso criará os arquivos chromedriver e headless-chromium dentro da pasta files/.

3. Deploy para Cloud Functions Gen 2
bash
Copiar
Editar
gcloud functions deploy selenium-handler \
  --gen2 \
  --runtime=python39 \
  --region=southamerica-east1 \
  --source=. \
  --entry-point=selenium_handler \
  --trigger-http \
  --memory=1Gi \
  --timeout=540s \
  --allow-unauthenticated
🔍 O que a função faz?
Acessa https://www.google.com, aguarda 2 segundos e retorna o título da página utilizando Selenium com Chrome em modo headless. Ideal como base para outras automações.

📜 Licença
MIT

✨ Créditos
Este projeto foi inspirado em soluções serverless com Selenium, adaptado para rodar em Cloud Functions com Python e ambiente temporário /tmp.

