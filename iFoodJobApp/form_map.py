from pymongo import MongoClient
from playwright.sync_api import sync_playwright
from time import sleep
from collections import defaultdict
from dados import MONGO_URI, DATABASE, COLLECTION

def conectar_mongo():
    client = MongoClient(MONGO_URI)
    db = client[DATABASE]
    return db[COLLECTION]

def extrair_labels_e_nomes(page):
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
    collection = conectar_mongo()
    vagas = list(collection.find({}))

    agrupado_por_valor = defaultdict(set)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        for vaga in vagas:
            url = vaga.get("url")
            if not url:
                print("⚠️ Documento sem URL, ignorado.")
                continue

            print(f"\n🔗 Acessando: {url}")

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

    if agrupado_por_valor:
        print("\n📝 Salvando agrupamento em labels_agrupados.py...")
        with open("labels_agrupados.py", "w", encoding="utf-8") as f:
            f.write("labels_agrupados = {\n")
            for label, chaves in agrupado_por_valor.items():
                label_limpo = label.replace("*", "").strip()
                f.write(f'    "{label_limpo}": {list(chaves)},\n')
            f.write("}\n")
        print("✅ Agrupamento salvo com sucesso.")
    else:
        print("✅ Nenhum campo encontrado.")

if __name__ == "__main__":
    mapear_todas_as_vagas()