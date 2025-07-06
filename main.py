from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import requests
import time

def realizar_login(email, senha, unidade):
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    wait = WebDriverWait(driver, 20)

    resultado = {
        "status": "erro",
        "mensagem": "",
        "cookies": {},
        "unidade": unidade
    }

    try:
        driver.get("http://mtr.ima.sc.gov.br/")
        wait.until(EC.element_to_be_clickable((By.ID, "rdCnpj"))).click()
        time.sleep(1)

        wait.until(EC.presence_of_element_located((By.ID, "txtCnpj"))).send_keys(email)
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
    url_base = "http://mtr.ima.sc.gov.br/br/com/brdti/mtr/controller/JqueryDatatablePluginDemo.java"

    params = {
        "tabela": "MTR",
        "perfil": "1",
        "MTRsAbertos": "",
        "MTRsComCdf": "",
        "dataInicial": data_inicial,
        "dataFinal": data_final,
        "numMtr": "",
        "sEcho": "1",
        "iColumns": "6",
        "sColumns": ",,,,,",
        "iDisplayStart": "0",
        "iDisplayLength": "10",
        "mDataProp_0": "0",
        "sSearch_0": "",
        "bRegex_0": "false",
        "bSearchable_0": "true",
        "mDataProp_1": "1",
        "sSearch_1": "",
        "bRegex_1": "false",
        "bSearchable_1": "true",
        "mDataProp_2": "2",
        "sSearch_2": "",
        "bRegex_2": "false",
        "bSearchable_2": "true",
        "mDataProp_3": "3",
        "sSearch_3": "",
        "bRegex_3": "false",
        "bSearchable_3": "true",
        "mDataProp_4": "4",
        "sSearch_4": "",
        "bRegex_4": "false",
        "bSearchable_4": "true",
        "mDataProp_5": "5",
        "sSearch_5": "",
        "bRegex_5": "false",
        "bSearchable_5": "true",
        "sSearch": "",
        "bRegex": "false",
        "_": str(int(time.time() * 1000))
    }

    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        "Connection": "keep-alive",
        "Host": "mtr.ima.sc.gov.br",
        "Referer": "http://mtr.ima.sc.gov.br/ControllerServlet?acao=acompanhamentoManifesto",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest"
    }

    response = requests.get(url_base, headers=headers, params=params, cookies=cookies_dict)

    if response.status_code == 200:
        return {
            "status": "sucesso",
            "dados": response.json()
        }
    else:
        return {
            "status": "erro",
            "codigo_http": response.status_code,
            "mensagem": response.text
        }
    
def busca_pessoa_por_tipo(cnpj, cookies_dict):
    url = "http://mtr.ima.sc.gov.br/ControllerServlet"

    payload = {
        "acao": "buscaPessoaPorTipo",
        "cnpj": cnpj,
        "tipoPessoa": "2"
    }

    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Host": "mtr.ima.sc.gov.br",
        "Origin": "http://mtr.ima.sc.gov.br",
        "Referer": "http://mtr.ima.sc.gov.br/ControllerServlet?acao=cadastroManifesto",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest"
    }

    response = requests.post(url, headers=headers, data=payload, cookies=cookies_dict)

    if response.status_code == 200:
        return {
            "status": "sucesso",
            "html": response.text
        }
    else:
        return {
            "status": "erro",
            "codigo_http": response.status_code,
            "mensagem": response.text
        }

def consultar_manifesto_por_codigo_barras(codigo_barras, cnpj, senha):
    url = f"http://mtr.ima.sc.gov.br/mtrservice/retornaManifesto/{codigo_barras}/{cnpj}/{senha}/{cnpj}"

    print(url)

    headers = {
        "Content-Type": "application/json",
        "Accept": "*/*"
    }


    response = requests.post(url, headers=headers)

    if response.status_code == 200:
        return {
            "status": "sucesso",
            "manifesto": response.json()
        }
    else:
        return {
            "status": "erro",
            "codigo_http": response.status_code,
            "mensagem": response.text
        }
    
def transformar_manifesto(resposta_manifesto):
    from datetime import datetime

    def data_para_millis(data_str):
        try:
            dt = datetime.strptime(data_str.split(" ")[0], "%Y-%m-%d")
            return int(dt.timestamp() * 1000)
        except:
            return None

    manifesto = resposta_manifesto.get("manifesto", {})

    item = manifesto.get("itemManifestoJSONs", [{}])[0]

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

import json

if __name__ == "__main__":
    login = realizar_login("39228967000160", "T2m@2024", "Unidade ABC")

    if login["status"] == "sucesso":
        cookies = login["cookies"]

        # 1. Consulta os MTRs
        resposta_mtr = consultar_mtrs("01/06/2025", "30/07/2025", cookies)
        print("Resposta MTR:", resposta_mtr)

        # 2. Consulta unidade pelo CNPJ do transportador (ou gerador, etc.)
        if resposta_mtr["status"] == "sucesso" and resposta_mtr["dados"]["iTotalRecords"] > 0:
            cnpj = "03498301000185"  # Pode vir do MTR também se necessário
            resultado_unidade = busca_pessoa_por_tipo(cnpj, cookies)
            print("Resposta Unidade:")
            print(resultado_unidade)

            # 3. Construir código de barras
            try:
                mtr = resposta_mtr['dados']['aaData'][0][0]

                unidade_json = json.loads(resultado_unidade["html"])
                pessoaCodigo = unidade_json["pessoaCodigo"]

                # Para este exemplo, vamos assumir que o mesmo código serve para os 3 papéis
                unidadeGerador = 107166
                unidadeColetor = pessoaCodigo
                unidadeDestino = pessoaCodigo

                mtrFormatado = str(mtr).zfill(10)
                geradorFormatado = str(unidadeGerador).zfill(8)
                transportadorFormatado = str(unidadeColetor).zfill(8)
                destinatarioFormatado = str(unidadeDestino).zfill(8)

                codigoDeBarras = f"{mtrFormatado}{geradorFormatado}{transportadorFormatado}{destinatarioFormatado}"

                print("Código de Barras:", codigoDeBarras)
                
                cnpj = "39228967000160"
                senha = "T2m@2024"
                resposta_manifesto = consultar_manifesto_por_codigo_barras(codigoDeBarras, cnpj, senha)
                print("Resposta do Manifesto por Código de Barras:")
                print(resposta_manifesto)

                if resposta_manifesto["status"] == "sucesso":
                    manifesto_formatado = transformar_manifesto(resposta_manifesto)
                    print(manifesto_formatado)

            except Exception as e:
                print("Erro ao gerar código de barras:", str(e))

        else:
            print("Nenhum MTR encontrado.")

    else:
        print("Falha no login:", login["mensagem"])
