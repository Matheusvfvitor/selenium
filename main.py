import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, timedelta
import json
import requests
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def realizar_login(cnpj, senha, unidade):
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    wait = WebDriverWait(driver, 20)

    resultado = {"status": "erro", "mensagem": "", "cookies": {}, "unidade": unidade}

    try:
        driver.get("http://mtr.ima.sc.gov.br/")
        wait.until(EC.element_to_be_clickable((By.ID, "rdCnpj"))).click()
        time.sleep(1)
        wait.until(EC.presence_of_element_located((By.ID, "txtCnpj"))).send_keys(cnpj)
        driver.find_element(By.ID, "txtSenha").send_keys(senha)
        driver.find_element(By.ID, "btEntrar").click()
        wait.until(lambda d: "ControllerServlet" in d.current_url or "logout" in d.page_source.lower())
        cookies = {c['name']: c['value'] for c in driver.get_cookies()}
        resultado["status"] = "sucesso"
        resultado["cookies"] = cookies
    except Exception as e:
        resultado["mensagem"] = str(e)
    finally:
        driver.quit()
    return resultado

def consultar_mtrs(data_inicial, data_final, cookies_dict):
    url = "http://mtr.ima.sc.gov.br/br/com/brdti/mtr/controller/JqueryDatatablePluginDemo.java"
    params = {
        "tabela": "MTR", "perfil": "1", "dataInicial": data_inicial, "dataFinal": data_final,
        "sEcho": "1", "iColumns": "6", "sColumns": ",,,,    ,", "iDisplayStart": "0",
        "iDisplayLength": "100", "sSearch": "", "bRegex": "false", "_": str(int(time.time() * 1000))
    }
    headers = {
        "Accept": "application/json", "User-Agent": "Mozilla/5.0",
        "Referer": "http://mtr.ima.sc.gov.br/ControllerServlet?acao=acompanhamentoManifesto"
    }
    response = requests.get(url, headers=headers, params=params, cookies=cookies_dict)
    if response.status_code == 200:
        return {"status": "sucesso", "dados": response.json()}
    else:
        return {"status": "erro", "codigo_http": response.status_code, "mensagem": response.text}

def busca_pessoa_por_tipo(cnpj, tipoPessoa, cookies_dict):
    url = "http://mtr.ima.sc.gov.br/ControllerServlet"
    payload = {"acao": "buscaPessoaPorTipo", "cnpj": cnpj, "tipoPessoa": tipoPessoa}
    headers = {"Content-Type": "application/x-www-form-urlencoded", "User-Agent": "Mozilla/5.0"}
    response = requests.post(url, headers=headers, data=payload, cookies=cookies_dict)
    if response.status_code == 200:
        return {"status": "sucesso", "html": response.text}
    return {"status": "erro", "codigo_http": response.status_code, "mensagem": response.text}

def consultar_manifesto_por_codigo_barras(codigo_barras, cnpj, senha):
    print(f"{codigo_barras}/{cnpj}/{senha}/{cnpj}")
    url = f"http://mtr.ima.sc.gov.br/mtrservice/retornaManifesto/{codigo_barras}/{cnpj}/{senha}/{cnpj}"
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, headers=headers)
    if response.status_code == 200:
        return {"status": "sucesso", "manifesto": response.json()}
    return {"status": "erro", "codigo_http": response.status_code, "mensagem": response.text}

def     transformar_manifesto(resposta_manifesto):
    from datetime import datetime

    def data_para_millis(data_str):
        try:
            dt = datetime.strptime(data_str.split(" ")[0], "%Y-%m-%d")
            return int(dt.timestamp() * 1000)
        except:
            return None
    
    print(resposta_manifesto)

    manifesto = resposta_manifesto.get("manifesto", {})

    print(manifesto)

    itens = manifesto.get("itemManifestoJSONs", [])
    if not itens:
        raise Exception("Manifesto não possui resíduos (itemManifestoJSONs está vazio)")
    item = itens[0]

    return {
        "cdfCodigo": manifesto.get("cdfCodigo", None),
        "estado": {
            "estAbreviacao": manifesto.get("ufGerador", "SP"),
            "estCodigo": 26 if manifesto.get("ufGerador", "SP") == "SP" else None
        },
        "listaManifestoResiduo": [
            {
                "classe": {
                    "claCodigo": 43,
                    "claDescricao": "CLASSE II A"
                },
                "codigoInterno": item.get("codigoInterno"),
                "descricaoInterna": None,
                "grupoEmbalagem": item.get("grupoEmbalagem") if item.get("grupoEmbalagem") != "0" else None,
                "marClasseRisco": None,
                "marDensidade": None,
                "marJustificativa": item.get("justificativa"),
                "marNomeEmbarque": item.get("nomeEmbarque"),
                "marNumeroONU": item.get("codigoONU"),
                "marObservacao": item.get("manifestoItemObservacao"),
                "marQuantidade": item.get("quantidade"),
                "marQuantidadeRecebida": item.get("quantidadeRecebida"),
                "residuo": {
                    "resCodigo": 422,
                    "resCodigoIbama": item.get("residuo"),
                    "resDescricao": item.get("descricao")
                },
                "tipoAcondicionamento": {
                    "tiaCodigo": item.get("codigoAcondicionamento"),
                    "tiaCodigoReferencia": item.get("codigoAcondicionamento"),
                    "tiaDescricao": "Big Bag"  # Se quiser um de/para, podemos implementar
                },
                "tipoEstado": {
                    "tieCodigo": 4,
                    "tieCodigoReferencia": item.get("codigoTipoEstado"),
                    "tieDescricao": "SÓLIDO"
                },
                "tratamento": {
                    "traCodigo": 43,
                    "traDescricao": "Reciclagem"
                },
                "unidade": {
                    "uniCodigo": 3,
                    "uniDescricao": "Tonelada",
                    "uniSigla": "TON"
                },
                "manData": data_para_millis(manifesto.get("manifData")),
                "manDataExpedicao": data_para_millis(manifesto.get("manifDataExpedicao")),
                "manDataRecebimentoArmazenamentoTemporario": None,
                "manDataRecebimentoDestinador": None,
                "manJustificativaCancelamento": "",
                "manNomeMotorista": manifesto.get("manifTransportadorNomeMotorista", ""),
                "manNumero": str(manifesto.get("manifestoCodigo")),
                "manNumeroEstadual": None,
                "manObservacao": manifesto.get("manifObservacao"),
                "manPlacaVeiculo": manifesto.get("manifTransportadorPlacaVeiculo", ""),
                "manResponsavel": manifesto.get("manifGeradorNomeResponsavel"),
                "manResponsavelRecebimento": manifesto.get("responsavelRecebimento"),
                "parceiroArmazenadorTemporario": {
                    "parCnpj": manifesto.get("cnpArmazenador"),
                    "parCodigo": manifesto.get("codigoArmazenador"),
                    "parDescricao": manifesto.get("razaoSocialArmazenador") or ""
                },
                "parceiroDestinador": {
                    "parCnpj": manifesto.get("cnpDestinador"),
                    "parCodigo": manifesto.get("codigoDestinador"),
                    "parDescricao": manifesto.get("razaoSocialDestinador")
                },
                "parceiroGerador": {
                    "parCnpj": manifesto.get("cnpGerador"),
                    "parCodigo": manifesto.get("codigoGerador"),
                    "parDescricao": manifesto.get("razaoSocialGerador")
                },
                "parceiroTransportador": {
                    "parCnpj": manifesto.get("cnpTransportador"),
                    "parCodigo": manifesto.get("codigoTransportador"),
                    "parDescricao": manifesto.get("razaoSocialTransportador")
                },
                "seuCodigo": None,
                "situacaoManifesto": {
                    "simCodigo": manifesto.get("situacaoManifestoCodigo"),
                    "simDescricao": "Em processamento",  # Pode fazer de/para se tiver os códigos
                    "simOrdem": manifesto.get("situacaoManifestoCodigo")
                }
            }
        ]
    }


# Firebase Setup
cred = credentials.Certificate("./test-and-show-firebase-adminsdk-ioqrb-7c45f15862.json")
# firebase_admin.initialize_app(cred)
db = firestore.client()

hoje = datetime.today()
inicio = (hoje - timedelta(days=90)).strftime("%d/%m/%Y")
fim = hoje.strftime("%d/%m/%Y")

empresas_ref = db.collection("destinadores").where("sistemaMTR", "==", "IMA")
empresas = empresas_ref.stream()

for empresa_doc in empresas:
    empresa_data = empresa_doc.to_dict()
    empresa_id = empresa_doc.id
    chave = empresa_data.get("chave", {})
    cnpj = chave.get("cpfcnpj")
    senha = chave.get("senha")
    unidade = chave.get("unidade", "Unidade Padrão")

    if not cnpj or not senha:
        print(f"[!] Dados incompletos para empresa {empresa_id}. Pulando...")
        continue

    print(f"\n➡️  Empresa: {empresa_id} ({cnpj})")
    login = realizar_login(cnpj, senha, unidade)
    if login["status"] != "sucesso":
        print(f"Erro ao logar: {login['mensagem']}")
        continue

    cookies = login["cookies"]
    print(cookies)
    resposta_mtr = consultar_mtrs(inicio, fim, cookies)
    if resposta_mtr["status"] != "sucesso":
        print("Erro ao consultar MTRs.")
        continue

    for row in resposta_mtr["dados"].get("aaData", []):
        try:
            print(row)
            numero_mtr = str(row[0])
            doc_ref = db.collection("destinadores").document(empresa_id).collection("envios").document(numero_mtr)
            doc_snapshot = doc_ref.get()

            cnpj_transportador = row[2].split(" - ")[0].strip()
            print(cnpj_transportador)
            cnpj_destinador = row[3].split(" - ")[0].strip()
            print(cnpj_destinador)


            res_transp = busca_pessoa_por_tipo(cnpj_transportador, 2, cookies)
            res_dest = busca_pessoa_por_tipo(cnpj_destinador, 4, cookies)

            cod_transportador = json.loads(res_transp["html"]).get("pessoaCodigo")
            print(json.loads(res_dest["html"]))
            cod_destinador = json.loads(res_dest["html"]).get("pessoaCodigo")


            print(cod_destinador)
            print(cod_transportador) 

            mtrFormatado = str(numero_mtr).zfill(10)
            pessoaFormatado = str(unidade).zfill(8)
            transportador_formatado = str(cod_transportador).zfill(8)
            destinador_formatado = str(cod_destinador).zfill(8)
            codigoBarras = f"{mtrFormatado}{pessoaFormatado}{transportador_formatado}{destinador_formatado}"

            resposta_manifesto = consultar_manifesto_por_codigo_barras(codigoBarras, cnpj, senha)
            if resposta_manifesto["status"] != "sucesso":
                print(f"Erro ao buscar manifesto {numero_mtr}")
                continue

            manifesto = transformar_manifesto(resposta_manifesto)

            if not doc_snapshot.exists:
                doc_ref.set(manifesto)
                print(f"✅ MTR {numero_mtr} salvo.")
            else:
                status_antigo = doc_snapshot.to_dict().get("listaManifestoResiduo", [{}])[0].get("situacaoManifesto", {}).get("simCodigo")
                status_novo = manifesto["listaManifestoResiduo"][0]["situacaoManifesto"]["simCodigo"]

                if status_antigo != status_novo:
                    doc_ref.set(manifesto, merge=True)
                    print(f"🔁 MTR {numero_mtr} atualizado.")
                else:
                    print(f"➖ MTR {numero_mtr} já atualizado.")

        except Exception as e:
            print(f"❌ Erro ao processar MTR {row[0]}: {str(e)}")
