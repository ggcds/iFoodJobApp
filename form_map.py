from pymongo import MongoClient
from playwright.sync_api import sync_playwright
from time import sleep
from collections import defaultdict
from dados import MONGO_URI, DATABASE, COLLECTION


def conectar_mongo():
    """
    Conecta ao MongoDB e retorna a coleção de vagas.
    """
    client = MongoClient(MONGO_URI)
    db = client[DATABASE]
    return db[COLLECTION]


def extrair_labels_e_nomes(page):
    """
    Extrai do formulário aberto todos os labels e seus 'for', retornando um dict {nome_campo: label_text}.
    """
    objeto = {}
    labels = page.query_selector_all("form label[for]")
    for label in labels:
        for_attr = label.get_attribute("for")
        texto = label.inner_text().strip()
        if for_attr and texto:
            texto_limpo = texto.replace("*", "").strip()
            objeto[for_attr] = texto_limpo
    return objeto


def mapear_todas_as_vagas():
    """
    Mapeia os campos de formulário apenas para vagas não processadas ou com erro,
    e agrupa os labels em um arquivo labels_agrupados.py.
    """
    collection = conectar_mongo()

    # Filtra apenas vagas novas (sem data_envio) ou com status 'erro'
    query = {
        "$or": [
            {"data_envio": {"$exists": False}},  # vagas nunca processadas
            {"status": "erro"}                   # vagas com tentativa anterior com erro
        ]
    }
    vagas = list(collection.find(query))
    print(f"📊 Vagas a mapear (novas/erro): {len(vagas)}\n")

    agrupado_por_valor = defaultdict(set)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        for vaga in vagas:
            url = vaga.get("url")
            if not url:
                print("⚠️ Documento sem URL, ignorado.")
                continue

            print(f"\n🔗 Acessando para mapear: {url}")
            try:
                page.goto(url)
                page.wait_for_load_state("networkidle")
                page.locator("button:has-text('Aplicar-se à Vaga')").click()
                page.wait_for_selector("form", timeout=10000)

                campos = extrair_labels_e_nomes(page)
                print(f"📋 Campos encontrados:\n{campos}")
                for chave, valor in campos.items():
                    agrupado_por_valor[valor].add(chave)

            except Exception as e:
                print(f"❌ Erro ao processar vaga {url}: {e}")

            sleep(2)

        browser.close()

    # Salva agrupamento em labels_agrupados.py (sobrescrevendo existente)
    if agrupado_por_valor:
        print("\n📝 Salvando agrupamento em labels_agrupados.py...")
        from pathlib import Path
        base = Path(__file__).parent
        destino = base / "labels_agrupados.py"
        with open(destino, "w", encoding="utf-8") as f:
            f.write("labels_agrupados = {\n")
            for label, chaves in agrupado_por_valor.items():
                label_limpo = label.replace("*", "").strip()
                f.write(f'    "{label_limpo}": {list(chaves)},\n')
            f.write("}\n")
        print("✅ Agrupamento salvo com sucesso.")
    else:
        print("✅ Nenhum campo encontrado.")