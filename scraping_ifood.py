from pymongo import MongoClient
from playwright.sync_api import sync_playwright, TimeoutError
from dados import MONGO_URI, DATABASE, COLLECTION

BASE_URL = "https://carreiras.ifood.com.br/jobs/"

def conectar_mongo():
    client = MongoClient(MONGO_URI)
    db = client[DATABASE]
    return db[COLLECTION]

def salvar_links_mongo(collection, documentos):
    novas = 0
    for doc in documentos:
        if not collection.find_one({"url": doc["url"]}):
            collection.insert_one(doc)
            novas += 1
    print(f"✅ {novas} novas vagas salvas.")

def extrair_links_ifood():
    collection = conectar_mongo()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=200)
        page = browser.new_page()
        page.goto(BASE_URL, timeout=60000)
        page.wait_for_timeout(2000)

        # 🎯 Filtro: Senioridade → Júnior + Pleno
        page.click("input[placeholder='Senioridade']")
        page.wait_for_timeout(500)
        page.click("label:has-text('Júnior')")
        page.click("label:has-text('Pleno')")
        page.wait_for_timeout(500)

        # 🎯 Filtro: Localidade → todos os que contêm "remoto"
        page.click("input[placeholder='Localidade']")
        page.wait_for_timeout(500)

        labels = page.locator("label")
        try:
            count = labels.count()
            print(f"🔍 Total de labels encontrados: {count}")

            for i in range(count):
                try:
                    texto = labels.nth(i).inner_text().strip().lower()
                    if "remoto" in texto:
                        print(f"📌 Clicando em: {texto}")
                        labels.nth(i).click(force=True, timeout=3000)
                        page.wait_for_timeout(500)
                except Exception as e:
                    print(f"⚠️ Erro ao clicar no label #{i}: {e}")
        except TimeoutError as e:
            print("⛔ Timeout ao buscar labels de localidade:", e)

        # 🔍 Captura das vagas
        documentos = []
        try:
            page.wait_for_selector("a[title][href^='/job/']", timeout=15000)
            vagas = page.locator("a[title][href^='/job/']")
            count = vagas.count()
            print(f"🔗 {count} vagas encontradas.")

            for i in range(count):
                try:
                    href = vagas.nth(i).get_attribute("href")
                    titulo = vagas.nth(i).get_attribute("title") or "Vaga sem título"

                    if href:
                        documentos.append({
                            "url": "https://carreiras.ifood.com.br" + href,
                            "titulo": titulo.strip()
                        })
                except Exception as e:
                    print(f"⚠️ Erro ao extrair vaga #{i}: {e}")
        except TimeoutError:
            print("⚠️ Nenhuma vaga encontrada ou a lista não carregou.")

        salvar_links_mongo(collection, documentos)

if __name__ == "__main__":
    extrair_links_ifood()
    print("📥 Scraping finalizado com sucesso!")
